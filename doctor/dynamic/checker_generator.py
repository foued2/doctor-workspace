#!/usr/bin/env python3
"""
Direction 2: Checker Generator

Builds and validates provisional LLM-generated checkers from extracted schemas.
"""
import copy
import json
import os
import re
from typing import Any, Callable, Optional


GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "deepseek/deepseek-chat-v3-0324")
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "openrouter")


class _TokenCursor:
    """Token cursor that preserves line boundaries for mixed scalar/list inputs."""

    def __init__(self, text: str):
        self.lines = [re.split(r"\s+", line.strip()) for line in text.splitlines() if line.strip()]
        self.line_index = 0
        self.token_index = 0

    def consume_token(self) -> Optional[str]:
        while self.line_index < len(self.lines):
            tokens = self.lines[self.line_index]
            if self.token_index < len(tokens):
                token = tokens[self.token_index]
                self.token_index += 1
                return token
            self.line_index += 1
            self.token_index = 0
        return None

    def consume_tokens(self, count: int) -> Optional[list[str]]:
        values = []
        for _ in range(count):
            token = self.consume_token()
            if token is None:
                return None
            values.append(token)
        return values

    def consume_line_tokens(self) -> Optional[list[str]]:
        while self.line_index < len(self.lines):
            tokens = self.lines[self.line_index]
            if self.token_index < len(tokens):
                remaining = tokens[self.token_index:]
                self.line_index += 1
                self.token_index = 0
                return remaining
            self.line_index += 1
            self.token_index = 0
        return None

    def at_end(self) -> bool:
        while self.line_index < len(self.lines):
            if self.token_index < len(self.lines[self.line_index]):
                return False
            self.line_index += 1
            self.token_index = 0
        return True


def _build_checker_prompt(schema: dict) -> str:
    """Build the checker-generation prompt from the extracted schema."""
    input_structure = schema.get("input_structure", {})
    output_format = schema.get("output_format", {})
    input_type = input_structure.get("type", "single_case")
    test_case_var = input_structure.get("test_case_count_var") or "t"
    per_case_fields = input_structure.get("per_case_format", [])
    fields_json = json.dumps(per_case_fields, indent=2, ensure_ascii=False)
    sample_cases_json = json.dumps(schema.get("sample_cases", []), indent=2, ensure_ascii=False)
    invariants_json = json.dumps(schema.get("invariants", []), indent=2, ensure_ascii=False)

    if input_type == "multi_case":
        input_contract = (
            f"input_args is a dict with keys:\n"
            f"- '{test_case_var}': integer number of test cases\n"
            f"- 'cases': list of per-case dicts, one dict per test case, using the fields below\n"
            f"output is a list aligned with input_args['cases']; one output element per case"
        )
    else:
        input_contract = (
            "input_args is a dict containing one test case using the fields below\n"
            "output is the single-case candidate output"
        )

    output_contract = (
        f"output_format.type is '{output_format.get('type', 'string')}'.\n"
        "Representation rules used by Doctor's internal tests:\n"
        "- integer: int\n"
        "- list: Python list\n"
        "- boolean: bool\n"
        "- string: raw trimmed string for that case. If the string contains space-separated integers, your checker must parse it itself."
    )

    return f"""You are generating a Python validator for an algorithmic problem.

Return ONLY Python source code for exactly one function with this exact signature:
def check(input_args: dict, output) -> tuple[bool, str]:

Hard requirements:
- Return (True, "ok") for valid output
- Return (False, "<reason>") for invalid output
- Use standard Python only
- Do not use external libraries
- Do not print anything
- Do not include markdown fences or commentary
- Do not implement a solver, search, brute-force enumerator, or constructive algorithm for the original problem
- If imports are unnecessary, do not import anything
- If you use a stdlib import, it must be inside the function body

Input contract:
{input_contract}

Per-case fields:
{fields_json}

Output contract:
{output_contract}

Problem metadata:
- has_multiple_valid_outputs: {schema.get("has_multiple_valid_outputs")}
- validation_type: {schema.get("validation_type")}
- output_format.description: {output_format.get("description", "")}

Output invariants that must be enforced:
{invariants_json}

Validation logic (verbatim):
{schema.get("validation_logic", "")}

Reference sample cases:
{sample_cases_json}
"""


