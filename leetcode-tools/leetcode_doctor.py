"""
LeetCode Doctor - AI-Powered Code Reviewer
===========================================

Analyzes your LeetCode solutions TODO by TODO, providing AI-powered feedback,
grading, and progressive hints until each TODO passes the required threshold.

Usage:
    python leetcode_doctor.py                           # Analyze the most recent file
    python leetcode_doctor.py 3870                      # Analyze problem 3870
    python leetcode_doctor.py "3870. Count Commas in Range.py"  # Analyze specific file
    python leetcode_doctor.py --show-solution           # Show solution for current file
    python leetcode_doctor.py --reset                   # Reset progress for current file
    python leetcode_doctor.py --all                     # Analyze all files with TODOs
    python leetcode_doctor.py --help                    # Show help

How it works:
    1. Scans your solution file for TODOs
    2. Evaluates each TODO in order using AI
    3. Grades based on criteria (8/10 for docs, 100% tests for solution)
    4. Adds inline feedback comments to your file
    5. Blocks next TODO until current one passes
    6. Tracks progress across sessions

TODO Order (checked sequentially):
    1. Problem Statement - Must be complete and accurate
    2. Approach - Must describe a valid algorithm
    3. Complexity - Must state accurate time/space complexity
    4. Solution - Must pass ALL test cases
    5. Test Cases - Must cover examples and edge cases

Grading:
    - Problem Statement: 8/10 to pass
    - Approach: 8/10 to pass
    - Complexity: 8/10 to pass
    - Solution: 100% test pass rate required
    - Test Cases: 8/10 to pass (coverage + correctness)

Configuration:
    - AI Provider: OpenAI (default), Ollama (local), or Claude
    - Set environment variables or configure in .qwen/doctor_config.json
"""

import os
import re
import sys
import json
import time
import hashlib
import subprocess
import builtins
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Tuple

TOOLS_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = TOOLS_ROOT.parent
SOLUTIONS_ROOT = PROJECT_ROOT / "solutions"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

from execution_controller import DEFAULT_BATCH_SIZE, ExecutionControlError, get_execution_controller

# Import via interface layer — decouples Doctor from Suggestor internals
from doctor_interface import (
    fetch_problem_statement, clean_html_content, get_folder_for_problem,
    fetch_ratings, find_unsolved_problems, get_existing_problems,
    parse_problem_details
)
from utils import chunk_items  # Shared utility

CONTROLLER = get_execution_controller(SOLUTIONS_ROOT)
SCAN_BATCH_SIZE = DEFAULT_BATCH_SIZE
RATING_CHUNK_SIZE = 25
FOLDER_PATTERN = re.compile(r"\d+\s+to\s+\d+")


def _coerce_console_text(text: str, stream) -> str:
    """Make console text safe for legacy Windows code pages."""
    encoding = getattr(stream, "encoding", None) or "utf-8"
    try:
        text.encode(encoding)
        return text
    except UnicodeEncodeError:
        return text.encode(encoding, errors="replace").decode(encoding)


def _print_safe(*args, **kwargs):
    """Print without crashing when stdout/stderr cannot encode emoji."""
    try:
        return builtins.print(*args, **kwargs)
    except UnicodeEncodeError:
        stream = kwargs.get("file") or sys.stdout
        sep = kwargs.get("sep", " ")
        end = kwargs.get("end", "\n")
        flush = kwargs.get("flush", False)
        text = sep.join(str(arg) for arg in args)
        stream.write(_coerce_console_text(text, stream))
        stream.write(_coerce_console_text(end, stream))
        if flush and hasattr(stream, "flush"):
            stream.flush()


print = _print_safe


def _sanitize_ai_response(response: str) -> str:
    """Normalize and bound AI output for resilient parsing under stress."""
    if response is None:
        return ""
    if not isinstance(response, str):
        response = str(response)
    response = response.replace("\r\n", "\n").strip()
    if len(response) > MAX_AI_RESPONSE_CHARS:
        response = response[:MAX_AI_RESPONSE_CHARS]
    return response


CLASSIC_PROBLEMS_FILE = PROJECT_ROOT / ".qwen" / "classic_problems.json"


def _load_classic_problems() -> dict:
    """Load classic problems mapping from JSON file."""
    data = CONTROLLER.read_json(CLASSIC_PROBLEMS_FILE, default=None)
    if data is None:
        return {}
    # Convert string keys to integers
    return {int(k): v for k, v in data.items()}


def get_problem_slug_by_id(problem_id: int) -> Optional[dict]:
    """Look up problem slug by problem number using ZeroTrac ratings or local mapping."""
    # Classic problems mapping (problems 1-745 not in ZeroTrac)
    CLASSIC_PROBLEMS = _load_classic_problems()

    # Check local mapping first
    if problem_id in CLASSIC_PROBLEMS:
        return CLASSIC_PROBLEMS[problem_id]

    # Fall back to ZeroTrac
    try:
        ratings = fetch_ratings()

        matches = CONTROLLER.process_batch(
            list(chunk_items(ratings, RATING_CHUNK_SIZE)),
            lambda rating_chunk: [
                parse_problem_details(problem['raw_line'])
                for problem in rating_chunk
                if problem['id'] == problem_id
            ],
            batch_size=SCAN_BATCH_SIZE,
            pipeline="validation",
            flush_writes=False,
            file_operation=False,
            batch_name="lookup-problem-slug",
            stop_when=lambda result, *_: bool(result),
        )
        for match in matches:
            if match:
                return match[0]
        return None
    except Exception as e:
        failure_type = classify_exception(e)
        print(f"⚠ Could not fetch problem slug ({failure_type}): {e}")
        return None


# Configuration
DOCTOR_TRACKING_FILE = PROJECT_ROOT / ".qwen" / "doctor_tracking.json"
DOCTOR_CONFIG_FILE = PROJECT_ROOT / ".qwen" / "doctor_config.json"
DOCTOR_SKILL_STATE_FILE = PROJECT_ROOT / ".qwen" / "doctor_skill_state.json"

# Grading thresholds
PASSING_GRADE_DOCS = 8.0  # Out of 10
PASSING_GRADE_SOLUTION = 1.0  # 100% pass rate (1.0)
MAX_HINT_ATTEMPTS = 3  # After this many failures, offer to show solution
MAX_AI_RESPONSE_CHARS = 12000
DEGRADED_PREFIX = "[DEGRADED:rule_based]"
TODO_ORDER = ['problem_statement', 'approach', 'complexity', 'solution', 'test_cases']
TODO_NAMES = ['Problem Statement', 'Approach', 'Complexity', 'Solution', 'Test Cases']
AI_EVALUATION_SYSTEM_PROMPT = (
    "You are an expert LeetCode code reviewer. You evaluate code quality, correctness, "
    "and provide constructive feedback. Always respond with a numeric grade out of 10 and "
    "specific feedback. Gate rule: a TODO can advance only with authoritative ai mode "
    "evaluation; degraded/rule_based evaluation can fail a TODO but can never pass one."
)

# Longitudinal grading parameters
SKILL_CATEGORIES = ["dp", "graph", "greedy", "recursion", "string"]
OVERALL_ACCURACY_WINDOW = 50
TREND_WINDOW = 20
CONSISTENCY_WINDOW = 20
EFFICIENCY_WINDOW = 50  # Bound efficiency history
ROBUSTNESS_WINDOW = 50  # Bound robustness history
TREND_IMPROVING_THRESHOLD = 0.05
TREND_DEGRADING_THRESHOLD = -0.05


# ============================================================
# Longitudinal Skill State Persistence
# ============================================================
def _default_skill_state() -> dict:
    return {
        "total_problems": 0,
        "overall_accuracy": 0.0,
        "skills": {cat: {"score": 0.0, "count": 0} for cat in SKILL_CATEGORIES},
        "efficiency": 0.0,
        "robustness": 0.0,
        "consistency": 0.0,
        "recent_trend": [],
        "_accuracy_history": [],
        "_efficiency_history": [],
        "_robustness_history": [],
        "_consistency_history": [],
    }


def load_skill_state() -> dict:
    state = CONTROLLER.read_json(DOCTOR_SKILL_STATE_FILE, default=None)
    if state is None:
        return _default_skill_state()
    # Back-fill missing keys from schema
    defaults = _default_skill_state()
    for key, val in defaults.items():
        if key not in state:
            state[key] = val
    for cat in SKILL_CATEGORIES:
        if cat not in state.get("skills", {}):
            state.setdefault("skills", {})[cat] = {"score": 0.0, "count": 0}
    return state


def load_skill_state_validated() -> dict:
    """Load skill state with explicit validation.

    Gap 1 Fix: If skill state is missing, corrupted, or returns defaults silently,
    we warn explicitly instead of running on zeroed state.
    """
    state = load_skill_state()
    if state["total_problems"] == 0:
        # Either genuinely new user OR corrupted/missing state
        # Cannot distinguish silently — warn explicitly
        print("⚠ Skill state is empty. Suggestor running in rating-only mode.")
        print("  Complete problems through the Doctor to enable personalized ranking.")
    return state


def save_skill_state(state: dict) -> None:
    CONTROLLER.ensure_directory(DOCTOR_SKILL_STATE_FILE.parent)
    CONTROLLER.queue_json_write(DOCTOR_SKILL_STATE_FILE, state, indent=2)
    CONTROLLER.commit(reason="doctor:save-skill-state")


