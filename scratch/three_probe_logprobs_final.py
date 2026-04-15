"""Final 3-probe check — verdict confidence from logprobs with subword handling."""
import json
import math
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral"

THREE_PROBES = [
    {
        "label": "correct",
        "expected_verdict": "correct",
        "problem": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
        "code": "def twoSum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        complement = target - n\n        if complement in seen:\n            return [seen[complement], i]\n        seen[n] = i\n    return []",
    },
    {
        "label": "incorrect",
        "expected_verdict": "incorrect",
        "problem": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
        "code": "def twoSum(nums, target):\n    for i in range(len(nums)):\n        if nums[i] + nums[i] == target:\n            return [i, i]\n    return []",
    },
    {
        "label": "partial",
        "expected_verdict": "partial",
        "problem": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
        "code": "def twoSum(nums, target):\n    for i in range(len(nums)):\n        for j in range(i + 1, len(nums)):\n            if nums[i] + nums[j] == target:\n                return [i, j]\n    return []",
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


def extract_verdict_confidence(logprobs, response_text):
    """Extract the actual verdict and its token probability from logprobs.
    
    Handles subword tokenization (e.g., 'incorrect' = 'inc' + 'or' + 'rect').
    Uses the first token of the verdict value after '"verdict": "'.
    """
    # Parse actual verdict from response
    try:
        parsed = json.loads(response_text)
        actual_verdict = parsed.get("verdict", "unknown")
    except:
        actual_verdict = "parse_error"
    
    # Find position after '"verdict": "' in the token stream
    # The first token after this pattern is the verdict value start
    found_verdict_key = False
    verdict_first_token = None
    verdict_first_logprob = None
    
    for i, lp in enumerate(logprobs):
        token_stripped = lp["token"].strip().strip('"')
        
        if token_stripped.lower() == "verdict":
            found_verdict_key = True
            continue
        
        if found_verdict_key and verdict_first_token is None:
            # This should be the first token of the verdict value
            verdict_first_token = lp["token"]
            verdict_first_logprob = lp["logprob"]
            break
    
    if verdict_first_logprob is not None:
        confidence = math.exp(verdict_first_logprob)
    else:
        confidence = None
    
    return actual_verdict, confidence, verdict_first_token, verdict_first_logprob


def main():
    print("=" * 70)
    print("3-PROBE CHECK — Verdict confidence from logprobs")
    print(f"Model: {MODEL}")
    print("=" * 70)

    results = []
    for i, probe in enumerate(THREE_PROBES, 1):
        prompt = PROMPT_TEMPLATE.format(problem_text=probe["problem"], solution_code=probe["code"])
        print(f"\nProbe {i} (GT={probe['label']}): ", end="", flush=True)

        resp = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "logprobs": True,
            "options": {"temperature": 0, "num_predict": 512}
        }, timeout=300)

        data = resp.json()
        raw = data["response"].strip()
        logprobs = data.get("logprobs", [])
        
        actual_verdict, conf, first_token, first_lp = extract_verdict_confidence(logprobs, raw)
        
        results.append((probe["label"], probe["expected_verdict"], actual_verdict, conf, first_token, first_lp))
        
        verdict_correct = (actual_verdict == probe["expected_verdict"])
        print(f"expected={probe['expected_verdict']}, actual={actual_verdict}, correct={verdict_correct}")
        if conf is not None:
            print(f"  verdict_first_token={repr(first_token)}, P(verdict)={conf:.4f}, logprob={first_lp:.4f}")
        else:
            print(f"  verdict token NOT FOUND in logprobs")

    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    confidences = []
    for gt, expected, actual, conf, token, lp in results:
        verdict_match = "✓" if actual == expected else "✗"
        if conf is not None:
            print(f"  GT={gt:<10}: verdict={actual:<12} {verdict_match}  P(verdict)={conf:.4f}")
            confidences.append(conf)
        else:
            print(f"  GT={gt:<10}: verdict={actual:<12} {verdict_match}  P(verdict)=N/A")

    if len(confidences) >= 2:
        conf_range = max(confidences) - min(confidences)
        print(f"\nConfidence range: {conf_range:.4f}")
        if conf_range < 0.01:
            print("⚠ FLAT — confidence barely varies. Signal is too weak to use.")
        elif conf_range < 0.1:
            print("~ Weak signal — confidence varies slightly. May need more probes to confirm.")
        else:
            print("✓ Meaningful variance — confidence signal is usable.")


if __name__ == "__main__":
    main()