def _call_llm(prompt: str) -> str:
    """Route to the configured LLM provider."""
    if LLM_PROVIDER == "groq" and GROQ_API_KEY:
        return _call_groq(prompt)
    elif OPENROUTER_API_KEY:
        return _call_openrouter(prompt)
    else:
        raise ValueError("No LLM provider configured. Set OPENROUTER_API_KEY or GROQ_API_KEY.")


def _call_groq(prompt: str) -> str:
    import requests
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0,
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def _call_openrouter(prompt: str) -> str:
    import requests
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": OPENROUTER_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0,
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def _extract_check_function(response: str) -> str | None:
    """Extract the check() function block from an LLM response."""
    if not response:
        return None

    blocks = re.findall(r"```(?:python)?\s*([\s\S]*?)```", response)
    candidates = blocks + [response]
    signature = re.compile(
        r"def\s+check\s*\(\s*input_args\s*:\s*dict\s*,\s*output\s*\)\s*->\s*tuple\s*\[\s*bool\s*,\s*str\s*\]\s*:"
    )

    for candidate in candidates:
        if not signature.search(candidate):
            continue

        lines = candidate.strip().splitlines()
        start = None
        for idx, line in enumerate(lines):
            if signature.search(line):
                start = idx
                break
        if start is None:
            continue

        function_lines = [lines[start]]
        for line in lines[start + 1:]:
            if not line.strip():
                function_lines.append(line)
                continue
            if line.startswith((" ", "\t", "#")):
                function_lines.append(line)
                continue
            break

        source = "\n".join(function_lines).strip()
        if source:
            return source + "\n"

    return None


def _compile_checker(source: str) -> Callable | None:
    """Compile checker source and return the check function if valid."""
    try:
        namespace: dict[str, Any] = {}
        compiled = compile(source, "<checker_generator>", "exec")
        exec(compiled, namespace, namespace)
        check_fn = namespace.get("check")
        if callable(check_fn):
            return check_fn
    except Exception:
        return None
    return None


def _parse_sample_case(schema: dict, raw_input: str, raw_output: str) -> tuple[dict, Any] | None:
    """Parse a raw sample case into the canonical checker input/output representation."""
    input_structure = schema.get("input_structure", {})
    per_case_format = input_structure.get("per_case_format", [])
    if not per_case_format:
        return None

    cursor = _TokenCursor(raw_input)
    if input_structure.get("type") == "multi_case":
        test_case_var = input_structure.get("test_case_count_var")
        if not test_case_var:
            return None
        test_count_token = cursor.consume_token()
        if test_count_token is None:
            return None
        try:
            test_count = int(test_count_token)
        except ValueError:
            return None

        cases = []
        for _ in range(test_count):
            case = _parse_case_from_cursor(cursor, per_case_format)
            if case is None:
                return None
            cases.append(case)

        if not cursor.at_end():
            return None

        outputs = _parse_multi_case_output(schema, raw_output, cases)
        if outputs is None:
            return None
        return {test_case_var: test_count, "cases": cases}, outputs

    case = _parse_case_from_cursor(cursor, per_case_format)
    if case is None or not cursor.at_end():
        return None
    output = _parse_single_case_output(schema.get("output_format", {}), raw_output, case)
    if output is None:
        return None
    return case, output


def _generate_invariant_violation(invariant: str, sample: dict) -> Any:
    """Generate one output that should violate the target invariant."""
    candidate = _generate_targeted_violation_from_rules(invariant, sample)
    if candidate is not None:
        return candidate
    return _llm_generate_targeted_violation("invariant", invariant, sample)


def _parse_validation_conditions(validation_logic: str) -> list[str] | None:
    """Decompose validation_logic into atomic, concrete conditions."""
    prompt = f"""Break the following validation logic into a JSON array of atomic, directly testable output conditions.

Rules:
- Each item must be a concrete predicate about the output or the output/input relationship
- Do not produce vague items like "output is correct" or "answer is valid"
- Each item must be specific enough that a separate system could create a targeted violating output for it
- If the logic cannot be decomposed into concrete conditions, return []
- Return ONLY a JSON array

Validation logic:
{validation_logic}
"""
    try:
        response = _call_llm(prompt)
    except Exception:
        return None

    parsed = _extract_json_value(response)
    if not isinstance(parsed, list) or not parsed:
        return None

    conditions = []
    for item in parsed:
        if not isinstance(item, str):
            return None
        condition = item.strip()
        if not condition or _is_vague_condition(condition):
            return None
        conditions.append(condition)

    return conditions or None