# ============================================================
# Feature Extraction (per problem)
# ============================================================
def extract_features(evaluation_results: dict, test_results: dict, file_content: str) -> dict:
    """Extract grading features from evaluation + test results.

    Returns dict with:
        correctness, runtime_score, memory_score, topic, error_type
    """
    # Correctness: derive from TODO evaluations
    # A problem is "correct" if all TODOs pass (docs >= 8/10, solution 100% tests)
    todo_correct = []
    for todo_key, todo_result in evaluation_results.items():
        grade = todo_result.get("grade", 0.0)
        todo_correct.append(grade >= 8.0 if todo_key != "solution" else grade >= 10.0)

    if not todo_correct:
        correctness = 0.0
    elif all(todo_correct):
        correctness = 1.0
    elif any(todo_correct):
        correctness = 0.5
    else:
        correctness = 0.0

    # Runtime score: based on test pass_rate (proxy — no real timing here)
    pass_rate = test_results.get("pass_rate", 0.0)
    total_tests = test_results.get("total", 0)
    # Normalize: if all tests pass, score = 1.0; partial = proportional
    runtime_score = pass_rate

    # Memory score: approximate via code complexity (no real memory measurement)
    # Heuristic: fewer lines + no nested loops => better
    lines = file_content.count("\n")
    nested_loops = file_content.count("for ") + file_content.count("while ")
    # Simple normalization: cap at 1000 lines, penalty for nesting
    memory_score = max(0.0, min(1.0, 1.0 - (lines / 2000.0) - (nested_loops * 0.05)))

    # Topic extraction: with confidence threshold to avoid poisoning skill state
    topic = _detect_topic_with_threshold(file_content, threshold=0.4)

    # Error type classification
    error_type = _classify_error(evaluation_results, test_results)

    return {
        "correctness": correctness,
        "runtime_score": round(runtime_score, 4),
        "memory_score": round(memory_score, 4),
        "topic": topic,
        "error_type": error_type,
    }


def _detect_topic(file_content: str) -> tuple[str, float]:
    """Best-effort topic detection from code/docstring content.
    
    Returns:
        Tuple of (topic, confidence) where confidence is 0.0-1.0
    """
    lower = file_content.lower()
    topic_keywords = {
        "dp": ["dynamic", "dp ", "memoiz", "subproblem", "optimal substructure", "knapsack"],
        "graph": ["graph", "bfs", "dfs", "adjacent", "node ", "edge", "traversal", "topological"],
        "greedy": ["greedy", "local optimal", "sort ", "heap", "priority"],
        "recursion": ["recursive", "recursion", "base case", "divide and conquer", "backtrack"],
        "string": ["string", "substring", "palindrome", "char", "regex", "pattern"],
    }
    scores = {}
    for cat, keywords in topic_keywords.items():
        scores[cat] = sum(1 for kw in keywords if kw in lower)
    
    best = max(scores, key=scores.get) if scores else "string"
    best_score = scores.get(best, 0)
    total = sum(scores.values())
    confidence = best_score / total if total > 0 else 0.0
    
    return best, confidence


def _detect_topic_with_threshold(file_content: str, threshold: float = 0.4) -> str:
    """Topic detection with confidence threshold to prevent unreliable classification.
    
    Gap 2 Fix: If confidence is below threshold, return "unknown" to avoid
    poisoning skill state with uncertain classification.
    """
    topic, confidence = _detect_topic(file_content)
    if confidence < threshold:
        return "unknown"
    return topic


def _classify_error(evaluation_results: dict, test_results: dict) -> str:
    """Classify the primary error type for a failed problem."""
    errors = test_results.get("errors", [])
    if errors:
        err_str = str(errors).lower()
        if "indexerror" in err_str or "keyerror" in err_str or "typeerror" in err_str:
            return "runtime"
        if "assertion" in err_str or "expected" in err_str:
            return "edge_case"
    # Check if doc TODOs failed but tests passed
    for key, result in evaluation_results.items():
        if key == "solution":
            continue
        if result.get("status", "").upper() == "FAIL":
            return "logic"
    if test_results.get("pass_rate", 1.0) < 1.0:
        return "edge_case"
    return "none"


# ============================================================
# Update Rules (STRICT per specification)
# ============================================================
def update_skill_state(state: dict, features: dict) -> dict:
    """Apply update rules to the persistent skill state.

    Returns the updated state dict.
    """
    topic = features["topic"]
    correctness = features["correctness"]
    runtime_score = features["runtime_score"]
    memory_score = features["memory_score"]
    error_type = features["error_type"]

    # 1. Skill update (per category): new_score = (old_score * count + current_score) / (count + 1)
    # Skip if topic is "unknown" to avoid poisoning skill state
    if topic != "unknown" and topic in state["skills"]:
        skill = state["skills"][topic]
        old_score = skill["score"]
        old_count = skill["count"]
        skill["score"] = round((old_score * old_count + correctness) / (old_count + 1), 4)
        skill["count"] = old_count + 1

    # 2. Overall accuracy: moving average of last 50 results
    state["_accuracy_history"].append(correctness)
    if len(state["_accuracy_history"]) > OVERALL_ACCURACY_WINDOW:
        state["_accuracy_history"] = state["_accuracy_history"][-OVERALL_ACCURACY_WINDOW:]
    state["overall_accuracy"] = round(
        sum(state["_accuracy_history"]) / len(state["_accuracy_history"]), 4
    )

    # 3. Efficiency: 0.7 * runtime_score + 0.3 * memory_score
    efficiency = 0.7 * runtime_score + 0.3 * memory_score
    state["_efficiency_history"].append(efficiency)
    if len(state["_efficiency_history"]) > EFFICIENCY_WINDOW:
        state["_efficiency_history"] = state["_efficiency_history"][-EFFICIENCY_WINDOW:]
    state["efficiency"] = round(
        sum(state["_efficiency_history"]) / len(state["_efficiency_history"]), 4
    )

    # 4. Robustness: based on edge_case success rate + failure frequency
    robustness_score = 1.0 if error_type == "none" else (0.5 if error_type == "edge_case" else 0.0)
    state["_robustness_history"].append(robustness_score)
    if len(state["_robustness_history"]) > ROBUSTNESS_WINDOW:
        state["_robustness_history"] = state["_robustness_history"][-ROBUSTNESS_WINDOW:]
    state["robustness"] = round(
        sum(state["_robustness_history"]) / len(state["_robustness_history"]), 4
    )

    # 5. Consistency: based on variance of last N correctness results
    state["_consistency_history"].append(correctness)
    if len(state["_consistency_history"]) > CONSISTENCY_WINDOW:
        state["_consistency_history"] = state["_consistency_history"][-CONSISTENCY_WINDOW:]
    hist = state["_consistency_history"]
    if len(hist) >= 2:
        mean = sum(hist) / len(hist)
        variance = sum((x - mean) ** 2 for x in hist) / len(hist)
        # Consistency = inverse of variance (clamped to 0–1)
        state["consistency"] = round(max(0.0, min(1.0, 1.0 - variance * 4)), 4)
    else:
        state["consistency"] = 1.0

    # 6. Total problems
    state["total_problems"] += 1

    # 7. Recent trend tracking: last 20 correctness results
    state["recent_trend"].append(correctness)
    if len(state["recent_trend"]) > TREND_WINDOW:
        state["recent_trend"] = state["recent_trend"][-TREND_WINDOW:]

    return state


def compute_trend_label(state: dict) -> str:
    """Compute trend direction from recent_trend using linear slope approximation."""
    trend = state["recent_trend"]
    if len(trend) < 3:
        return "stable"
    n = len(trend)
    # Simple slope via first/last segment average comparison
    mid = n // 2
    first_half_avg = sum(trend[:mid]) / mid
    second_half_avg = sum(trend[mid:]) / (n - mid)
    slope = second_half_avg - first_half_avg
    if slope > TREND_IMPROVING_THRESHOLD:
        return "improving"
    elif slope < TREND_DEGRADING_THRESHOLD:
        return "degrading"
    else:
        return "stable"


def get_weak_areas(state: dict) -> list:
    """Return list of skill categories below overall accuracy OR with zero exposure."""
    overall = state["overall_accuracy"]
    weak = []
    for cat in SKILL_CATEGORIES:
        skill = state["skills"][cat]
        # Untouched topics are weak areas (topic gaming detection)
        if skill["count"] == 0:
            weak.append(cat)
        elif skill["score"] < overall:
            weak.append(cat)
    return weak


def score_problem(problem: dict, skill_state: dict, weights: dict) -> float:
    """Score a single problem based on multi-feature ranking.
    
    Features:
    - w1: normalized rating (0-1, higher = harder, we want slightly above skill)
    - w2: difficulty fit -- reward problems near skill ceiling, not above it
    - w3: topic gap -- boost under-practiced or weak categories  
    - w4: recency bonus -- slight preference for newer problems
    """
    # w1: normalized rating (0-1, higher = harder, we want slightly above skill)
    rating_norm = min(problem['rating'], 3000) / 3000.0

    # w2: difficulty fit -- reward problems near skill ceiling, not above it
    topic = problem.get('topic', 'unknown')
    skill_score = skill_state['skills'].get(topic, {}).get('score', 0.0)
    # Sweet spot: problems 10-30% above current skill level
    difficulty_fit = 1.0 - abs(rating_norm - (skill_score + 0.2))
    difficulty_fit = max(0.0, difficulty_fit)

    # w3: topic gap -- boost under-practiced or weak categories
    weak_areas = get_weak_areas(skill_state)
    topic_gap = 1.0 if topic in weak_areas else 0.0

    # w4: recency bonus -- slight preference for newer problems
    recency = min(problem['id'], 4000) / 4000.0

    return (
        weights['w1'] * rating_norm +
        weights['w2'] * difficulty_fit +
        weights['w3'] * topic_gap +
        weights['w4'] * recency
    )


def rank_problems(problems: list, skill_state: dict, weights: dict) -> list:
    """Rank problems using multi-feature scoring.
    
    Returns sorted list of unsolved problems, highest score first.
    """
    scored = [
        (p, score_problem(p, skill_state, weights))
        for p in problems
        if not p.get('solved', False)
    ]
    return [p for p, _ in sorted(scored, key=lambda x: -x[1])]


