"""
Real-World Injector
===================
Injects real LeetCode problems and messy real-world prompts into the stress test pipeline.

This breaks the assumption that all inputs come from the synthetic generator,
introducing distribution shift and real-world ambiguity.
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Optional, Tuple

from external_stress_layer import StressCase, StressKind


# Real LeetCode problem descriptions (messy, ambiguous, real-world)
LEETCODE_PROBLEMS = [
    {
        "title": "Two Sum",
        "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. You may assume that each input would have exactly one solution, and you may not use the same element twice.",
        "ground_truth": "correct",
        "ambiguity": "What if multiple pairs sum to target? What if no solution exists despite the assumption?",
        "real_issues": "Assumption stated in problem but not enforced in edge cases",
    },
    {
        "title": "Valid Parentheses",
        "description": "Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid. An input string is valid if: Open brackets must be closed by the same type of brackets. Open brackets must be closed in the correct order. Every close bracket has a corresponding open bracket of the same type.",
        "ground_truth": "correct",
        "ambiguity": "What about empty string? What about characters other than brackets?",
        "real_issues": "Edge cases not fully specified, implicit assumptions about input domain",
    },
    {
        "title": "Merge Intervals",
        "description": "Given an array of intervals where intervals[i] = [starti, endi], merge all overlapping intervals, and return an array of the non-overlapping intervals that cover all the intervals in the input.",
        "ground_truth": "partial",
        "ambiguity": "What defines 'overlapping'? Does [1,4] overlap with [4,5]? What about sorting order?",
        "real_issues": "Boundary conditions ambiguous, real implementations need to make arbitrary choices",
    },
    {
        "title": "Group Anagrams",
        "description": "Given an array of strings strs, group the anagrams together. You can return the answer in any order.",
        "ground_truth": "correct",
        "ambiguity": "What about empty strings? Case sensitivity? Unicode vs ASCII?",
        "real_issues": "Output order 'any' but grading systems expect specific order",
    },
    {
        "title": "Longest Substring Without Repeating Characters",
        "description": "Given a string s, find the length of the longest substring without repeating characters.",
        "ground_truth": "correct",
        "ambiguity": "What constitutes a 'repeating character'? Case-sensitive? Unicode normalization?",
        "real_issues": "Real-world text has complications the problem ignores",
    },
    {
        "title": "3Sum",
        "description": "Given an integer array nums, return all the triplets [nums[i], nums[j], nums[k]] such that i != j, i != k, and j != k, and nums[i] + nums[j] + nums[k] == 0. Notice that the solution set must not contain duplicate triplets.",
        "ground_truth": "partial",
        "ambiguity": "What defines 'duplicate'? Same values or same indices? Order within triplet?",
        "real_issues": "Duplicate handling is ambiguous without explicit definition",
    },
    {
        "title": "Container With Most Water",
        "description": "You are given an integer array height of length n. There are n vertical lines drawn such that the two endpoints of ith line are (i, 0) and (i, height[i]). Find two lines that together with the x-axis form a container, such that the container contains the most water.",
        "ground_truth": "correct",
        "ambiguity": "Physical interpretation vs. mathematical - which takes priority?",
        "real_issues": "Real-world analogy introduces unnecessary confusion",
    },
    {
        "title": "Trapping Rain Water",
        "description": "Given n non-negative integers representing an elevation map where the width of each bar is 1, compute how much water it can trap after raining.",
        "ground_truth": "partial",
        "ambiguity": "Edge behavior at boundaries? What about zero-height bars?",
        "real_issues": "Physical model requires assumptions not stated in problem",
    },
]

# Messy community discussions and forum posts
FORUM_DISCUSSIONS = [
    {
        "title": "Confused about edge case in problem 42",
        "content": "So I submitted my solution and it passes 95% of test cases but fails on one where the input is [0,0,0,0]. The problem says 'non-negative integers' so zeros should be valid, but the expected output seems wrong? Or maybe I'm misunderstanding something. Also, does anyone know if the input can be empty? The constraints say 1 <= n but some test cases seem to violate this.",
        "ground_truth": "undefined",
        "reason": "Contradictory information, unclear specifications",
    },
    {
        "title": "Why does my O(n) solution get TLE?",
        "content": "I implemented the optimal two-pointer approach which is O(n) time and O(1) space, but I'm getting Time Limit Exceeded. My friend's O(n²) solution passes. I think there might be an issue with how Python handles large integers? Or maybe the test cases are just really strict. The problem statement doesn't mention anything about constant factors.",
        "ground_truth": "partial",
        "reason": "Performance requirements implicit, implementation-dependent",
    },
    {
        "title": "Multiple valid outputs??",
        "content": "The problem says 'you can return any valid answer' but the judge only accepts one specific output. I tried returning [[1,2,3]] and [[3,2,1]] and only one passed. This is super confusing. The examples show one format but the description says any order is fine. Which one should I follow?",
        "ground_truth": "undefined",
        "reason": "Contradiction between problem statement and judge behavior",
    },
]

# Poorly written community problems
COMMUNITY_PROBLEMS = [
    {
        "title": "Sort but kinda weird",
        "content": "You need to sort an array but there's a twist - even numbers should come first but in reverse order, and odd numbers should be in normal order at the end. Wait, actually I think I got it wrong. Let me check... no, it's definitely even numbers first. Or maybe it was descending order? I forgot. Just implement something that works for the test cases I guess.",
        "ground_truth": "undefined",
        "reason": "Requirements unclear and self-contradictory",
    },
    {
        "title": "Binary search but with duplicates",
        "content": "Implement binary search on a sorted array that might have duplicates. Return the index of the target. If there are multiple occurrences, return... um... I think the first one? Or maybe any one? Actually the original problem just says 'find the element' so probably any index is fine. But what if it's not present? Return -1 I suppose.",
        "ground_truth": "partial",
        "reason": "Some requirements stated, others implied or uncertain",
    },
    {
        "title": "Graph problem (I think)",
        "content": "Given a list of edges, find the shortest path from A to B. The graph might be directed? Or undirected? I'm not sure, the diagram shows arrows but the text doesn't specify. Edge weights are positive I think. Use Dijkstra or BFS or something. Just output the distance.",
        "ground_truth": "undefined",
        "reason": "Critical information missing (directed vs undirected)",
    },
]

# Incomplete specifications
INCOMPLETE_SPECS = [
    {
        "title": "Queue with priority",
        "content": "Implement a queue that supports push and pop operations. Pop should return the highest priority element. Priority is determined by... uh... the value I guess? Higher value = higher priority? What if two elements have the same priority? No idea, make something up.",
        "ground_truth": "undefined",
        "reason": "Tie-breaking behavior unspecified",
    },
    {
        "title": "String matcher",
        "content": "Check if string A is a substring of string B. Case sensitivity not specified. Empty strings? Unicode? Emoji? I haven't thought about these cases. Just handle ASCII for now.",
        "ground_truth": "partial",
        "reason": "Domain assumptions made explicit but incomplete",
    },
    {
        "title": "Counter with limits",
        "content": "Create a counter that increments on 'inc' and decrements on 'dec'. The counter should stay within bounds [0, 100]. What happens if you try to go below 0 or above 100? Does it clamp? Error? Ignore? I'd say clamp but that's just my opinion.",
        "ground_truth": "partial",
        "reason": "Boundary behavior suggested but not confirmed",
    },
]


class RealWorldInjector:
    """Injects real-world problems and messy prompts into stress tests.
    
    This component breaks the closed-loop assumption by introducing:
    - Actual LeetCode problems with their inherent ambiguities
    - Community forum discussions with contradictory information
    - Poorly written community problems
    - Incomplete specifications
    
    These inputs don't fit the generator's A-E strata and expose
    whether the Doctor has learned patterns vs. truly reasoning.
    """
    
    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.case_counter = 0
    
    def generate_cases(self, n: int = 20) -> List[StressCase]:
        """Generate n real-world stress cases.
        
        Args:
            n: Number of cases to generate
            
        Returns:
            List of StressCase objects with real-world prompts
        """
        cases = []
        
        # Distribute across different sources
        sources = [
            (LEETCODE_PROBLEMS, "leetcode"),
            (FORUM_DISCUSSIONS, "forum"),
            (COMMUNITY_PROBLEMS, "community"),
            (INCOMPLETE_SPECS, "incomplete_spec"),
        ]
        
        cases_per_source = max(1, n // len(sources))
        remainder = n - cases_per_source * len(sources)
        
        for source_data, source_type in sources:
            count = cases_per_source + (1 if remainder > 0 else 0)
            remainder = max(0, remainder - 1)
            
            # Sample with replacement if needed
            selected = self.rng.choices(source_data, k=count)
            
            for item in selected:
                case = self._create_case(item, source_type)
                cases.append(case)
        
        self.rng.shuffle(cases)
        return cases
    
    def _create_case(self, item: Dict[str, Any], source_type: str) -> StressCase:
        """Create a StressCase from a real-world item."""
        self.case_counter += 1
        case_id = f"RW-{self.case_counter:04d}"
        
        # Build prompt from the real-world item
        if source_type == "leetcode":
            prompt = self._build_leetcode_prompt(item)
        elif source_type == "forum":
            prompt = self._build_forum_prompt(item)
        elif source_type == "community":
            prompt = self._build_community_prompt(item)
        else:  # incomplete_spec
            prompt = self._build_incomplete_spec_prompt(item)
        
        return StressCase(
            case_id=case_id,
            prompt=prompt,
            stress_kind=StressKind.REAL_WORLD,
            ground_truth=item["ground_truth"],
            metadata={
                "source_type": source_type,
                "title": item.get("title", "unknown"),
                "ambiguity": item.get("ambiguity", item.get("reason", "")),
                "real_issueses": item.get("real_issues", ""),
            },
        )
    
    def _build_leetcode_prompt(self, item: Dict[str, Any]) -> str:
        """Build a prompt from a LeetCode problem."""
        return (
            f"PROBLEM: {item['title']}\n"
            f"Description: {item['description']}\n"
            f"Note: {item['ambiguity']}\n"
            f"PROPOSED RESPONSE: Standard algorithmic solution "
            f"with edge case handling and optimal complexity."
        )
    
    def _build_forum_prompt(self, item: Dict[str, Any]) -> str:
        """Build a prompt from a forum discussion."""
        return (
            f"FORUM DISCUSSION: {item['title']}\n"
            f"Content: {item['content']}\n"
            f"Assessment needed: {item['reason']}\n"
            f"PROPOSED RESPONSE: Analysis based on available information, "
            f"noting contradictions and ambiguities."
        )
    
    def _build_community_prompt(self, item: Dict[str, Any]) -> str:
        """Build a prompt from a poorly written community problem."""
        return (
            f"COMMUNITY PROBLEM: {item['title']}\n"
            f"Content: {item['content']}\n"
            f"Assessment: {item['reason']}\n"
            f"PROPOSED RESPONSE: Best-effort interpretation of ambiguous "
            f"requirements, with assumptions stated."
        )
    
    def _build_incomplete_spec_prompt(self, item: Dict[str, Any]) -> str:
        """Build a prompt from an incomplete specification."""
        return (
            f"INCOMPLETE SPEC: {item['title']}\n"
            f"Content: {item['content']}\n"
            f"Issue: {item['reason']}\n"
            f"PROPOSED RESPONSE: Partial implementation with documented "
            f"assumptions for unspecified behavior."
        )
    
    def inject_into_batch(self, cases: List[StressCase], n_inject: int = 5) -> List[StressCase]:
        """Inject real-world cases into an existing batch of cases.
        
        Args:
            cases: Existing cases (e.g., from generator)
            n_inject: Number of real-world cases to inject
            
        Returns:
            Combined list with injected cases
        """
        injected = self.generate_cases(n_inject)
        combined = cases + injected
        self.rng.shuffle(combined)
        return combined
