import requests
import json
import time

print("Testing mistral confidence calibration...")

OLLAMA_URL = "http://localhost:11435/api/generate"

test_cases = [
    ("Two Sum", "correct", "def twoSum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        complement = target - n\n        if complement in seen:\n            return [seen[complement], i]\n        seen[n] = i\n    return []"),
    ("Two Sum", "incorrect", "def twoSum(nums, target):\n    for i in range(len(nums)):\n        if nums[i] + nums[i] == target:\n            return [i, i]\n    return []"),
    ("Valid Parentheses", "correct", "def isValid(s):\n    stack = []\n    mapping = {')': '(', '}': '{', ']': '['}\n    for char in s:\n        if char in mapping:\n            top = stack.pop() if stack else '#'\n            if mapping[char] != top:\n                return False\n        else:\n            stack.append(char)\n    return not stack"),
    ("Valid Parentheses", "incorrect", "def isValid(s):\n    return len(s) % 2 == 0"),
]

prompt_template = """You are evaluating a LeetCode solution.

Problem: {problem_text}

Code:
{solution_code}

Classify as correct, partial, or incorrect.
Output JSON only:
{{"verdict": "correct|partial|incorrect", "confidence": 0.0-1.0, "reasoning": "one sentence"}}"""

for name, gt, code in test_cases:
    prompt = prompt_template.format(
        problem_text="Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.",
        solution_code=code
    )
    
    try:
        start = time.time()
        resp = requests.post(OLLAMA_URL, json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0}
        }, timeout=120)
        elapsed = time.time() - start
        
        data = resp.json()
        raw = data.get("response", "").strip()
        
        try:
            parsed = json.loads(raw)
            verdict = parsed.get("verdict", "unknown")
            confidence = parsed.get("confidence", 0.5)
        except:
            # Try to extract JSON from text
            start_idx = raw.find("{")
            end_idx = raw.rfind("}") + 1
            if start_idx >= 0:
                parsed = json.loads(raw[start_idx:end_idx])
                verdict = parsed.get("verdict", "unknown")
                confidence = parsed.get("confidence", 0.5)
            else:
                verdict = "parse_error"
                confidence = 0.5
        
        print(f"{name}_{gt}: verdict={verdict} conf={confidence:.2f} ({elapsed:.1f}s)")
        
    except Exception as e:
        print(f"{name}_{gt}: ERROR - {str(e)[:50]}")