# ============================================================
# Doctor evaluation output integration
# ============================================================
def build_grading_output(state: dict, features: dict, evaluation_results: dict) -> dict:
    """Build the required grading output dict after each evaluation."""
    trend = compute_trend_label(state)
    weak = get_weak_areas(state)
    topic = features["topic"]

    return {
        "correctness": features["correctness"],
        "efficiency_score": round(0.7 * features["runtime_score"] + 0.3 * features["memory_score"], 4),
        "skill_update": {
            "topic": topic,
            "new_score": state["skills"][topic]["score"],
            "count": state["skills"][topic]["count"],
        },
        "overall_progress": state["overall_accuracy"],
        "weak_areas": weak,
        "trend": trend,
    }


# ============================================================
# Failure Classification (Fix #3)
# ============================================================
class FailureReason:
    """Structured failure categories — never silently convert to empty result."""
    NETWORK_FAILURE = "NETWORK_FAILURE"           # HTTP/API/timeout errors
    FILE_IO_FAILURE = "FILE_IO_FAILURE"           # Read/write/permission errors
    PARSE_ERROR = "PARSE_ERROR"                   # JSON/regex/structural parse failures
    SCHEMA_INVALID = "SCHEMA_INVALID"             # File exists but violates expected schema
    INCOMPLETE_DATA = "INCOMPLETE_DATA"           # Missing fields, None values, empty collections


def classify_exception(exc: Exception) -> str:
    """Classify an exception into a FailureReason category."""
    import urllib.error
    if isinstance(exc, (urllib.error.URLError, urllib.error.HTTPError)):
        return FailureReason.NETWORK_FAILURE
    if isinstance(exc, json.JSONDecodeError):
        return FailureReason.PARSE_ERROR
    if isinstance(exc, re.error):
        return FailureReason.PARSE_ERROR
    if isinstance(exc, (FileNotFoundError, PermissionError, IsADirectoryError)):
        return FailureReason.FILE_IO_FAILURE
    if isinstance(exc, ValueError):
        return FailureReason.SCHEMA_INVALID
    if isinstance(exc, OSError):
        return FailureReason.FILE_IO_FAILURE
    return FailureReason.NETWORK_FAILURE  # default for unknown


def atomic_write(file_path: Path, content: str, required_markers: List[str] = None) -> bool:
    """
    Fix #1 — Atomic file write using temp file + rename pattern.

    Writes to file_path.tmp, validates structure, then atomically renames to file_path.
    Never leaves a partially written final file visible.

    Args:
        file_path: Target file path
        content: Content to write
        required_markers: List of strings that must appear in content (validation gate)

    Returns:
        True on success, False on failure
    """
    try:
        CONTROLLER.queue_text_write(
            file_path,
            content,
            required_markers=required_markers or [],
        )
        CONTROLLER.commit(reason=f"doctor:write:{file_path.name}")
        return True

    except Exception:
        CONTROLLER.io_manager.clear()
        return False


