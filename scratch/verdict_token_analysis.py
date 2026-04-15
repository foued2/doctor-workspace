"""Deeper logprobs analysis — check if verdict token probabilities differ."""
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

VERDICT_TOKENS = {"correct": ["correct", "Correct"], "partial": ["partial", "Partial"], "incorrect": ["incorrect", "Incorrect"]}


def analyze_verdict_tokens(logprobs):
    """Find the first token that matches a verdict keyword and return its probability."""
    verdict_token_probs = {}
    verdict_token_logprobs = {}
    
    for lp in logprobs:
        token = lp["token"].strip().strip('"').strip('{')
        logprob = lp["logprob"]
        prob = math.exp(logprob)
        
        for verdict, variants in VERDICT_TOKENS.items():
            if token in variants and verdict not in verdict_token_probs:
                verdict_token_probs[verdict] = prob
                verdict_token_logprobs[verdict] = logprob
    
    return verdict_token_probs, verdict_token_logprobs


def main():
    print("=" * 70)
    print("VERDICT TOKEN PROBABILITY ANALYSIS (logprobs)")
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
        logprobs = data.get("logprobs", [])
        verdict_probs, verdict_logprobs = analyze_verdict_tokens(logprobs)
        
        results.append((probe["label"], verdict_probs, verdict_logprobs))

        # Show first 5 tokens for debugging
        print(f"\n  First 5 logprob tokens:")
        for lp in logprobs[:5]:
            print(f"    {repr(lp['token']):>15}  logprob={lp['logprob']:.4f}  prob={math.exp(lp['logprob']):.4f}")
        
        print(f"  Verdict token probabilities:")
        for v in ["correct", "partial", "incorrect"]:
            if v in verdict_probs:
                print(f"    P({v}) = {verdict_probs[v]:.4f}  (logprob={verdict_logprobs[v]:.4f})")
            else:
                print(f"    P({v}) = not found in first tokens")

    print(f"\n{'=' * 70}")
    print("COMPARISON")
    print(f"{'=' * 70}")
    for gt, probs, logprobs_dict in results:
        correct_p = probs.get("correct", 0)
        incorrect_p = probs.get("incorrect", 0)
        partial_p = probs.get("partial", 0)
        # Confidence = P(verdict token matches model's actual verdict)
        max_verdict_p = max(correct_p, incorrect_p, partial_p)
        print(f"  GT={gt:<10}: P(correct)={correct_p:.4f}  P(partial)={partial_p:.4f}  P(incorrect)={incorrect_p:.4f}  max={max_verdict_p:.4f}")


if __name__ == "__main__":
    main()
