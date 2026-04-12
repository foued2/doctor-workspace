import sys
sys.path.insert(0, r'F:\pythonProject')
from doctor.test_executor import TestExecutor

# The partial solutions from the baseline test
partial_solutions = {
    "longest_palindrome": """def longestPalindrome(s):
    if not s: return ""
    best = s[0]
    for i in range(len(s)):
        l, r = i, i
        while l >= 0 and r < len(s) and s[l] == s[r]:
            if r - l + 1 > len(best):
                best = s[l:r+1]
            l -= 1
            r += 1
    return best""",
    # Only odd-length expansion (misses even)
    
    "roman_to_integer": """def romanToInt(s):
    val = {'I':1,'V':5,'X':10,'L':50,'C':100,'D':500,'M':1000}
    total = 0
    for i in range(len(s)):
        total += val[s[i]]
    return total""",
    # No subtractive notation
    
    "trap": """def trap(height):
    if not height: return 0
    total = 0
    for i in range(1, len(height)-1):
        left = max(height[:i])
        right = max(height[i+1:])
        water = min(left, right) - height[i]
        if water > 0:
            total += water
    return total""",
    # Correct but O(n^2)
    
    "valid_parentheses": """def isValid(s):
    count = 0
    for c in s:
        if c == '(': count += 1
        elif c == ')': count -= 1
        if count < 0: return False
    return count == 0""",
    # Counter only, ignores type ordering
}

executor = TestExecutor()
problem_names = {
    "longest_palindrome": "Longest Palindromic Substring",
    "roman_to_integer": "Roman to Integer",
    "trap": "Trapping Rain Water",
    "valid_parentheses": "Valid Parentheses",
}
for key, code in partial_solutions.items():
    report = executor.verify(problem_names[key], code)
    failed = [r.label for r in report.results if not r.passed]
    print(f"\n{key}:")
    print(f"  verdict={report.verdict}, pass_rate={report.pass_rate}")
    print(f"  severity={report.severity}, ratio={report.failure_ratio}")
    print(f"  core_fail={report.core_failures}, edge_fail={report.edge_failures}")
    print(f"  failed_labels={failed}")
