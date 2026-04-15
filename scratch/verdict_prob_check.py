"""Find the verdict token probability in the JSON response."""
import json
import math
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral"

THREE_PROBES = [
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

VERDICT_KEYWORDS = {"correct", "partial", "incorrect", "Correct", "Partial", "Incorrect"}


def find_verdict_token(logprobs):
    """Find the token that is the actual verdict value (the word after 'verdict': \")."""
    for i, lp in enumerate(logprobs):
        token = lp["token"].strip().strip('"')
        if token in VERDICT_KEYWORDS:
            # Check if previous token was '":' or '"' — confirms it's the verdict value
            if i > 0:
                prev = logprobs[i-1]["token"].strip()
                if prev in ('":', '"'):
                    return lp["token"].strip(), lp["logprob"]
    return None, None


def main():
    print("=" * 70)
    print("VERDICT TOKEN PROBABILITY (after \"verdict\": \")")
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
        
        verdict_token, verdict_logprob = find_verdict_token(logprobs)
        verdict_prob = math.exp(verdict_logprob) if verdict_logprob else None
        
        results.append((probe["label"], verdict_token, verdict_prob, verdict_logprob))

        # Also extract the parsed verdict
        try:
            parsed = json.loads(raw)
            actual_verdict = parsed.get("verdict", "unknown")
        except:
            actual_verdict = "parse_error"

        if verdict_token:
            print(f"actual_verdict={actual_verdict}")
            print(f"  verdict_token={repr(verdict_token)}, P={verdict_prob:.6f}, logprob={verdict_logprob:.4f}")
        else:
            print(f"actual_verdict={actual_verdict}")
            # Show ALL tokens to find how 'incorrect' was tokenized
            print(f"  All tokens:")
            for j, lp in enumerate(logprobs):
                t = lp["token"]
                lp_val = lp["logprob"]
                is_verdict = t.strip().strip('"').lower() in ("correct", "incorrect", "partial")
                marker = " <<< VERDICT" if is_verdict else ""
                print(f"    [{j:3d}] {repr(t):>20}  logprob={lp_val:.4f}{marker}")
            break

    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    for gt, token, prob, logprob in results:
        if prob is not None:
            print(f"  GT={gt:<10}: verdict={token:<12} P={prob:.6f}")
        else:
            print(f"  GT={gt:<10}: verdict token NOT FOUND")


if __name__ == "__main__":
    main()
