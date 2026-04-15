"""3-probe variance check v2 — using logprobs as real confidence signal."""
import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral"

THREE_PROBES = [
    # Probe 1: Clearly correct solution
    {
        "label": "correct",
        "problem": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
        "code": (
            "def twoSum(nums, target):\n"
            "    seen = {}\n"
            "    for i, n in enumerate(nums):\n"
            "        complement = target - n\n"
            "        if complement in seen:\n"
            "            return [seen[complement], i]\n"
            "        seen[n] = i\n"
            "    return []"
        ),
    },
    # Probe 2: Clearly incorrect solution
    {
        "label": "incorrect",
        "problem": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
        "code": (
            "def twoSum(nums, target):\n"
            "    for i in range(len(nums)):\n"
            "        if nums[i] + nums[i] == target:\n"
            "            return [i, i]\n"
            "    return []"
        ),
    },
    # Probe 3: Partial solution (brute force O(n^2))
    {
        "label": "partial",
        "problem": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
        "code": (
            "def twoSum(nums, target):\n"
            "    for i in range(len(nums)):\n"
            "        for j in range(i + 1, len(nums)):\n"
            "            if nums[i] + nums[j] == target:\n"
            "                return [i, j]\n"
            "    return []"
        ),
    },
]

PROMPT_TEMPLATE = """You are evaluating a LeetCode solution.

Problem:
{problem_text}

Code:
{solution_code}

Classify as correct, partial, or incorrect.
Output JSON only:
{{"verdict": "correct|partial|incorrect", "confidence": 0.0-1.0, "reasoning": "one sentence"}}"""


def _extract_json(raw):
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    start = raw.find("{")
    end = raw.rfind("}")
    if start >= 0 and end > start:
        try:
            return json.loads(raw[start:end + 1])
        except json.JSONDecodeError:
            pass
    return {"verdict": "incorrect", "confidence": 0.5, "reasoning": f"parse fail"}


def compute_logprob_confidence(logprobs):
    """Derive confidence from token logprobs.
    
    Two signals:
    1. Mean logprob of response tokens (lower = more uncertain)
    2. Variance of logprobs (high variance = mixed certainty)
    
    We use: confidence = exp(mean_logprob) — maps [-inf, 0] -> [0, 1]
    This is the geometric mean of token probabilities.
    """
    import math
    if not logprobs:
        return 0.0
    
    logprobs_vals = [lp["logprob"] for lp in logprobs]
    mean_lp = sum(logprobs_vals) / len(logprobs_vals)
    variance = sum((x - mean_lp) ** 2 for x in logprobs_vals) / len(logprobs_vals)
    
    # Geometric mean probability
    confidence = math.exp(mean_lp)
    
    return confidence, mean_lp, math.sqrt(variance)


def main():
    print("=" * 70)
    print("3-PROBE CONFIDENCE VARIANCE CHECK v2 (logprobs)")
    print("=" * 70)

    results = []
    for i, probe in enumerate(THREE_PROBES, 1):
        prompt = PROMPT_TEMPLATE.format(problem_text=probe["problem"], solution_code=probe["code"])
        print(f"\nProbe {i} ({probe['label']}): ", end="", flush=True)

        resp = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "logprobs": True,
            "options": {"temperature": 0, "num_predict": 512}
        }, timeout=300)

        data = resp.json()
        raw = data["response"].strip()
        parsed = _extract_json(raw)
        logprobs = data.get("logprobs", [])
        
        conf_geo, mean_lp, std_lp = compute_logprob_confidence(logprobs)
        verdict = parsed.get("verdict", "unknown")
        results.append((probe["label"], verdict, conf_geo, mean_lp, std_lp))

        print(f"verdict={verdict}")
        print(f"  self_reported_conf={parsed.get('confidence', 'N/A')}")
        print(f"  logprob_confidence={conf_geo:.4f}")
        print(f"  mean_logprob={mean_lp:.4f}")
        print(f"  std_logprob={std_lp:.4f}")
        print(f"  reasoning: {parsed.get('reasoning', 'N/A')[:100]}")

    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    for gt, verdict, conf, mean_lp, std_lp in results:
        print(f"  GT={gt:<10} → verdict={verdict:<10} logprob_conf={conf:.4f}  mean_lp={mean_lp:.4f}  std={std_lp:.4f}")

    confs = [r[2] for r in results]
    range_val = max(confs) - min(confs)
    print(f"\nLogprob confidence range: {range_val:.4f}")
    
    if range_val < 0.01:
        print("⚠ FLAT — logprob confidence is constant. Experiment INVALID.")
    else:
        print(f"✓ VARIANCE DETECTED (range={range_val:.4f}). Experiment is VALID.")


if __name__ == "__main__":
    main()
