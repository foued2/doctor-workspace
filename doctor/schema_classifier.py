#!/usr/bin/env python3
"""
Schema classifier: given a problem statement, outputs domain, paradigm, dp_type, confidence.
Uses few-shot examples from ground truth labels.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from doctor.ingest.problem_parser import _call_llm_with_stats

# Few-shot examples drawn from ground truth labels
FEW_SHOT = (
    "Example 1:\n"
    "Statement: Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.\n"
    "Output: {\"domain\": \"array\", \"paradigm\": \"hashing\", \"dp_type\": \"\", \"confidence\": \"high\"}\n\n"
    "Example 2:\n"
    "Statement: Given an integer x, return true if x reads the same forward and backward.\n"
    "Output: {\"domain\": \"math\", \"paradigm\": \"reversal\", \"dp_type\": \"\", \"confidence\": \"high\"}\n\n"
    "Example 3:\n"
    "Statement: Given an integer array nums, return the contiguous subarray with the largest sum.\n"
    "Output: {\"domain\": \"array\", \"paradigm\": \"dynamic_programming\", \"dp_type\": \"1D\", \"confidence\": \"high\"}\n\n"
    "Example 4:\n"
    "Statement: Given two strings s and t, return the minimum window substring of s such that every character in t is included.\n"
    "Output: {\"domain\": \"string\", \"paradigm\": \"sliding_window\", \"dp_type\": \"\", \"confidence\": \"high\"}\n\n"
    "Example 5:\n"
    "Statement: Given an integer n, return all distinct solutions to the n-queens puzzle.\n"
    "Output: {\"domain\": \"matrix\", \"paradigm\": \"backtracking\", \"dp_type\": \"\", \"confidence\": \"high\"}\n\n"
    "Example 6:\n"
    "Statement: Return the sum of the even-valued Fibonacci terms that do not exceed n.\n"
    "Output: {\"domain\": \"math\", \"paradigm\": \"iterative\", \"dp_type\": \"\", \"confidence\": \"high\"}\n"
)

PROMPT_START = (
    "Classify this problem statement into schema fields.\n\n"
    "Return only valid JSON:\n"
    "{\n"
    '  "domain": "array|string|math|matrix|linked_list|tree|graph",\n'
    '  "paradigm": "hashing|two_pointer|reversal|backtracking|dynamic_programming|recursive|iterative|greedy|stack_based|sliding_window|binary_search|other",\n'
    '  "dp_type": "1D|2D|",\n'
    '  "confidence": "high|low"\n'
    "}\n\n"
    "Rules:\n"
    "- domain: structural data type the problem operates on\n"
    "- paradigm: primary algorithmic technique\n"
    "- dp_type: only fill if problem uses dynamic programming\n"
    "- confidence: high if clear, low if ambiguous\n\n"
)

PROMPT_END = "\n\nOutput JSON:"


def classify_schema(statement):
    """Classify problem statement into schema fields.
    
    Returns: {"domain": str, "paradigm": str, "dp_type": str, "confidence": str}
    """
    prompt = PROMPT_START + FEW_SHOT + "Statement: " + statement + PROMPT_END
    
    try:
        response, _ = _call_llm_with_stats(prompt)
        data = json.loads(response.strip())
        return {
            "domain": data.get("domain", ""),
            "paradigm": data.get("paradigm", ""),
            "dp_type": data.get("dp_type", ""),
            "confidence": data.get("confidence", "low")
        }
    except Exception as e:
        return {
            "domain": "",
            "paradigm": "",
            "dp_type": "",
            "confidence": "",
            "error": str(e)
        }


if __name__ == "__main__":
    # Quick test
    test_statement = "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target."
    result = classify_schema(test_statement)
    print(json.dumps(result, indent=2))