def _generate_condition_violation(condition: str, sample: dict) -> Any:
    """Generate one output that should violate the target validation condition."""
    if _is_vague_condition(condition):
        return None

    candidate = _generate_targeted_violation_from_rules(condition, sample)
    if candidate is not None:
        return candidate
    return _llm_generate_targeted_violation("condition", condition, sample)


def generate_checker(schema: dict) -> str | None:
    """Generate a checker, validate it against the protocol, and return source on success."""
    try:
        prompt = _build_checker_prompt(schema)
        response = _call_llm(prompt)
        checker_source = _extract_check_function(response)
        if checker_source is None:
            print("failure_mode: extraction_failed")
            return None

        check_fn = _compile_checker(checker_source)
        if check_fn is None:
            print("failure_mode: extraction_failed")
            return None

        parsed_samples = []
        for sample_case in schema.get("sample_cases", []):
            parsed = _parse_sample_case(schema, sample_case.get("input", ""), sample_case.get("output", ""))
            if parsed is None:
                print("failure_mode: format_mismatch")
                return None
            parsed_samples.append(
                {
                    "schema": schema,
                    "input_args": parsed[0],
                    "output": parsed[1],
                    "raw_input": sample_case.get("input", ""),
                    "raw_output": sample_case.get("output", ""),
                }
            )

        for index, sample in enumerate(parsed_samples, start=1):
            accepted, reason = _call_checker(check_fn, sample["input_args"], sample["output"])
            if not accepted:
                print(f"sample_failure: sample_{index}: {reason}")
                print("failure_mode: checker_rejected_samples")
                return None

        for invariant in schema.get("invariants", []):
            violation = _find_violation_for_samples(
                parsed_samples,
                lambda sample, inv=invariant: _generate_invariant_violation(inv, sample),
            )
            if violation is None:
                print(f"invariant_failure: {invariant}")
                print("failure_mode: checker_rejected_invariants")
                return None
            sample, bad_output = violation
            accepted, reason = _call_checker(check_fn, sample["input_args"], bad_output)
            if accepted:
                print(f"invariant_failure: {invariant}: accepted targeted violation")
                print("failure_mode: checker_rejected_invariants")
                return None

        for index, sample in enumerate(parsed_samples, start=1):
            negatives = _generate_negative_outputs(sample, check_fn=check_fn)
            if len(negatives) < 3:
                print(f"negative_failure: sample_{index}: only generated {len(negatives)} negatives")
                print("failure_mode: checker_rejected_negatives")
                return None
            for bad_output in negatives[:5]:
                accepted, reason = _call_checker(check_fn, sample["input_args"], bad_output)
                if accepted:
                    print(f"negative_failure: sample_{index}: accepted negative output")
                    print("failure_mode: checker_rejected_negatives")
                    return None

        conditions = _parse_validation_conditions(schema.get("validation_logic", ""))
        if not conditions:
            print("failure_mode: checker_rejected_coverage")
            return None

        for condition in conditions:
            violation = _find_violation_for_samples(
                parsed_samples,
                lambda sample, cond=condition: _generate_condition_violation(cond, sample),
            )
            if violation is None:
                print(f"coverage_failure: {condition}")
                print("failure_mode: checker_rejected_coverage")
                return None
            sample, bad_output = violation
            accepted, reason = _call_checker(check_fn, sample["input_args"], bad_output)
            if accepted:
                print(f"coverage_failure: {condition}: accepted targeted violation")
                print("failure_mode: checker_rejected_coverage")
                return None

        print("checker_confidence: MEDIUM")
        return checker_source
    except Exception as exc:
        print(f"checker_generator_error: {exc}")
        print("failure_mode: extraction_failed")
        return None


def _parse_case_from_cursor(cursor: _TokenCursor, fields: list[dict]) -> dict | None:
    case: dict[str, Any] = {}
    for field in fields:
        name = field.get("name")
        field_type = (field.get("type") or "").lower()
        description = field.get("description", "")
        if not name:
            return None

        if "list" in field_type or "array" in field_type:
            length = _infer_list_length(name, field_type, description, case)
            if length is not None:
                tokens = cursor.consume_tokens(length)
            else:
                tokens = cursor.consume_line_tokens()
            if not tokens:
                return None
            case[name] = _coerce_list_tokens(tokens, field_type, description)
        else:
            token = cursor.consume_token()
            if token is None:
                return None
            scalar = _coerce_scalar_token(token, field_type)
            if scalar is None and "string" not in field_type:
                return None
            case[name] = token if scalar is None else scalar
    return case