class AIClient:
    """AI client abstraction layer supporting multiple providers."""

    def __init__(self, provider: str = None):
        config = load_doctor_config()
        self.provider = provider or config.get("ai_provider", "openai")
        self.model = config.get(f"{self.provider}_model", self._get_default_model())
        self.api_key = self._get_api_key()

    def _get_default_model(self) -> str:
        models = {
            "openai": "gpt-4",
            "ollama": "llama3",
            "claude": "claude-3-sonnet-20240229",
            "qwen": "qwen-plus"
        }
        return models.get(self.provider, "qwen-plus")

    def _get_api_key(self) -> str:
        keys = {
            "openai": os.environ.get("OPENAI_API_KEY", ""),
            "claude": os.environ.get("ANTHROPIC_API_KEY", ""),
            "qwen": os.environ.get("DASHSCOPE_API_KEY", ""),
            "ollama": ""  # Local, no key needed
        }
        return keys.get(self.provider, "")

    def analyze(self, prompt: str) -> str:
        """Send prompt to AI and return response."""
        if self.provider == "openai":
            return self._call_openai(prompt)
        elif self.provider == "ollama":
            return self._call_ollama(prompt)
        elif self.provider == "claude":
            return self._call_claude(prompt)
        elif self.provider == "qwen":
            return self._call_qwen(prompt)
        else:
            print(f"⚠ Unsupported AI provider: {self.provider}")
            print("Falling back to rule-based evaluation...\n")
            return rule_based_evaluation(prompt)

    def _request_json(self, request, *, timeout: int, label: str) -> dict:
        last_error = None
        for attempt in range(1, 4):
            try:
                def _send():
                    from urllib.request import urlopen
                    with urlopen(request, timeout=timeout) as response:
                        return json.loads(response.read().decode('utf-8'))

                return CONTROLLER.run_operation(
                    _send,
                    label=label,
                    file_operation=False,
                )
            except Exception as exc:
                last_error = exc
                if attempt >= 3:
                    break
                time.sleep(min(1.5 * attempt, 3.0))
        if last_error is not None:
            raise last_error
        raise RuntimeError("Unknown network error")

    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API."""
        if not self.api_key:
            print("⚠ OPENAI_API_KEY not set!")
            print("Set it with: set OPENAI_API_KEY=your_key_here")
            print("Falling back to rule-based evaluation...\n")
            return rule_based_evaluation(prompt)

        try:
            from urllib.request import Request

            payload = json.dumps({
                "model": self.model,
                "messages": [
                    {"role": "system", "content": AI_EVALUATION_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3
            }).encode('utf-8')

            req = Request("https://api.openai.com/v1/chat/completions", data=payload)
            req.add_header("Content-Type", "application/json")
            req.add_header("Authorization", f"Bearer {self.api_key}")

            data = self._request_json(
                req,
                timeout=60,
                label="network:openai",
            )

            return _sanitize_ai_response(data['choices'][0]['message']['content'])

        except Exception as e:
            failure_type = classify_exception(e)
            print(f"⚠ OpenAI API error ({failure_type}): {e}")
            print("Falling back to rule-based evaluation...\n")
            return rule_based_evaluation(prompt)

    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama (local AI)."""
        try:
            from urllib.request import Request

            payload = json.dumps({
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }).encode('utf-8')

            req = Request("http://localhost:11434/api/generate", data=payload)
            req.add_header("Content-Type", "application/json")

            data = self._request_json(
                req,
                timeout=120,
                label="network:ollama",
            )

            return _sanitize_ai_response(data.get('response', 'No response from Ollama'))

        except Exception as e:
            failure_type = classify_exception(e)
            print(f"⚠ Ollama error ({failure_type}): {e}")
            print("Is Ollama running? (ollama serve)")
            print("Falling back to rule-based evaluation...\n")
            return rule_based_evaluation(prompt)

    def _call_claude(self, prompt: str) -> str:
        """Call Anthropic Claude API."""
        if not self.api_key:
            print("⚠ ANTHROPIC_API_KEY not set!")
            print("Falling back to rule-based evaluation...\n")
            return rule_based_evaluation(prompt)

        try:
            from urllib.request import Request

            payload = json.dumps({
                "model": self.model,
                "max_tokens": 1024,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }).encode('utf-8')

            req = Request("https://api.anthropic.com/v1/messages", data=payload)
            req.add_header("Content-Type", "application/json")
            req.add_header("x-api-key", self.api_key)
            req.add_header("anthropic-version", "2023-06-01")

            data = self._request_json(
                req,
                timeout=60,
                label="network:claude",
            )

            return _sanitize_ai_response(data['content'][0]['text'])

        except Exception as e:
            failure_type = classify_exception(e)
            print(f"⚠ Claude API error ({failure_type}): {e}")
            print("Falling back to rule-based evaluation...\n")
            return rule_based_evaluation(prompt)

    def _call_qwen(self, prompt: str) -> str:
        """Call Alibaba DashScope Qwen API (compatible OpenAI format)."""
        if not self.api_key:
            print("⚠ DASHSCOPE_API_KEY not set!")
            print("Set it with: set DASHSCOPE_API_KEY=your_key_here")
            print("Falling back to rule-based evaluation...\n")
            return rule_based_evaluation(prompt)

        try:
            from urllib.request import Request

            payload = json.dumps({
                "model": self.model,
                "messages": [
                    {"role": "system", "content": AI_EVALUATION_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3
            }).encode('utf-8')

            req = Request("https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions", data=payload)
            req.add_header("Content-Type", "application/json")
            req.add_header("Authorization", f"Bearer {self.api_key}")

            data = self._request_json(
                req,
                timeout=60,
                label="network:qwen",
            )

            return _sanitize_ai_response(data['choices'][0]['message']['content'])

        except Exception as e:
            failure_type = classify_exception(e)
            print(f"⚠ Qwen/DashScope API error ({failure_type}): {e}")
            print("Falling back to rule-based evaluation...\n")
            return rule_based_evaluation(prompt)


def _rule_based_core(prompt: str) -> str:
    """Core fallback heuristic evaluator."""
    prompt_lower = prompt.lower()
    is_problem = 'problem statement' in prompt_lower
    is_approach = 'approach' in prompt_lower
    is_complexity = 'time complexity' in prompt_lower or 'space complexity' in prompt_lower

    # Extract content (everything before "Respond with ONLY")
    resp_pos = prompt_lower.find('respond with only')
    content_part = prompt[:resp_pos] if resp_pos > 0 else prompt
    content_lower = content_part.lower()

    if is_problem:
        has_desc = any(p in content_lower for p in ['you are given', 'given', 'return', 'integer'])
        has_ex = 'example' in content_lower and 'input' in content_lower
        has_con = 'constraint' in content_lower and '<=' in content_lower
        score = (4 if has_desc else 0) + (3 if has_ex else 0) + (3 if has_con else 0)
        fb = []
        if has_desc: fb.append("Problem description present")
        if has_ex: fb.append("Examples included")
        if has_con: fb.append("Constraints listed")
        return f"Grade: {score}/10\nStatus: {'PASS' if score >= 8 else 'FAIL'}\nFeedback: {'; '.join(fb)}"

    elif is_approach:
        # Check if it's a bare TODO placeholder (no real content)
        # Use case-insensitive matching
        has_todo_placeholder = bool(re.search(r'todo:\s*(replace|describe|implement)', content_lower))

        # CRITICAL: If it's still a placeholder, FAIL immediately. Ignore any keywords.
        if has_todo_placeholder:
            return "Grade: 2/10\nStatus: FAIL\nFeedback: Approach has TODO placeholder\nImprovements: Replace TODO with algorithm description\nHint: Think about how you would solve this manually"

        # Only check for algorithm keywords in the actual content part, not the criteria text
        # Split on "approach section:" to get just the user's content
        approach_marker = content_lower.find('approach section:\n')
        if approach_marker >= 0:
            user_content = content_lower[approach_marker + len('approach section:\n'):]
        else:
            user_content = content_lower

        has_algo = any(w in user_content for w in ['iterate', 'loop', 'sort', 'hash', 'count', 'calculate', 'format', 'scan', 'compute'])
        has_steps = bool(re.search(r'(algorithm:|step|first|then|finally|\d+\.)', user_content))
        has_exp = len(user_content) > 150

        if has_algo and has_steps and has_exp:
            return "Grade: 9/10\nStatus: PASS\nFeedback: Approach well-documented with algorithm details"
        elif has_algo and has_steps:
            return "Grade: 8/10\nStatus: PASS\nFeedback: Approach describes valid algorithm"
        elif has_algo and has_exp:
            return "Grade: 7/10\nStatus: FAIL\nFeedback: Approach mentions techniques but lacks step-by-step detail\nImprovements: Add numbered algorithm steps\nHint: Break down your approach into clear steps"
        elif has_exp and not has_algo:
            return "Grade: 5/10\nStatus: FAIL\nFeedback: Approach has content but lacks specific algorithm details\nImprovements: Add specific techniques\nHint: Describe the data structures and algorithms you will use"
        else:
            return "Grade: 3/10\nStatus: FAIL\nFeedback: Approach section is too brief\nImprovements: Describe your algorithm step by step\nHint: Start with 'I will iterate through X...'"

    elif is_complexity:
        t_match = re.search(r'time complexity:.*?o\(([^)]+?)\)', content_lower)
        s_match = re.search(r'space complexity:.*?o\(([^)]+?)\)', content_lower)
        score = 0
        fb = []
        if t_match:
            v = t_match.group(1).strip()
            if v and v != '?':
                score += 4; fb.append(f"Time complexity: O({v})")
            else:
                score += 1; fb.append("Time complexity has placeholder O(?)")
        else:
            fb.append("Time complexity not specified")
        if s_match:
            v = s_match.group(1).strip()
            if v and v != '?':
                score += 4; fb.append(f"Space complexity: O({v})")
            else:
                score += 1; fb.append("Space complexity has placeholder O(?)")
        else:
            fb.append("Space complexity not specified")
        if 'because' in content_lower or 'where' in content_lower:
            score += 2; fb.append("Includes justification")
        return f"Grade: {score}/10\nStatus: {'PASS' if score >= 8 else 'FAIL'}\nFeedback: {'; '.join(fb)}"

    else:
        return "Grade: 5/10\nStatus: FAIL\nFeedback: Could not evaluate section"


def rule_based_evaluation(prompt: str) -> str:
    """Fallback rule-based evaluation when AI is not available."""
    result = _rule_based_core(prompt)
    return f"{DEGRADED_PREFIX}\n{result}"



class DoctorEvaluation:
    """Evaluates a single TODO in a solution file."""

    def __init__(self, ai_client: AIClient):
        self.ai = ai_client

    def evaluate_problem_statement(self, file_content: str, problem_data: dict) -> dict:
        """Evaluate the problem statement TODO."""
        # Extract only the problem statement section
        ps_match = re.search(r'PROBLEM STATEMENT:.*?={5,}\n(.*?)(?=\n={5,}|DIFFICULTY:|APPROACH:)',
                            file_content, re.DOTALL)
        section_content = ps_match.group(1) if ps_match else file_content[:2000]

        prompt = f"""
You are evaluating the problem statement section of a LeetCode solution file.

Criteria (Grade out of 10):
- Completeness (3 points): Does it include full problem description?
- Examples (3 points): Are examples with input/output included?
- Constraints (2 points): Are constraints listed?
- Accuracy (2 points): Is the problem accurately described?

Problem statement section:
{section_content[:2000]}

Respond with ONLY:
Grade: X/10
Status: PASS or FAIL
Feedback: [2-3 sentences of specific feedback]
Improvements: [bullet list of what to improve if failed]
"""

        response = self.ai.analyze(prompt)
        return self._parse_grade_response(response, "problem_statement")

    def evaluate_approach(self, file_content: str) -> dict:
        """Evaluate the approach TODO."""
        # Try to extract the approach section (between TODO #2 marker and TODO #3 marker or end of docstring)
        approach_match = re.search(r'TODO\s*#?2\s*[-—]\s*APPROACH:(.*?)(?=\n={5,}\s*\nTODO\s*#?3|\n"""|\nfrom typing|\nclass Solution)',
                                  file_content, re.DOTALL)
        # If extraction fails, use the whole content (pre-extracted section)
        section_content = approach_match.group(1).strip() if approach_match else file_content.strip()

        prompt = f"""
You are evaluating the approach section of a LeetCode solution file.

Criteria (Grade out of 10):
- Clarity (3 points): Is the approach clearly explained?
- Validity (3 points): Is the algorithm logically sound?
- Specificity (2 points): Are specific techniques mentioned?
- Completeness (2 points): Does it cover the full solution strategy?

Approach section:
{section_content[:1000]}

Respond with ONLY:
Grade: X/10
Status: PASS or FAIL
Feedback: [2-3 sentences of specific feedback]
Improvements: [bullet list of what to improve if failed]
Hint: [if grade < 8, provide a helpful hint]
"""

        response = self.ai.analyze(prompt)
        return self._parse_grade_response(response, "approach")

    def evaluate_complexity(self, file_content: str) -> dict:
        """Evaluate the complexity analysis TODO."""
        # Extract complexity from TODO #3 section
        complexity_match = re.search(r'TODO\s*#?3\s*[-—]\s*COMPLEXITY:.*?Time Complexity:\s*(.*?)\nSpace Complexity:\s*(.*?)(?=\n"""|\nfrom typing|\nclass Solution)',
                                    file_content, re.DOTALL)

        if complexity_match:
            time_complexity = complexity_match.group(1).strip()
            space_complexity = complexity_match.group(2).strip()
            section_content = f"Time Complexity: {time_complexity}\nSpace Complexity: {space_complexity}"
        else:
            # Pre-extracted or direct content
            section_content = file_content.strip()

        prompt = f"""
You are evaluating the complexity analysis of a LeetCode solution file.

Criteria (Grade out of 10):
- Time Complexity (4 points): Is it stated and accurate?
- Space Complexity (4 points): Is it stated and accurate?
- Justification (2 points): Is there reasoning for the complexity?

Complexity analysis:
{section_content}

Respond with ONLY:
Grade: X/10
Status: PASS or FAIL
Feedback: [2-3 sentences of specific feedback]
Improvements: [bullet list of what to improve if failed]
"""

        response = self.ai.analyze(prompt)
        return self._parse_grade_response(response, "complexity")

    def evaluate_solution(self, file_content: str, test_results: dict) -> dict:
        """Evaluate the solution implementation."""
        pass_rate = test_results.get('pass_rate', 0.0)
        total_tests = test_results.get('total', 0)
        passed_tests = test_results.get('passed', 0)
        errors = test_results.get('errors', [])

        # Solution MUST pass 100% of tests
        if pass_rate >= 1.0:
            grade = 10.0
            status = "PASS"
            feedback = f"✓ Solution passes all {total_tests} test cases!"
        elif pass_rate >= 0.75:
            grade = 7.0
            status = "FAIL"
            feedback = f"⚠ Solution passes {passed_tests}/{total_tests} tests ({pass_rate*100:.0f}%)"
        elif pass_rate > 0:
            grade = 4.0
            status = "FAIL"
            feedback = f"✗ Solution only passes {passed_tests}/{total_tests} tests ({pass_rate*100:.0f}%)"
        else:
            grade = 2.0
            status = "FAIL"
            feedback = "✗ Solution fails all test cases"

        if errors:
            feedback += f"\nErrors: {'; '.join(errors[:3])}"

        return {
            'grade': grade,
            'status': status,
            'feedback': feedback,
            'test_results': test_results,
            'improvements': errors if errors else ["Ensure solution handles all edge cases"],
            'hint': self._generate_solution_hint(file_content, test_results) if status == "FAIL" else None,
            'mode': 'tests',
            'validity': 'authoritative',
        }

    def evaluate_test_cases(self, file_content: str) -> dict:
        """Evaluate the test cases TODO."""
        prompt = f"""
You are evaluating the test cases of a LeetCode solution file.

Criteria (Grade out of 10):
- Coverage (4 points): Do tests cover the examples from the problem?
- Edge Cases (3 points): Are edge cases tested?
- Correctness (3 points): Are the expected outputs correct?

File content:
{file_content[-2000:]}  # Look at the end of file where tests are

Respond with ONLY:
Grade: X/10
Status: PASS or FAIL
Feedback: [2-3 sentences of specific feedback]
Improvements: [bullet list of what to improve if failed]
"""

        response = self.ai.analyze(prompt)
        return self._parse_grade_response(response, "test_cases")

    def _parse_grade_response(self, response: str, todo_type: str) -> dict:
        """Parse AI response into structured evaluation."""
        response = _sanitize_ai_response(response)
        if response.startswith(DEGRADED_PREFIX):
            evaluation_mode = "rule_based"
            validity = "degraded"
            response = response[len(DEGRADED_PREFIX):].lstrip("\r\n")
        else:
            evaluation_mode = "ai"
            validity = "authoritative"

        grade_match = re.search(r'Grade:\s*(\d+(?:\.\d+)?)\s*/\s*10', response)
        status_match = re.search(r'Status:\s*(PASS|FAIL)', response, re.IGNORECASE)
        feedback_match = re.search(r'Feedback:\s*(.+?)(?=Improvements:|Hint:|$)', response, re.DOTALL)
        improvements_match = re.search(r'Improvements:\s*(.+?)(?=Hint:|$)', response, re.DOTALL)
        hint_match = re.search(r'Hint:\s*(.+)', response, re.DOTALL)

        grade = float(grade_match.group(1)) if grade_match else 5.0
        status = status_match.group(1).upper() if status_match else ("PASS" if grade >= 8.0 else "FAIL")
        feedback = feedback_match.group(1).strip() if feedback_match else "See detailed feedback"
        improvements = improvements_match.group(1).strip() if improvements_match else ""
        hint = hint_match.group(1).strip() if hint_match else None

        result = {
            'grade': grade,
            'status': status,
            'feedback': feedback,
            'improvements': improvements,
            'hint': hint,
            'raw_response': response
        }
        result["mode"] = evaluation_mode
        result["validity"] = validity
        if validity == "degraded":
            result["warning"] = "AI unavailable - heuristic scoring, not authoritative"
        return result

    def _display_result(self, todo_name: str, result: dict):
        """Display evaluation result with degraded mode warnings."""
        if result.get("validity") == "degraded":
            print(f"⚠ WARNING: {result['warning']}")
            print(f"  Grade {result['grade']}/10 is HEURISTIC — not valid for progression")

        # CRITICAL: degraded grades cannot unlock the next TODO
        if result.get("validity") == "degraded" and result.get("grade", 0) >= 8:
            result["status"] = "FAIL"
            result["blocked_reason"] = "degraded_evaluation"
            print(f"  Gate blocked: degraded evaluation cannot pass TODO #{todo_name}")

    def _generate_solution_hint(self, file_content: str, test_results: dict) -> str:
        """Generate a helpful hint for failing solution."""
        errors = test_results.get('errors', [])

        if 'index' in str(errors).lower():
            return "💡 Hint: Check your array indexing. Are you accessing out of bounds?"
        elif 'type' in str(errors).lower():
            return "💡 Hint: Check your variable types. Are you mixing strings and integers?"
        else:
            return "💡 Hint: Test your solution with the example inputs manually to find the issue."


def find_problem_file(problem_identifier: str = None) -> Optional[Path]:
    """Find the solution file to analyze."""
    if isinstance(problem_identifier, Path):
        problem_identifier = str(problem_identifier)

    def _list_solution_folders() -> list[Path]:
        project_items = CONTROLLER.list_directory(SOLUTIONS_ROOT)
        return [
            item for item in project_items if item.is_dir() and FOLDER_PATTERN.match(item.name)
        ]

    def _scan_folder_for_matches(folder: Path, matcher, batch_name: str) -> list:
        children = CONTROLLER.list_directory(folder)
        matches = []
        for child in children:
            if not child.is_file():
                continue
            match = matcher(child)
            if match is not None:
                matches.append(match)
        return matches

    solution_folders = _list_solution_folders()

    if problem_identifier is None:
        # Find most recently created/modified solution file
        def _latest_candidate(file_path: Path):
            if not file_path.name[0].isdigit() or file_path.name.startswith('_'):
                return None
            return (file_path, file_path.stat().st_mtime)

        folder_results = CONTROLLER.process_batch(
            solution_folders,
            lambda folder: _scan_folder_for_matches(folder, _latest_candidate, "latest-file"),
            batch_size=SCAN_BATCH_SIZE,
            pipeline="validation",
            flush_writes=False,
            file_operation=True,
            batch_name="latest-solution-folder",
        )
        solution_files = [candidate for matches in folder_results for candidate in matches]

        if not solution_files:
            return None

        # Return most recently modified
        return max(solution_files, key=lambda item: item[1])[0]

    if isinstance(problem_identifier, str) and problem_identifier.endswith('.py'):
        direct_candidate = Path(problem_identifier)
        candidate_paths = [direct_candidate]
        if not direct_candidate.is_absolute():
            candidate_paths.append(PROJECT_ROOT / direct_candidate)
            candidate_paths.append(Path.cwd() / direct_candidate)

        for candidate in candidate_paths:
            try:
                resolved = candidate.resolve()
            except OSError:
                continue
            if resolved.exists() and resolved.is_file():
                return resolved

    # If it's a number, find the file
    if problem_identifier.isdigit():
        problem_id = int(problem_identifier)

        def _match_problem_id(file_path: Path):
            return file_path if file_path.name.startswith(f"{problem_id}.") else None

        folder_results = CONTROLLER.process_batch(
            solution_folders,
            lambda folder: _scan_folder_for_matches(folder, _match_problem_id, "problem-id"),
            batch_size=SCAN_BATCH_SIZE,
            pipeline="validation",
            flush_writes=False,
            file_operation=True,
            batch_name="find-problem-id",
            stop_when=lambda result, *_: bool(result),
        )
        for matches in folder_results:
            if matches:
                return matches[0]

    # If it's a filename, try direct path
    if isinstance(problem_identifier, str) and '.py' in problem_identifier:
        def _match_filename(file_path: Path):
            return file_path if file_path.name == problem_identifier else None

        folder_results = CONTROLLER.process_batch(
            solution_folders,
            lambda folder: _scan_folder_for_matches(folder, _match_filename, "filename"),
            batch_size=SCAN_BATCH_SIZE,
            pipeline="validation",
            flush_writes=False,
            file_operation=True,
            batch_name="find-filename",
            stop_when=lambda result, *_: bool(result),
        )
        for matches in folder_results:
            if matches:
                return matches[0]

    return None


def extract_problem_data(file_content: str) -> dict:
    """Extract problem metadata for evaluation context."""
    data = {}

    # Extract problem number and title
    match = re.search(r'LeetCode\s+(\d+)\.\s+(.+)', file_content)
    if match:
        data['problem_number'] = int(match.group(1))
        data['title'] = match.group(2).strip()

    # Extract slug
    slug_match = re.search(r'Problem Slug:\s*(.+)', file_content)
    if slug_match:
        data['slug'] = slug_match.group(1).strip()

    # Extract URL
    url_match = re.search(r'LeetCode URL:\s*(.+)', file_content)
    if url_match:
        data['url'] = url_match.group(1).strip()

    return data


def run_test_cases(file_path: Path) -> dict:
    """Run the solution's test cases and return results."""
    try:
        test_env = os.environ.copy()
        test_env["LEETCODE_DOCTOR_FILE_MODE"] = "run-tests"
        test_env["PYTHONPATH"] = str(PROJECT_ROOT)

        # Execute the file and capture output
        result = CONTROLLER.run_subprocess(
            [sys.executable, str(file_path)],
            timeout=30,
            cwd=str(file_path.parent),
            env=test_env,
        )

        output = result.stdout.strip()
        errors = result.stderr.strip()

        # Basic test: did it run without errors?
        test_results = {
            'total': 1,
            'passed': 1 if not errors else 0,
            'failed': 0 if not errors else 1,
            'pass_rate': 1.0 if not errors else 0.0,
            'output': output,
            'errors': [errors] if errors else [],
            'exit_code': result.returncode
        }

        # TODO: Enhanced test extraction and validation
        # For now, we just check if the code runs
        # Later: parse test cases from file and validate each

        return test_results

    except subprocess.TimeoutExpired:
        return {
            'total': 1,
            'passed': 0,
            'failed': 1,
            'pass_rate': 0.0,
            'output': '',
            'errors': ['Execution timed out (30s limit)'],
            'exit_code': -1
        }
    except Exception as e:
        failure_type = classify_exception(e)
        return {
            'total': 1,
            'passed': 0,
            'failed': 1,
            'pass_rate': 0.0,
            'output': '',
            'errors': [f"{failure_type}: {str(e)}"],
            'exit_code': -1
        }


def load_doctor_config() -> dict:
    """Load doctor configuration."""
    config = CONTROLLER.read_json(DOCTOR_CONFIG_FILE, default=None)
    if config is not None:
        return config

    return {
        "ai_provider": "qwen",
        "qwen_model": "qwen-plus",
        "openai_model": "gpt-4",
        "ollama_model": "llama3",
        "claude_model": "claude-3-sonnet-20240229"
    }


def load_scoring_weights(config: dict) -> dict:
    """Load and validate scoring weights from doctor config.
    
    Gap 3 Fix: Validates that weights sum to 1.0 and are non-negative.
    Falls back to defaults if validation fails to prevent silent bad recommendations.
    """
    defaults = {"w1": 0.4, "w2": 0.3, "w3": 0.2, "w4": 0.1}
    weights = config.get("scoring_weights", defaults.copy())
    
    # Validate sum
    total = sum(weights.values())
    if abs(total - 1.0) > 0.01:
        print(f"Scoring weights sum to {total:.2f}, not 1.0. Using defaults.")
        return defaults.copy()
    
    # Validate non-negative
    if any(v < 0 for v in weights.values()):
        print("Negative scoring weight detected. Using defaults.")
        return defaults.copy()
    
    return weights


def save_doctor_config(config: dict):
    """Save doctor configuration."""
    CONTROLLER.ensure_directory(DOCTOR_CONFIG_FILE.parent)
    CONTROLLER.queue_json_write(DOCTOR_CONFIG_FILE, config, indent=2)
    CONTROLLER.commit(reason="doctor:save-config")


def load_doctor_tracking() -> dict:
    """Load doctor tracking data."""
    tracking = CONTROLLER.read_json(DOCTOR_TRACKING_FILE, default=None)
    if not isinstance(tracking, dict):
        return {"evaluations": {}}
    evaluations = tracking.get("evaluations")
    if not isinstance(evaluations, dict):
        tracking["evaluations"] = {}
    return tracking


def get_file_hash(file_path: Path) -> str:
    """Compute a stable file hash for tracking staleness."""
    return hashlib.md5(file_path.read_bytes()).hexdigest()


def save_doctor_tracking(tracking: dict):
    """Save doctor tracking data."""
    CONTROLLER.ensure_directory(DOCTOR_TRACKING_FILE.parent)
    CONTROLLER.queue_json_write(
        DOCTOR_TRACKING_FILE,
        tracking,
        indent=2,
        ensure_ascii=False,
    )
    CONTROLLER.commit(reason="doctor:save-tracking")


def add_inline_feedback(file_path: Path, todo_type: str, evaluation: dict):
    """Write feedback to CONSOLE only. Do NOT modify the solution file."""
    # Inline file modification disabled to prevent corruption of solution files.
    # All feedback is displayed in console output and tracked in doctor_tracking.json.
    pass

def evaluate_todo_in_sequence(file_path: Path, todo_index: int, ai_client: AIClient, tracking: dict) -> dict:
    """
    Evaluate a specific TODO in the sequence.
    Each TODO is tested INDEPENDENTLY - only analyzes that specific section.
    A TODO is only evaluated if all previous TODOs have passed.
    Returns evaluation result for this TODO only.
    """
    if todo_index >= len(TODO_ORDER):
        return {'error': 'All TODOs completed!'}

    todo_type = TODO_ORDER[todo_index]
    file_key = str(file_path.relative_to(PROJECT_ROOT))

    # CRITICAL: Check if all previous TODOs have passed
    # If any previous TODO hasn't passed, BLOCK evaluation
    if file_key in tracking.get('evaluations', {}):
        file_evals = tracking['evaluations'][file_key]
        for i in range(todo_index):
            prev_todo = TODO_ORDER[i]
            if prev_todo not in file_evals or file_evals[prev_todo].get('status') != 'PASS':
                return {
                    'error': 'BLOCKED',
                    'blocked_by': prev_todo,
                    'message': f'Cannot evaluate "{todo_type}" because "{prev_todo}" has not passed yet. Fix "{prev_todo}" first!'
                }

    # Check if this TODO was already passed in previous session
    if file_key in tracking.get('evaluations', {}):
        prev_eval = tracking['evaluations'][file_key]
        if todo_type in prev_eval and prev_eval[todo_type].get('status') == 'PASS':
            return {
                'status': 'ALREADY_PASSED',
                'todo_type': todo_type,
                'todo_index': todo_index,
                'grade': prev_eval[todo_type]['grade'],
                'message': f'{todo_type.replace("_", " ").title()} - Already passed! (Grade: {prev_eval[todo_type]["grade"]:.1f}/10)'
            }

    # Load file content for THIS TODO ONLY
    file_content = CONTROLLER.read_text(file_path, encoding='utf-8', default='')

    # Check if this is an old-format file
    if is_old_format_file(file_content):
        print(f"\n{'=' * 60}")
        print(f"⚠️  OLD FORMAT DETECTED")
        print(f"{'=' * 60}")
        print(f"File: {file_path.name}")
        print(f"\nThis file uses the old format (no TODO structure).")
        print(f"The Doctor cannot evaluate it in its current form.\n")
        print(f"Would you like to redo this problem in the new format?")
        print(f"The system will:")
        print(f"  1. Back up your current solution as .py.old")
        print(f"  2. Create a fresh TODO template with problem statement")
        print(f"  3. Let you fill in the TODOs properly\n")

        try:
            response = input("Redo this problem in new format? (yes/no): ").strip().lower()

            if response in ['yes', 'y']:
                print(f"\n🔄 Converting to new format...")
                success = regenerate_as_new_format(file_path)

                if success:
                    print(f"\n✅ Conversion successful!")
                    print(f"Run the Doctor again when you've filled in the TODOs.")
                    return {'status': 'converted', 'message': 'File converted to new format'}
                else:
                    print(f"\n❌ Conversion failed. Please contact support.")
                    return {'status': 'error', 'message': 'Conversion failed'}
            else:
                print(f"\n👍 No problem! Move on to a different problem.")
                print(f"Run the suggestor to get a new suggestion with the TODO format.")
                return {'status': 'skipped', 'message': 'User chose to skip old-format file'}
        except (KeyboardInterrupt, EOFError):
            print(f"\n\n⚠️  Cancelled.")
            return {'status': 'cancelled', 'message': 'User cancelled'}

    # Extract ONLY this TODO's section for independent evaluation
    section_content = extract_todo_section(file_content, todo_type)

    # ============================================================
    # Fix #2 — Pre-evaluation validation gate
    # ============================================================
    # STOP evaluation immediately if file is structurally invalid.
    # No grading allowed on invalid input.
    def _validate_file_state():
        validation_errors = []

        if len(file_content) == 0:
            validation_errors.append((FailureReason.SCHEMA_INVALID, 'File is empty (0 bytes)'))
        elif len(file_content) < 50:
            validation_errors.append((FailureReason.SCHEMA_INVALID, f'File suspiciously short ({len(file_content)} bytes)'))

        if 'PROBLEM STATEMENT:' not in file_content:
            validation_errors.append((FailureReason.SCHEMA_INVALID, 'Missing PROBLEM STATEMENT section'))

        if 'class Solution:' not in file_content:
            validation_errors.append((FailureReason.SCHEMA_INVALID, 'Missing class Solution definition'))

        ps_match = re.search(
            r'PROBLEM STATEMENT:.*?={5,}\n(.*?)(?=\n={5,}|DIFFICULTY:)',
            file_content,
            re.DOTALL,
        )
        if ps_match:
            ps_content = ps_match.group(1).strip()
            if len(ps_content) == 0:
                validation_errors.append((FailureReason.INCOMPLETE_DATA, 'Problem statement section is empty'))
            elif 'Could not auto-fetch' in ps_content or 'Unable to auto-fetch' in ps_content or '[Add problem statement' in ps_content:
                validation_errors.append((FailureReason.INCOMPLETE_DATA, 'Problem statement is a placeholder (not fetched)'))
            elif 'You are given' not in ps_content and 'Given ' not in ps_content and 'Return' not in ps_content:
                validation_errors.append((FailureReason.INCOMPLETE_DATA, 'Problem statement lacks problem description keywords'))

        if 'TODO WORKFLOW' not in file_content and 'TODO #1' not in file_content:
            validation_errors.append((FailureReason.SCHEMA_INVALID, 'Missing TODO workflow structure'))

        if section_content.strip() == '' and todo_type != 'solution':
            validation_errors.append((FailureReason.INCOMPLETE_DATA, f'Extracted section for {todo_type} is empty'))

        return validation_errors

    validation_errors = CONTROLLER.validate_batch(
        f"doctor-file-validation:{file_path.name}:{todo_type}",
        _validate_file_state,
    )

    if validation_errors:
        reasons = '; '.join(f'{reason}: {detail}' for reason, detail in validation_errors)
        print(f"\n{'=' * 60}")
        print(f"🚫 INVALID FILE STATE — Evaluation stopped")
        print(f"{'=' * 60}")
        for reason, detail in validation_errors:
            print(f"  ❌ {reason}: {detail}")
        print(f"\nFix the issues above before running the Doctor again.")
        return {
            'status': 'INVALID_FILE_STATE',
            'errors': validation_errors,
            'reason': reasons
        }

    # Extract problem data
    problem_data = extract_problem_data(file_content)

    # Evaluate this TODO INDEPENDENTLY using only its section
    evaluator = DoctorEvaluation(ai_client)

    if todo_type == 'problem_statement':
        result = evaluator.evaluate_problem_statement(section_content, problem_data)
    elif todo_type == 'approach':
        result = evaluator.evaluate_approach(section_content)
    elif todo_type == 'complexity':
        result = evaluator.evaluate_complexity(section_content)
    elif todo_type == 'solution':
        # Run tests first (independent of other TODOs)
        test_results = run_test_cases(file_path)
        result = evaluator.evaluate_solution(section_content, test_results)
    elif todo_type == 'test_cases':
        result = evaluator.evaluate_test_cases(section_content)
    else:
        result = {'grade': 0, 'status': 'FAIL', 'feedback': 'Unknown TODO type'}

    # Display result with degraded mode warnings
    evaluator._display_result(TODO_NAMES[todo_index], result)

    # Determine if passed based on TODO type
    if todo_type == 'solution':
        is_passed = result['grade'] >= PASSING_GRADE_SOLUTION * 10  # 100%
    else:
        is_passed = result['grade'] >= PASSING_GRADE_DOCS

    # Critical gate rule: degraded/rule_based evaluations can never pass a TODO.
    if result.get('validity') == 'degraded':
        if result.get('grade', 0) >= PASSING_GRADE_DOCS:
            result['blocked_reason'] = 'degraded_evaluation'
        result['status'] = 'FAIL'
        is_passed = False

    result['is_passed'] = is_passed
    result['todo_type'] = todo_type
    result['todo_index'] = todo_index

    # Add inline feedback ONLY for this TODO
    if not is_passed:
        add_inline_feedback(file_path, todo_type, result)

    # Update tracking for THIS TODO ONLY
    if file_key not in tracking.setdefault('evaluations', {}):
        tracking['evaluations'][file_key] = {}
    tracking['evaluations'][file_key]['file_hash'] = get_file_hash(file_path)

    tracking['evaluations'][file_key][todo_type] = {
        'grade': result['grade'],
        'status': result['status'],
        'mode': result.get('mode', 'unknown'),
        'validity': result.get('validity', 'unknown'),
        'is_passed': is_passed,
        'attempts': tracking['evaluations'][file_key].get(todo_type, {}).get('attempts', 0) + 1,
        'timestamp': datetime.now().isoformat()
    }

    save_doctor_tracking(tracking)

    return result


def extract_todo_section(file_content: str, todo_type: str) -> str:
    """
    Extract ONLY the specific TODO section from the file.
    Each TODO is evaluated INDEPENDENTLY with only its own content.
    """
    if todo_type == 'problem_statement':
        # Extract PROBLEM STATEMENT section only
        match = re.search(
            r'PROBLEM STATEMENT:\s*\n={5,}\n(.*?)(?=\n={5,}\n|\nDIFFICULTY:|\nAPPROACH:)',
            file_content, re.DOTALL
        )
        return match.group(1).strip() if match else ""

    elif todo_type == 'approach':
        # Extract APPROACH section only — stop at the next separator or TODO #3
        match = re.search(
            r'APPROACH:\s*\n(.*?)(?=\n={10,}|\nTODO\s*#?3|\nTime Complexity:)',
            file_content, re.DOTALL
        )
        if match:
            # Clean up: remove trailing separator lines
            text = match.group(1).strip()
            # Remove any trailing === lines
            text = re.sub(r'\n={5,}.*$', '', text).strip()
            return text
        return ""

    elif todo_type == 'complexity':
        # Extract complexity lines only
        match = re.search(
            r'(Time Complexity:.*?\nSpace Complexity:.*?)(?:\n|\Z)',
            file_content, re.DOTALL
        )
        return match.group(1).strip() if match else ""

    elif todo_type == 'solution':
        # Extract the Solution class and solve method only
        match = re.search(
            r'class Solution:.*?(?=\n# Test cases|\nif __name__)',
            file_content, re.DOTALL
        )
        return match.group(0).strip() if match else ""

    elif todo_type == 'test_cases':
        # Extract test cases section only
        match = re.search(
            r'# Test cases.*?$',
            file_content, re.DOTALL
        )
        return match.group(0).strip() if match else ""

    return ""


def display_evaluation(result: dict, todo_index: int):
    """Display evaluation results to user."""
    todo_name = TODO_NAMES[todo_index] if todo_index < len(TODO_NAMES) else 'Unknown'

    print(f"\n{'=' * 70}")
    print(f"👨‍⚕️ DOCTOR EVALUATION: {todo_name}")
    print(f"{'=' * 70}")

    if 'error' in result:
        print(f"✅ {result['error']}")
        return

    grade = result.get('grade', 0)
    status = result.get('status', 'FAIL')
    feedback = result.get('feedback', '')
    improvements = result.get('improvements', '')
    hint = result.get('hint')

    if result.get("validity") == "degraded":
        print(f"⚠ WARNING: {result.get('warning', 'AI unavailable - heuristic scoring, not authoritative')}")
        print(f"  Grade {grade:.1f}/10 is HEURISTIC - not valid for progression")
        if grade >= 8:
            print(f"  Gate blocked: degraded evaluation cannot pass TODO #{todo_name}")

    # Grade bar
    if grade >= 8:
        grade_bar = "🟢" * int(grade) + "⚪" * (10 - int(grade))
    elif grade >= 5:
        grade_bar = "🟡" * int(grade) + "⚪" * (10 - int(grade))
    else:
        grade_bar = "🔴" * int(grade) + "⚪" * (10 - int(grade))

    print(f"Grade: {grade_bar} ({grade:.1f}/10)")
    print(f"Status: {status}")
    print(f"\n📝 Feedback:")
    print(f"  {feedback}")

    if improvements and status == 'FAIL':
        print(f"\n🔧 Improvements needed:")
        if isinstance(improvements, list):
            for line in improvements:
                print(f"  {line}")
        else:
            for line in improvements.split('\n'):
                print(f"  {line}")

    if hint:
        print(f"\n💡 Hint:")
        print(f"  {hint}")

    if status == 'PASS' or result.get('is_passed'):
        print(f"\n✅ {todo_name} PASSED! Moving to next TODO...")
    else:
        attempts = result.get('attempts', 1)
        print(f"\n❌ {todo_name} needs more work (Attempt #{attempts})")

        if attempts >= MAX_HINT_ATTEMPTS:
            print(f"\n⚠️  You've tried {attempts} times.")
            print(f"Would you like to see the solution? (y/n)")
            try:
                response = input("> ").strip().lower()
                if response in ['y', 'yes']:
                    print(f"\n💊 SOLUTION REVEALED:")
                    print(f"  [Solution would be shown here - implement this based on problem]")
            except:
                pass


def run_doctor(problem_identifier: str = None, mode: str = 'analyze'):
    """Main doctor function - evaluates TODOs in order, one at a time."""
    print("=" * 70)
    print("👨‍⚕️ LeetCode Doctor - AI-Powered Code Reviewer")
    print("=" * 70)

    # Find the file to analyze
    file_path = find_problem_file(problem_identifier)

    if not file_path:
        print("\n✗ No solution file found!")
        print("Run leetcode_suggestor.py first to create a problem file.")
        return

    print(f"\n📄 Analyzing: {file_path.name}")
    print(f"   Location: {file_path.relative_to(PROJECT_ROOT)}\n")

    # Initialize AI
    ai_client = AIClient()

    # Load tracking
    tracking = load_doctor_tracking()
    file_key = str(file_path.relative_to(PROJECT_ROOT))
    current_hash = get_file_hash(file_path)
    file_tracking = tracking.setdefault("evaluations", {}).get(file_key)
    if file_tracking and file_tracking.get("file_hash") != current_hash:
        # File changed since previous evaluation; invalidate stale TODO states.
        tracking["evaluations"][file_key] = {"file_hash": current_hash}
        save_doctor_tracking(tracking)
    elif file_tracking is None:
        tracking["evaluations"][file_key] = {"file_hash": current_hash}
        save_doctor_tracking(tracking)

    if mode == 'analyze':
        # Determine which TODO to evaluate
        file_evals = tracking.get('evaluations', {}).get(file_key, {})

        # Find FIRST TODO that hasn't passed (enforces order)
        next_todo_index = None
        for i, todo_type in enumerate(TODO_ORDER):
            if todo_type not in file_evals or file_evals[todo_type].get('status') != 'PASS':
                next_todo_index = i
                break

        # If all TODOs passed
        if next_todo_index is None:
            print("🎉 All TODOs passed! This solution is complete!")
            print("\nYou can now:")
            print("  • Move on to the next problem")
            print("  • Run leetcode_suggestor.py for a new suggestion")
            return

        next_todo_type = TODO_ORDER[next_todo_index]
        next_todo_name = TODO_NAMES[next_todo_index]

        print(f"📋 Evaluating TODO #{next_todo_index + 1}: {next_todo_name}")
        print(f"   (TODOs must be passed in order)\n")

        # Check if blocked by previous TODO
        if next_todo_index > 0:
            prev_todo_type = TODO_ORDER[next_todo_index - 1]
            prev_todo_name = TODO_NAMES[next_todo_index - 1]
            if prev_todo_type in file_evals and file_evals[prev_todo_type].get('status') != 'PASS':
                print(f"🔒 BLOCKED!")
                print(f"   Cannot evaluate '{next_todo_name}' yet.")
                print(f"   You must pass '{prev_todo_name}' first.\n")
                print(f"   Current status of '{prev_todo_name}':")
                prev_grade = file_evals[prev_todo_type].get('grade', 0)
                prev_attempts = file_evals[prev_todo_type].get('attempts', 0)
                print(f"   Grade: {prev_grade:.1f}/10 | Attempts: {prev_attempts}")
                return

        # Evaluate this TODO (and ONLY this TODO)
        result = evaluate_todo_in_sequence(file_path, next_todo_index, ai_client, tracking)

        # Display result
        if 'error' in result:
            if result['error'] == 'BLOCKED':
                blocked_by = result.get('blocked_by', 'unknown')
                blocked_name = TODO_NAMES[TODO_ORDER.index(blocked_by)] if blocked_by in TODO_ORDER else blocked_by
                print(f"🔒 BLOCKED!")
                print(f"   Cannot evaluate '{next_todo_name}' because '{blocked_name}' has not passed.")
                print(f"   Fix '{blocked_name}' first!\n")

                # Show status of blocking TODO
                if blocked_by in file_evals:
                    blocked_grade = file_evals[blocked_by].get('grade', 0)
                    blocked_attempts = file_evals[blocked_by].get('attempts', 0)
                    print(f"   Status of '{blocked_name}':")
                    print(f"   Grade: {blocked_grade:.1f}/10 | Attempts: {blocked_attempts}")
                    print(f"   Need: 8.0/10 to pass")
            else:
                print(f"⚠️ {result['error']}")
        elif result.get('status') == 'ALREADY_PASSED':
            print(f"✅ {result.get('message', 'TODO already passed')}")
            print(f"\n   Moving to next TODO...")
        else:
            display_evaluation(result, next_todo_index)

    elif mode == 'show-solution':
        print("\n💊 Showing solution...")
        print("Solution display not yet implemented")

    elif mode == 'reset':
        file_key = str(file_path.relative_to(PROJECT_ROOT))
        if file_key in tracking.get('evaluations', {}):
            del tracking['evaluations'][file_key]
            save_doctor_tracking(tracking)
            print(f"✓ Reset evaluation history for {file_path.name}")
        else:
            print(f"No evaluation history for {file_path.name}")


def is_old_format_file(file_content: str) -> bool:
    """Detect if a file uses the old format (no TODO structure)."""
    # Old format files lack the TODO workflow markers
    has_todo_workflow = 'TODO WORKFLOW' in file_content or 'TODO #1' in file_content or 'TODO #2' in file_content
    has_todo_sections = 'TODO #2' in file_content and 'TODO #3' in file_content

    # Old format typically has class Solution but no TODO markers
    has_solution_class = 'class Solution:' in file_content
    no_todo_structure = not has_todo_workflow and not has_todo_sections

    return has_solution_class and no_todo_structure


def regenerate_as_new_format(file_path: Path) -> bool:
    """Regenerate an old-format file into the new TODO-based format."""
    try:
        # Extract problem number and title from filename
        filename = file_path.name
        match = re.match(r'(\d+)\.\s+(.+)\.py', filename)

        if not match:
            print(f"⚠ Cannot extract problem number from filename: {filename}")
            return False

        problem_id = int(match.group(1))
        problem_title = match.group(2)

        print(f"\n{'=' * 60}")
        print(f"🔄 REGENERATING FILE IN NEW FORMAT")
        print(f"{'=' * 60}")
        print(f"Problem: {problem_id}. {problem_title}")
        print(f"{'=' * 60}")

        # Try to fetch the problem statement from LeetCode
        print(f"\nFetching problem statement from LeetCode...")

        # Strategy 1: Try to extract slug from existing file
        original_content = CONTROLLER.read_text(file_path, encoding='utf-8', default='') or ''
        slug_match = re.search(r'leetcode\.com/problems/([^/]+)', original_content)

        problem_stmt = None
        title_slug = None
        problem_info = None

        if slug_match:
            title_slug = slug_match.group(1)
            problem_stmt = fetch_problem_statement(title_slug)

        # Strategy 2: Use ZeroTrac or local mapping to look up by problem number
        if not problem_stmt:
            print(f"  Not found in file, looking up problem #{problem_id}...")
            problem_info = get_problem_slug_by_id(problem_id)

            if problem_info:
                title_slug = problem_info['title_slug']
                print(f"  Found: {title_slug}")
                problem_stmt = fetch_problem_statement(title_slug)
            else:
                print(f"  ⚠ Could not find problem #{problem_id} in any database")

        backup_path = file_path.with_suffix('.py.old')
        CONTROLLER.queue_text_write(backup_path, original_content)

        # Create new content with TODO structure
        folder = get_folder_for_problem(problem_id)

        # Get rating - only for problems in ZeroTrac range (746+)
        rating_str = "N/A"
        if problem_id >= 746:
            try:
                ratings = fetch_ratings()
                rating_results = CONTROLLER.process_batch(
                    list(chunk_items(ratings, RATING_CHUNK_SIZE)),
                    lambda rating_chunk: [
                        f"{problem['rating']:.2f} (ZeroTrac)"
                        for problem in rating_chunk
                        if problem['id'] == problem_id
                    ],
                    batch_size=SCAN_BATCH_SIZE,
                    pipeline="validation",
                    flush_writes=False,
                    file_operation=False,
                    batch_name="lookup-problem-rating",
                    stop_when=lambda result, *_: bool(result),
                )
                for rating in rating_results:
                    if rating:
                        rating_str = rating[0]
                        break
            except:
                pass

        if problem_stmt:
            clean_content = clean_html_content(problem_stmt['content'])
            topics_str = ", ".join([tag['name'] for tag in problem_stmt['topics']]) if problem_stmt['topics'] else "None"

            statement_section = f"""
PROBLEM STATEMENT:
{'=' * 60}
{clean_content}

DIFFICULTY: {problem_stmt['difficulty']}
LIKES: {problem_stmt['likes']} | DISLIKES: {problem_stmt['dislikes']}
TOPICS: {topics_str}
"""
        else:
            leetcode_link = f"https://leetcode.com/problems/{title_slug}/" if title_slug else f"https://leetcode.com/problemset/all/"
            statement_section = f"""
PROBLEM STATEMENT:
{'=' * 60}

⚠️  Could not auto-fetch problem statement.
📎 Add it manually from: {leetcode_link}

"""

        leetcode_url = f"https://leetcode.com/problems/{title_slug}/" if title_slug else "N/A"
        contest_str = problem_info.get('contest_slug', 'N/A') if problem_info else 'N/A'
        index_str = problem_info.get('problem_index', 'N/A') if problem_info else 'N/A'
        title_zh = problem_info.get('title_zh', 'N/A') if problem_info else 'N/A'

        content = f'''"""
LeetCode {problem_id}. {problem_title}
{'=' * 60}

Problem Number: {problem_id}
Difficulty Rating: {rating_str}
Contest: {contest_str}
Problem Index: {index_str}

LeetCode URL: {leetcode_url}

Problem Slug: {title_slug or 'N/A'}
Chinese Title: {title_zh}
{statement_section}

{'=' * 60}
TODO WORKFLOW - Complete in Order (1 → 2 → 3 → 4):
{'=' * 60}
TODO #1 — PROBLEM STATEMENT      [Review auto-generated content above]
TODO #2 — APPROACH                [Describe your algorithm step-by-step]
TODO #3 — COMPLEXITY              [State Time/Space complexity with reasoning]
TODO #4 — SOLUTION + TESTS        [Implement solution + comprehensive test cases]
{'=' * 60}

Progress: Run this file directly to call the Doctor for this TODO workflow
          Alternative: `python leetcode_doctor.py {problem_id}`
          Must pass in order: #1 -> #2 -> #3 -> #4
          Each requires >=8/10 to pass (except #4 needs 100% test pass)

{'=' * 60}
TODO #2 — APPROACH:
TODO: Replace this line with your algorithm description.
      Explain step-by-step how you will solve this problem.
      Example: "I will use a hash map to store..." or "This is a sliding window problem where..."

{'=' * 60}
TODO #3 — COMPLEXITY:
Time Complexity: O(?)  — replace with actual complexity (e.g., O(n log n))
Space Complexity: O(?) — replace with actual complexity (e.g., O(n) for hash map)
"""

from typing import List, Optional
import heapq
from collections import defaultdict, deque


class Solution:
    @staticmethod
    def solve() -> None:
        """
        TODO #4a — Implement the solution for {problem_title}

        Args:
            TODO: Add parameters based on the problem statement

        Returns:
            TODO: Add return type based on the problem statement
        """
        # TODO: Implement your solution here
        pass


# ============================================================
# TODO #4b — Test Cases (add from LeetCode examples + edge cases)
# ============================================================
def _run_embedded_tests() -> None:
    solution = Solution()

    # Example 1:
    # Input: TODO
    # Expected: TODO

    # Example 2:
    # Input: TODO
    # Expected: TODO

    # Edge case:
    # Input: TODO
    # Expected: TODO

    result = solution.solve()
    print(f"Result: {{result}}")


if __name__ == '__main__':
    from pathlib import Path
    import sys

    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    from doctor_runtime import run_doctor_or_embedded_tests

    raise SystemExit(run_doctor_or_embedded_tests(__file__, _run_embedded_tests))
'''

        required_markers = ['TODO WORKFLOW', 'TODO #1', 'TODO #2', 'TODO #3', 'TODO #4']
        CONTROLLER.queue_text_write(
            file_path,
            content,
            required_markers=required_markers,
        )
        try:
            CONTROLLER.commit(reason=f"doctor:regenerate:{file_path.name}")
            success = True
        except Exception:
            CONTROLLER.io_manager.clear()
            success = False

        if success:
            print(f"✓ Backed up old file to: {backup_path.name}")
            print(f"✓ Regenerated file with TODO structure: {filename}")
            print(f"\n{'=' * 60}")
            print(f"✅ Conversion complete!")
            print(f"{'=' * 60}")
            print(f"\nNext steps:")
            print(f"  1. Open the file in your editor")
            print(f"  2. Fill in TODOs #2, #3, and #4")
            print(f"  3. Run the Doctor when ready: python leetcode_doctor.py {problem_id}")
            print(f"\nYour old solution is backed up at: {backup_path.name}")

            return True
        else:
            print(f"\n❌ File write failed validation — changes not committed.")
            print(f"Your original file is untouched.")
            print(f"Backup is at: {backup_path}")
            return False

    except Exception as e:
        failure_type = classify_exception(e)
        print(f"\n❌ Unexpected error during conversion ({failure_type}): {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Entry point."""
    mode = 'analyze'
    problem_id = None

    args = sys.argv[1:]

    if not args:
        # No arguments - analyze most recent file
        pass
    elif args[0] in ['--help', '-h']:
        print(__doc__)
        return
    elif args[0] == '--show-solution':
        mode = 'show-solution'
        if len(args) > 1:
            problem_id = args[1]
    elif args[0] == '--reset':
        mode = 'reset'
        if len(args) > 1:
            problem_id = args[1]
    elif args[0] == '--all':
        print("Analyzing all files... (not yet implemented)")
        return
    else:
        # First argument is problem ID or filename
        problem_id = args[0]

    try:
        CONTROLLER.run_entrypoint(
            "leetcode_doctor",
            lambda: run_doctor(problem_id, mode),
        )
    except ExecutionControlError as exc:
        print(f"\nControlled execution stopped: {exc}")
        sys.exit(1)


if __name__ == '__main__':
    main()
