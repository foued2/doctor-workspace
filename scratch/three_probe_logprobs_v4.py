"""3-probe logprobs check — verdict confidence extracted correctly."""
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
    """Extract verdict confidence by finding the token after '\"verdict\": \"'.
    
    Tokenization pattern observed: 'ver'+'dict'+'":'+' "' + **VERDICT_TOKEN**
    The verdict token is the first token after ' "' that follows 'dict'.
    """
    try:
        parsed = json.loads(response_text)
        actual_verdict = parsed.get("verdict", "unknown")
    except:
        actual_verdict = "parse_error"
    
    # Find 'dict' token (second half of 'verdict'), then skip '":' and ' "' to get value
    verdict_token = None
    verdict_logprob = None
    
    for i, lp in enumerate(logprobs):
        if lp["token"].strip() == "dict" and i + 3 < len(logprobs):
            # Pattern: 'dict' -> '":' -> ' "' -> VERDICT
            # But sometimes there's no ' "' token, verdict comes right after '":'
            # Check tokens after 'dict'
            for j in range(i + 1, min(i + 4, len(logprobs))):
                t = logprobs[j]["token"].strip().strip('"')
                if t.lower() in ("correct", "incorrect", "partial"):
                    verdict_token = logprobs[j]["token"]
                    verdict_logprob = logprobs[j]["logprob"]
                    break
            if verdict_logprob is not None:
                break
    
    # Fallback: reconstruct from response text
    if verdict_token is None and actual_verdict != "parse_error":
        # Find first token whose text starts with the verdict word
        for lp in logprobs:
            t = lp["token"].strip().strip('"')
            if t.lower().startswith(actual_verdict.lower()[:3]):
                verdict_token = lp["token"]
                verdict_logprob = lp["logprob"]
                break
    
    confidence = math.exp(verdict_logprob) if verdict_logprob is not None else None
    return actual_verdict, confidence, verdict_token, verdict_logprob


def main():
    print("=" * 70)
    print(f"3-PROBE CHECK — Verdict confidence from logprobs ({MODEL})")
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
        
        actual_verdict, conf, token, lp = extract_verdict_confidence(logprobs, raw)
        verdict_ok = "✓" if actual_verdict == probe["expected_verdict"] else "✗"
        
        results.append((probe["label"], actual_verdict, conf, token, lp, verdict_ok))
        
        print(f"expected={probe['expected_verdict']}, actual={actual_verdict} {verdict_ok}")
        if conf is not None:
            print(f"  P(verdict)={conf:.4f}  token={repr(token)}  logprob={lp:.4f}")
        else:
            print(f"  P(verdict)=N/A")

    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    confidences = []
    for gt, actual, conf, token, lp, ok in results:
        conf_str = f"{conf:.4f}" if conf is not None else "N/A"
        print(f"  GT={gt:<10}: verdict={actual:<12} {ok}  P={conf_str}")
        if conf is not None:
            confidences.append(conf)

    if len(confidences) >= 2:
        crange = max(confidences) - min(confidences)
        print(f"\nP(verdict) range: {crange:.4f}")
        if crange < 0.01:
            print("⚠ FLAT — signal too weak. Model equally confident on everything.")
        elif crange < 0.1:
            print("~ Weak — slight variance. Borderline usable.")
        else:
            print("✓ Usable signal — confidence varies meaningfully.")


if __name__ == "__main__":
    main()