def _infer_list_length(name: str, field_type: str, description: str, current_case: dict) -> int | None:
    text = f"{name} {field_type} {description}".lower()
    patterns = [
        r"list of ([a-z_][a-z0-9_]*)",
        r"array of ([a-z_][a-z0-9_]*)",
        r"([a-z_][a-z0-9_]*) integers",
        r"([a-z_][a-z0-9_]*) values",
        r"length ([a-z_][a-z0-9_]*)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if not match:
            continue
        var_name = match.group(1)
        if var_name in current_case and isinstance(current_case[var_name], int):
            return current_case[var_name]

    heuristics = []
    lowered_name = name.lower()
    if lowered_name in {"k", "ks"}:
        heuristics.extend(["m", "n"])
    if lowered_name in {"a", "arr", "array", "nums", "numbers", "values"}:
        heuristics.extend(["n", "m"])

    for candidate in heuristics:
        value = current_case.get(candidate)
        if isinstance(value, int):
            return value
    return None


def _coerce_scalar_token(token: str, field_type: str) -> Any:
    field_type = field_type.lower()
    if "int" in field_type or "integer" in field_type:
        try:
            return int(token)
        except ValueError:
            return None
    if "bool" in field_type or "boolean" in field_type:
        lowered = token.lower()
        if lowered in {"true", "yes", "1"}:
            return True
        if lowered in {"false", "no", "0"}:
            return False
        return None
    if "float" in field_type:
        try:
            return float(token)
        except ValueError:
            return None
    return token


def _coerce_list_tokens(tokens: list[str], field_type: str, description: str) -> list[Any]:
    field_type = field_type.lower()
    text = f"{field_type} {description}".lower()
    if "int" in text or "integer" in text:
        values = []
        for token in tokens:
            try:
                values.append(int(token))
            except ValueError:
                return tokens
        return values
    return tokens


def _parse_multi_case_output(schema: dict, raw_output: str, cases: list[dict]) -> list[Any] | None:
    lines = [line.strip() for line in raw_output.splitlines() if line.strip()]
    if len(lines) != len(cases):
        return None

    output_format = schema.get("output_format", {})
    outputs = []
    for line, case in zip(lines, cases):
        value = _parse_case_output_value(output_format, line, case)
        if value is None:
            return None
        outputs.append(value)
    return outputs


def _parse_single_case_output(output_format: dict, raw_output: str, case_input: dict) -> Any:
    output_type = (output_format.get("type") or "string").lower()
    trimmed = raw_output.strip()
    if not trimmed:
        return None

    if output_type == "string":
        return trimmed
    if output_type == "integer":
        tokens = _split_tokens(trimmed)
        if not tokens:
            return None
        try:
            return int(tokens[0])
        except ValueError:
            return None
    if output_type == "boolean":
        tokens = _split_tokens(trimmed)
        if not tokens:
            return None
        return _coerce_scalar_token(tokens[0], "boolean")
    if output_type == "list":
        tokens = _split_tokens(trimmed)
        return _coerce_list_tokens(tokens, "list of integers", output_format.get("description", ""))
    return trimmed


def _parse_case_output_value(output_format: dict, line: str, case_input: dict) -> Any:
    output_type = (output_format.get("type") or "string").lower()
    if output_type == "string":
        return line.strip()
    if output_type == "integer":
        try:
            return int(_split_tokens(line)[0])
        except (IndexError, ValueError):
            return None
    if output_type == "boolean":
        tokens = _split_tokens(line)
        if not tokens:
            return None
        return _coerce_scalar_token(tokens[0], "boolean")
    if output_type == "list":
        tokens = _split_tokens(line)
        if not tokens:
            return []
        return _coerce_list_tokens(tokens, "list of integers", output_format.get("description", ""))
    return line.strip()


def _split_tokens(text: str) -> list[str]:
    return [part for part in re.split(r"[\s,]+", text.strip()) if part]


def _call_checker(check_fn: Callable, input_args: dict, output: Any) -> tuple[bool, str]:
    try:
        result = check_fn(copy.deepcopy(input_args), copy.deepcopy(output))
    except Exception as exc:
        return False, f"checker raised: {exc}"

    if not isinstance(result, tuple) or len(result) != 2:
        return False, "checker returned non-tuple result"

    accepted, reason = result
    if not isinstance(accepted, bool) or not isinstance(reason, str):
        return False, "checker returned invalid tuple payload"
    return accepted, reason


def _find_violation_for_samples(parsed_samples: list[dict], generator: Callable[[dict], Any]) -> tuple[dict, Any] | None:
    for sample in parsed_samples:
        candidate = generator(sample)
        if candidate is not None:
            return sample, candidate
    return None


def _generate_negative_outputs(sample: dict, check_fn: Callable | None = None) -> list[Any]:
    variants = []
    seen = set()
    candidate_generators = [
        lambda s: _mutation_wrong_type(s),
        lambda s: _mutation_wrong_length(s),
        lambda s: _mutation_duplicate_or_missing(s),
        lambda s: _mutation_off_by_one(s),
        lambda s: _mutation_reverse_order(s),
        lambda s: _mutation_negative_one_misuse(s),
        lambda s: _mutation_break_adjacency(s),
        lambda s: _mutation_wrong_outer_length(s),
    ]

    for generator in candidate_generators:
        candidate = generator(sample)
        if candidate is None:
            continue
        key = _stable_key(candidate)
        if key in seen:
            continue
        if check_fn is not None:
            accepted, _ = _call_checker(check_fn, sample["input_args"], candidate)
            if accepted:
                continue
        seen.add(key)
        variants.append(candidate)
        if len(variants) >= 5:
            break

    return variants


def _generate_targeted_violation_from_rules(target_text: str, sample: dict) -> Any:
    lowered = target_text.lower()
    if "length" in lowered:
        return _mutation_wrong_length(sample)
    if "permutation" in lowered or "exactly once" in lowered or "contains each integer exactly once" in lowered:
        return _mutation_duplicate_or_missing(sample)
    if "adjacent" in lowered or "difference" in lowered or "divisible" in lowered:
        return _mutation_break_adjacency(sample)
    if "-1" in lowered or "no valid permutation" in lowered or "if and only if" in lowered:
        return _mutation_negative_one_misuse(sample)
    if "type" in lowered or "integer" in lowered or "boolean" in lowered or "string" in lowered or "list" in lowered:
        return _mutation_wrong_type(sample)
    return None


def _mutation_wrong_type(sample: dict) -> Any:
    output = sample["output"]
    if isinstance(output, list) and _is_multi_case_sample(sample):
        return {"unexpected": True}
    if isinstance(output, str):
        return 123456
    if isinstance(output, bool):
        return "not_bool"
    if isinstance(output, int):
        return "not_int"
    if isinstance(output, list):
        return "not_a_list"
    return {"unexpected": True}


def _mutation_wrong_outer_length(sample: dict) -> Any:
    if not _is_multi_case_sample(sample):
        return None
    outputs = copy.deepcopy(sample["output"])
    if not isinstance(outputs, list):
        return None
    if len(outputs) > 1:
        return outputs[:-1]
    return outputs + [outputs[0]]


def _mutation_wrong_length(sample: dict) -> Any:
    selection = _select_sequence_case(sample)
    if selection is None:
        return None
    case_index, sequence, original = selection
    if len(sequence) > 1:
        mutated = sequence[:-1]
    else:
        mutated = sequence + [sequence[0] + 1 if sequence else 0]
    return _wrap_case_output(sample, case_index, _serialize_sequence_like(original, mutated))


def _mutation_duplicate_or_missing(sample: dict) -> Any:
    selection = _select_sequence_case(sample)
    if selection is None:
        return None
    case_index, sequence, original = selection
    if not sequence:
        return None
    mutated = list(sequence)
    replacement = mutated[0]
    mutated[-1] = replacement
    return _wrap_case_output(sample, case_index, _serialize_sequence_like(original, mutated))


def _mutation_off_by_one(sample: dict) -> Any:
    selection = _select_sequence_case(sample)
    if selection is not None:
        case_index, sequence, original = selection
        if not sequence:
            return None
        mutated = list(sequence)
        mutated[0] = mutated[0] + 1
        return _wrap_case_output(sample, case_index, _serialize_sequence_like(original, mutated))

    if _is_multi_case_sample(sample):
        outputs = copy.deepcopy(sample["output"])
        for index, value in enumerate(outputs):
            if isinstance(value, int):
                outputs[index] = value + 1
                return outputs
            if isinstance(value, str) and value.strip() == "-1":
                outputs[index] = "-2"
                return outputs
        return None

    output = sample["output"]
    if isinstance(output, int):
        return output + 1
    if isinstance(output, str) and output.strip() == "-1":
        return "-2"
    return None


def _mutation_reverse_order(sample: dict) -> Any:
    selection = _select_sequence_case(sample)
    if selection is None:
        return None
    case_index, sequence, original = selection
    if len(sequence) < 2:
        return None
    mutated = list(reversed(sequence))
    if sample.get("schema", {}).get("has_multiple_valid_outputs"):
        case_input = _case_input(sample, case_index or 0)
        if _is_valid_permutation(mutated, case_input) and not _violates_adjacency(mutated, case_input):
            return None
    return _wrap_case_output(sample, case_index, _serialize_sequence_like(original, mutated))


def _mutation_negative_one_misuse(sample: dict) -> Any:
    if _is_multi_case_sample(sample):
        outputs = copy.deepcopy(sample["output"])
        for index, value in enumerate(outputs):
            if isinstance(value, str) and value.strip() != "-1":
                outputs[index] = "-1"
                return outputs
            if isinstance(value, list):
                outputs[index] = "-1"
                return outputs
        case_input = _case_input(sample, 0)
        n_value = case_input.get("n")
        if isinstance(n_value, int) and n_value > 0:
            outputs[0] = " ".join(str(i) for i in range(n_value))
            return outputs
        return None

    output = sample["output"]
    if isinstance(output, str) and output.strip() != "-1":
        return "-1"
    if isinstance(output, list):
        return "-1"
    if isinstance(output, int):
        return -1
    return None


def _mutation_break_adjacency(sample: dict) -> Any:
    selection = _select_sequence_case(sample)
    if selection is None:
        return None

    case_index, sequence, original = selection
    case_input = _case_input(sample, case_index)
    if not _can_check_adjacency(case_input):
        return None

    candidates = []
    if len(sequence) >= 2:
        swapped = list(sequence)
        swapped[0], swapped[1] = swapped[1], swapped[0]
        candidates.append(swapped)
        candidates.append(list(reversed(sequence)))
        candidates.append(sequence[1:] + sequence[:1])

    n_value = case_input.get("n")
    if isinstance(n_value, int) and n_value == len(sequence):
        candidates.append(list(range(n_value)))

    for candidate in candidates:
        if candidate == sequence:
            continue
        if _is_valid_permutation(candidate, case_input) and _violates_adjacency(candidate, case_input):
            return _wrap_case_output(sample, case_index, _serialize_sequence_like(original, candidate))
    return None


def _select_sequence_case(sample: dict) -> tuple[int | None, list[int], Any] | None:
    case_outputs = sample["output"] if _is_multi_case_sample(sample) else [sample["output"]]
    for index, value in enumerate(case_outputs):
        sequence = _parse_int_sequence(value)
        if sequence is None or len(sequence) < 1:
            continue
        return (index if _is_multi_case_sample(sample) else None, sequence, value)
    return None


def _parse_int_sequence(value: Any) -> list[int] | None:
    if isinstance(value, list) and all(isinstance(item, int) for item in value):
        return list(value)
    if isinstance(value, str):
        stripped = value.strip()
        if stripped == "-1":
            return None
        tokens = _split_tokens(stripped)
        if not tokens:
            return None
        integers = []
        for token in tokens:
            try:
                integers.append(int(token))
            except ValueError:
                return None
        return integers
    return None


def _serialize_sequence_like(original: Any, sequence: list[int]) -> Any:
    if isinstance(original, list):
        return sequence
    return " ".join(str(value) for value in sequence)


def _wrap_case_output(sample: dict, case_index: int | None, case_output: Any) -> Any:
    if not _is_multi_case_sample(sample):
        return case_output
    outputs = copy.deepcopy(sample["output"])
    if case_index is None:
        return outputs
    outputs[case_index] = case_output
    return outputs


def _is_multi_case_sample(sample: dict) -> bool:
    return sample.get("schema", {}).get("input_structure", {}).get("type") == "multi_case"


def _case_input(sample: dict, case_index: int) -> dict:
    if _is_multi_case_sample(sample):
        return sample["input_args"]["cases"][case_index]
    return sample["input_args"]


def _can_check_adjacency(case_input: dict) -> bool:
    divisors = _find_divisor_list(case_input)
    return bool(divisors)


def _find_divisor_list(case_input: dict) -> list[int]:
    for key, value in case_input.items():
        if isinstance(value, list) and value and all(isinstance(item, int) for item in value):
            lowered = key.lower()
            if lowered.startswith("k") or "divisor" in lowered:
                return value
    for value in case_input.values():
        if isinstance(value, list) and value and all(isinstance(item, int) for item in value):
            return value
    return []


def _is_valid_permutation(sequence: list[int], case_input: dict) -> bool:
    n_value = case_input.get("n")
    if isinstance(n_value, int):
        return len(sequence) == n_value and set(sequence) == set(range(n_value))
    return len(sequence) == len(set(sequence))


def _violates_adjacency(sequence: list[int], case_input: dict) -> bool:
    divisors = [value for value in _find_divisor_list(case_input) if isinstance(value, int) and value != 0]
    if not divisors:
        return False
    for index in range(len(sequence) - 1):
        diff = abs(sequence[index + 1] - sequence[index])
        if not any(diff % divisor == 0 for divisor in divisors):
            return True
    return False


def _llm_generate_targeted_violation(target_kind: str, target_text: str, sample: dict) -> Any:
    prompt = f"""Produce a deliberately wrong candidate output for checker validation.

Return ONLY JSON with this exact shape:
{{"candidate_output": <json value>}}

Rules:
- The candidate_output must use the same outer representation shape as the reference output below
- For multi-case outputs, keep the same list length and mutate only one case if possible
- Try to violate only the target {target_kind}, while preserving unrelated properties when possible
- Do not explain anything

Target {target_kind}:
{target_text}

Schema summary:
{json.dumps({
    "input_structure": sample["schema"].get("input_structure"),
    "output_format": sample["schema"].get("output_format"),
    "invariants": sample["schema"].get("invariants"),
}, indent=2, ensure_ascii=False)}

Reference input_args:
{json.dumps(sample["input_args"], indent=2, ensure_ascii=False)}

Reference valid output:
{json.dumps(sample["output"], indent=2, ensure_ascii=False)}
"""
    try:
        response = _call_llm(prompt)
    except Exception:
        return None

    parsed = _extract_json_value(response)
    if not isinstance(parsed, dict) or "candidate_output" not in parsed:
        return None
    return parsed["candidate_output"]


def _extract_json_value(text: str) -> Any:
    if not text:
        return None
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    block_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if block_match:
        try:
            return json.loads(block_match.group(1))
        except json.JSONDecodeError:
            pass

    for opening, closing in (("[", "]"), ("{", "}")):
        start = text.find(opening)
        end = text.rfind(closing)
        if start >= 0 and end > start:
            snippet = text[start:end + 1]
            try:
                return json.loads(snippet)
            except json.JSONDecodeError:
                continue
    return None


def _is_vague_condition(condition: str) -> bool:
    lowered = condition.strip().lower()
    if len(lowered.split()) < 4:
        return True

    vague_phrases = {
        "output is correct",
        "answer is correct",
        "output is valid",
        "answer is valid",
        "satisfies the problem statement",
        "satisfies the condition",
        "meets the requirements",
        "appropriate output",
        "suitable output",
        "valid answer",
    }
    if any(phrase in lowered for phrase in vague_phrases):
        return True

    concrete_markers = {
        "output",
        "length",
        "permutation",
        "adjacent",
        "difference",
        "divisible",
        "equals",
        "equal",
        "contains",
        "exactly",
        "unique",
        "distinct",
        "sum",
        "count",
        "order",
        "value",
        "values",
        "-1",
        "integer",
        "integers",
        "list",
        "boolean",
        "string",
        "pair",
        "pairs",
    }
    return not any(marker in lowered for marker in concrete_markers)


def _stable_key(value: Any) -> str:
    try:
        return json.dumps(value, sort_keys=True, ensure_ascii=False)
    except TypeError:
        return repr(value)
