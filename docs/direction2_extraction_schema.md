**1. Top-level fields:**
```json
{
  "problem_id": "string — slugified name",
  "problem_class": "construction | optimization | counting | decision | search",
  "has_multiple_valid_outputs": "boolean",
  "evaluation_mode": "provisional — always, never registry",
  "input_structure": {
    "type": "single_case | multi_case",
    "test_case_count_var": "string or null",
    "per_case_format": "ordered list of fields with types"
  },
  "output_format": {
    "type": "integer | list | string | boolean",
    "description": "one sentence"
  },
  "constraints": {
    "variable_name": {
      "expression": "Python-evaluatable string",
      "depends_on": ["list of variable names this depends on"]
    }
  },
  "invariants": ["explicit list of testable conditions as strings"],
  "validation_logic": "human readable — what makes output correct",
  "validation_type": "exact_match | arrangement | checker",
  "sample_cases": [
    {"input": "raw string", "output": "raw string"}
  ]
}
```

**2. Constraint evaluation rules:**
- All expressions must be valid Python
- Variables evaluated in dependency order
- Cyclic dependencies → extraction rejected
- Undefined variables → extraction rejected
- Evaluation context: only extracted variable names, no globals

**3. Invariant format:**
- Each invariant is a testable predicate in plain English
- Must map to a verifiable property of the output
- Examples: "output is a permutation of 0..n-1", "output length equals n", "sum of output equals target"
- No invariants derived implicitly — all must be explicit in schema

**4. Input structure rules:**
- Multi-case: `type=multi_case`, `test_case_count_var` names the variable holding t
- Single-case: `type=single_case`, `test_case_count_var=null`
- `per_case_format`: ordered list of `{name, type, description}` for each line of input

**5. Validation type rules:**
- `exact_match`: one correct answer, direct comparison
- `arrangement`: any valid arrangement, checker required
- `checker`: complex validation, checker required, lowest trust
