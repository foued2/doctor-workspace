"""3-probe confidence variance check — verify mistral outputs varying confidence values."""
import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "phi3"

THREE_PROBES = [
    # Probe 1: Clearly correct solution (Two Sum optimal)
    {
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
    # Probe 2: Clearly incorrect solution (Two Sum broken)
    {
        "problem": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
        "code": (
            "def twoSum(nums, target):\n"
            "    for i in range(len(nums)):\n"
            "        if nums[i] + nums[i] == target:\n"
            "            return [i, i]\n"
            "    return []"
        ),
    },
    # Probe 3: Partial solution (Two Sum brute force)
    {
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
    if "```" in raw:
        for block in raw.split("```"):
            block = block.strip()
            if block.startswith("json"):
                block = block[4:].strip()
            try:
                return json.loads(block)
            except json.JSONDecodeError:
                continue
    start = raw.find("{")
    end = raw.rfind("}")
    if start >= 0 and end > start:
        try:
            return json.loads(raw[start:end + 1])
        except json.JSONDecodeError:
            pass
    return {"verdict": "incorrect", "confidence": 0.5, "reasoning": f"Could not parse: {raw[:200]}"}


def main():
    print("=" * 70)
    print("3-PROBE CONFIDENCE VARIANCE CHECK (mistral)")
    print("=" * 70)

    confidences = []
    for i, probe in enumerate(THREE_PROBES, 1):
        prompt = PROMPT_TEMPLATE.format(problem_text=probe["problem"], solution_code=probe["code"])
        print(f"\nProbe {i}: ", end="")

        resp = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0, "num_predict": 512}
        }, timeout=300)

        raw = resp.json()["response"].strip()
        parsed = _extract_json(raw)
        conf = parsed.get("confidence", -1)
        verdict = parsed.get("verdict", "unknown")
        confidences.append(conf)

        print(f"verdict={verdict}, confidence={conf}")
        print(f"  reasoning: {parsed.get('reasoning', 'N/A')[:120]}")

    print(f"\n{'=' * 70}")
    print(f"Confidences: {confidences}")
    print(f"Min: {min(confidences):.2f}, Max: {max(confidences):.2f}, Range: {max(confidences) - min(confidences):.2f}")

    if max(confidences) - min(confidences) < 0.05:
        print("⚠ FLAT — confidence is constant. Experiment is INVALID.")
    else:
        print("✓ VARIANCE DETECTED — confidence varies across solutions. Experiment is VALID.")


if __name__ == "__main__":
    main()
