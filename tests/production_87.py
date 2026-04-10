#!/usr/bin/env python
"""
87-Case Production Test — 29 LeetCode Problems × 3 Solution Types.
Real problem descriptions, real Python solution code.
No labels, no hints, no solution type markers in the prompt.
"""
import sys
import json
from pathlib import Path
from collections import Counter
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from doctor.llm_doctor import LLMDoctor

# ===========================================================================
# 29 LeetCode problems with problem descriptions and 3 Python solutions each.
# Correct:   optimal approach, handles all constraints
# Partial:   right idea but subtle edge case bug
# Incorrect: wrong approach or fundamentally broken
# ===========================================================================
PROBLEMS = [
    # ── Easy (9) ──────────────────────────────────────────────────────────
    {
        "name": "Two Sum",
        "difficulty": "Easy",
        "problem": (
            "Given an array of integers nums and an integer target, "
            "return indices of the two numbers such that they add up to target. "
            "You may assume that each input would have exactly one solution, "
            "and you may not use the same element twice. "
            "You can return the answer in any order."
        ),
        "correct": (
            "def twoSum(nums, target):\n"
            "    seen = {}\n"
            "    for i, n in enumerate(nums):\n"
            "        if target - n in seen:\n"
            "            return [seen[target - n], i]\n"
            "        seen[n] = i"
        ),
        "partial": (
            "def twoSum(nums, target):\n"
            "    seen = {}\n"
            "    for i, n in enumerate(nums):\n"
            "        seen[n] = i\n"
            "        if target - n in seen:\n"
            "            return [seen[target - n], i]"
        ),
        "incorrect": (
            "def twoSum(nums, target):\n"
            "    for i in range(len(nums)):\n"
            "        for j in range(len(nums)):\n"
            "            if nums[i] + nums[j] == target:\n"
            "                return [i, j]"
        ),
    },
    {
        "name": "Palindrome Number",
        "difficulty": "Easy",
        "problem": (
            "Given an integer x, return true if x is a palindrome, and false otherwise. "
            "An integer is a palindrome when it reads the same forward and backward."
        ),
        "correct": (
            "def isPalindrome(x):\n"
            "    if x < 0:\n"
            "        return False\n"
            "    if x == 0:\n"
            "        return True\n"
            "    if x % 10 == 0:\n"
            "        return False\n"
            "    rev = 0\n"
            "    orig = x\n"
            "    while x > 0:\n"
            "        rev = rev * 10 + x % 10\n"
            "        x //= 10\n"
            "    return rev == orig"
        ),
        "partial": (
            "def isPalindrome(x):\n"
            "    if x < 0:\n"
            "        return False\n"
            "    rev = 0\n"
            "    temp = x\n"
            "    while temp > 0:\n"
            "        rev = rev * 10 + temp % 10\n"
            "        temp //= 10\n"
            "    return rev == x"
        ),
        "incorrect": (
            "def isPalindrome(x):\n"
            "    s = str(abs(x))\n"
            "    return s == s[::-1]"
        ),
    },
    {
        "name": "Roman to Integer",
        "difficulty": "Easy",
        "problem": (
            "Roman numerals are represented by seven different symbols: "
            "I, V, X, L, C, D and M. "
            "Given a roman numeral, convert it to an integer. "
            "The input is guaranteed to be a valid roman numeral in the range [1, 3999]."
        ),
        "correct": (
            "def romanToInt(s):\n"
            "    values = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}\n"
            "    total = 0\n"
            "    prev = 0\n"
            "    for ch in reversed(s):\n"
            "        curr = values[ch]\n"
            "        if curr < prev:\n"
            "            total -= curr\n"
            "        else:\n"
            "            total += curr\n"
            "        prev = curr\n"
            "    return total"
        ),
        "partial": (
            "def romanToInt(s):\n"
            "    values = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}\n"
            "    total = 0\n"
            "    for i in range(len(s) - 1):\n"
            "        if values[s[i]] < values[s[i + 1]]:\n"
            "            total -= values[s[i]]\n"
            "        else:\n"
            "            total += values[s[i]]\n"
            "    return total + values[s[-1]]"
        ),
        "incorrect": (
            "def romanToInt(s):\n"
            "    values = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}\n"
            "    return sum(values[c] for c in s)"
        ),
    },
    {
        "name": "Longest Common Prefix",
        "difficulty": "Easy",
        "problem": (
            "Write a function to find the longest common prefix string amongst an array of strings. "
            "If there is no common prefix, return an empty string \"\"."
        ),
        "correct": (
            "def longestCommonPrefix(strs):\n"
            "    if not strs:\n"
            "        return \"\"\n"
            "    prefix = strs[0]\n"
            "    for s in strs[1:]:\n"
            "        while not s.startswith(prefix):\n"
            "            prefix = prefix[:-1]\n"
            "            if not prefix:\n"
            "                return \"\"\n"
            "    return prefix"
        ),
        "partial": (
            "def longestCommonPrefix(strs):\n"
            "    prefix = strs[0]\n"
            "    for s in strs[1:]:\n"
            "        while not s.startswith(prefix):\n"
            "            prefix = prefix[:-1]\n"
            "    return prefix"
        ),
        "incorrect": (
            "def longestCommonPrefix(strs):\n"
            "    return min(strs)"
        ),
    },
    {
        "name": "Valid Parentheses",
        "difficulty": "Easy",
        "problem": (
            "Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', "
            "determine if the input string is valid.\n"
            "An input string is valid if:\n"
            "1. Open brackets must be closed by the same type of brackets.\n"
            "2. Open brackets must be closed in the correct order.\n"
            "3. Every close bracket has a corresponding open bracket of the same type."
        ),
        "correct": (
            "def isValid(s):\n"
            "    stack = []\n"
            "    mapping = {')': '(', '}': '{', ']': '['}\n"
            "    for char in s:\n"
            "        if char in mapping:\n"
            "            top = stack.pop() if stack else '#'\n"
            "            if mapping[char] != top:\n"
            "                return False\n"
            "        else:\n"
            "            stack.append(char)\n"
            "    return not stack"
        ),
        "partial": (
            "def isValid(s):\n"
            "    stack = []\n"
            "    mapping = {')': '(', '}': '{', ']': '['}\n"
            "    for char in s:\n"
            "        if char in mapping:\n"
            "            if not stack:\n"
            "                return False\n"
            "            top = stack.pop()\n"
            "            if mapping[char] != top:\n"
            "                return False\n"
            "        else:\n"
            "            stack.append(char)\n"
            "    return True"
        ),
        "incorrect": (
            "def isValid(s):\n"
            "    while '()' in s or '{}' in s or '[]' in s:\n"
            "        s = s.replace('()', '').replace('{}', '').replace('[]', '')\n"
            "    return s == ''"
        ),
    },
    {
        "name": "Merge Two Sorted Lists",
        "difficulty": "Easy",
        "problem": (
            "You are given the heads of two sorted linked lists list1 and list2. "
            "Merge the two lists into one sorted list. "
            "The list should be made by splicing together the nodes of the first two lists. "
            "Return the head of the merged linked list."
        ),
        "correct": (
            "def mergeTwoLists(list1, list2):\n"
            "    dummy = ListNode(0)\n"
            "    curr = dummy\n"
            "    while list1 and list2:\n"
            "        if list1.val <= list2.val:\n"
            "            curr.next = list1\n"
            "            list1 = list1.next\n"
            "        else:\n"
            "            curr.next = list2\n"
            "            list2 = list2.next\n"
            "        curr = curr.next\n"
            "    curr.next = list1 or list2\n"
            "    return dummy.next"
        ),
        "partial": (
            "def mergeTwoLists(list1, list2):\n"
            "    vals = []\n"
            "    while list1:\n"
            "        vals.append(list1.val)\n"
            "        list1 = list1.next\n"
            "    while list2:\n"
            "        vals.append(list2.val)\n"
            "        list2 = list2.next\n"
            "    vals.sort()\n"
            "    dummy = ListNode(0)\n"
            "    curr = dummy\n"
            "    for v in vals:\n"
            "        curr.next = ListNode(v)\n"
            "        curr = curr.next\n"
            "    return dummy.next"
        ),
        "incorrect": (
            "def mergeTwoLists(list1, list2):\n"
            "    if not list1:\n"
            "        return list2\n"
            "    curr = list1\n"
            "    while curr.next:\n"
            "        curr = curr.next\n"
            "    curr.next = list2\n"
            "    return list1"
        ),
    },
    {
        "name": "Remove Duplicates from Sorted Array",
        "difficulty": "Easy",
        "problem": (
            "Given an integer array nums sorted in non-decreasing order, "
            "remove the duplicates in-place such that each unique element appears only once. "
            "Return k after placing the final result in the first k slots of nums."
        ),
        "correct": (
            "def removeDuplicates(nums):\n"
            "    if not nums:\n"
            "        return 0\n"
            "    k = 1\n"
            "    for i in range(1, len(nums)):\n"
            "        if nums[i] != nums[i - 1]:\n"
            "            nums[k] = nums[i]\n"
            "            k += 1\n"
            "    return k"
        ),
        "partial": (
            "def removeDuplicates(nums):\n"
            "    seen = set()\n"
            "    result = []\n"
            "    for n in nums:\n"
            "        if n not in seen:\n"
            "            seen.add(n)\n"
            "            result.append(n)\n"
            "    for i in range(len(result)):\n"
            "        nums[i] = result[i]\n"
            "    return len(result)"
        ),
        "incorrect": (
            "def removeDuplicates(nums):\n"
            "    return len(set(nums))"
        ),
    },
    {
        "name": "Implement strStr()",
        "difficulty": "Easy",
        "problem": (
            "Given two strings needle and haystack, return the index of the first occurrence "
            "of needle in haystack, or -1 if needle is not part of haystack."
        ),
        "correct": (
            "def strStr(haystack, needle):\n"
            "    if not needle:\n"
            "        return 0\n"
            "    for i in range(len(haystack) - len(needle) + 1):\n"
            "        if haystack[i:i + len(needle)] == needle:\n"
            "            return i\n"
            "    return -1"
        ),
        "partial": (
            "def strStr(haystack, needle):\n"
            "    n, m = len(haystack), len(needle)\n"
            "    for i in range(n):\n"
            "        if haystack[i:i + m] == needle:\n"
            "            return i\n"
            "    return -1"
        ),
        "incorrect": (
            "def strStr(haystack, needle):\n"
            "    if needle in haystack:\n"
            "        return 0\n"
            "    return -1"
        ),
    },
    {
        "name": "Search Insert Position",
        "difficulty": "Easy",
        "problem": (
            "Given a sorted array of distinct integers and a target value, "
            "return the index if the target is found. If not, return the index "
            "where it would be if it were inserted in order. "
            "You must write an algorithm with O(log n) runtime complexity."
        ),
        "correct": (
            "def searchInsert(nums, target):\n"
            "    left, right = 0, len(nums) - 1\n"
            "    while left <= right:\n"
            "        mid = (left + right) // 2\n"
            "        if nums[mid] == target:\n"
            "            return mid\n"
            "        elif nums[mid] < target:\n"
            "            left = mid + 1\n"
            "        else:\n"
            "            right = mid - 1\n"
            "    return left"
        ),
        "partial": (
            "def searchInsert(nums, target):\n"
            "    for i, n in enumerate(nums):\n"
            "        if n >= target:\n"
            "            return i\n"
            "    return len(nums)"
        ),
        "incorrect": (
            "def searchInsert(nums, target):\n"
            "    return nums.index(target) if target in nums else -1"
        ),
    },
    # ── Medium (10) ───────────────────────────────────────────────────────
    {
        "name": "Longest Palindromic Substring",
        "difficulty": "Medium",
        "problem": (
            "Given a string s, return the longest palindromic substring in s. "
            "A substring is a contiguous sequence of characters within the string."
        ),
        "correct": (
            "def longestPalindrome(s):\n"
            "    if not s:\n"
            "        return \"\"\n"
            "    start = end = 0\n"
            "    for i in range(len(s)):\n"
            "        l1 = _expand(s, i, i)\n"
            "        l2 = _expand(s, i, i + 1)\n"
            "        longer = max(l1, l2)\n"
            "        if longer > end - start:\n"
            "            start = i - (longer - 1) // 2\n"
            "            end = i + longer // 2\n"
            "    return s[start:end + 1]\n"
            "def _expand(s, l, r):\n"
            "    while l >= 0 and r < len(s) and s[l] == s[r]:\n"
            "        l -= 1\n"
            "        r += 1\n"
            "    return r - l - 1"
        ),
        "partial": (
            "def longestPalindrome(s):\n"
            "    if not s:\n"
            "        return \"\"\n"
            "    best = s[0]\n"
            "    for i in range(len(s)):\n"
            "        l, r = i, i\n"
            "        while l >= 0 and r < len(s) and s[l] == s[r]:\n"
            "            if r - l + 1 > len(best):\n"
            "                best = s[l:r + 1]\n"
            "            l -= 1\n"
            "            r += 1\n"
            "    return best"
        ),
        "incorrect": (
            "def longestPalindrome(s):\n"
            "    best = \"\"\n"
            "    for i in range(len(s)):\n"
            "        for j in range(i, len(s)):\n"
            "            sub = s[i:j + 1]\n"
            "            if sub == sub[::-1] and len(sub) > len(best):\n"
            "                best = sub\n"
            "    return best"
        ),
    },
    {
        "name": "Zigzag Conversion",
        "difficulty": "Medium",
        "problem": (
            "The string \"PAYPALISHIRING\" is written in a zigzag pattern on a given number of rows. "
            "Write the code that will take a string and make this conversion given a number of rows. "
            "Return the string read line by line."
        ),
        "correct": (
            "def convert(s, numRows):\n"
            "    if numRows == 1 or numRows >= len(s):\n"
            "        return s\n"
            "    rows = [''] * numRows\n"
            "    idx = 0\n"
            "    step = 1\n"
            "    for ch in s:\n"
            "        rows[idx] += ch\n"
            "        if idx == 0:\n"
            "            step = 1\n"
            "        elif idx == numRows - 1:\n"
            "            step = -1\n"
            "        idx += step\n"
            "    return ''.join(rows)"
        ),
        "partial": (
            "def convert(s, numRows):\n"
            "    if numRows == 1:\n"
            "        return s\n"
            "    rows = [''] * numRows\n"
            "    idx = 0\n"
            "    step = 1\n"
            "    for ch in s:\n"
            "        rows[idx] += ch\n"
            "        idx += step\n"
            "        if idx == 0 or idx == numRows - 1:\n"
            "            step = -step\n"
            "    return ''.join(rows)"
        ),
        "incorrect": (
            "def convert(s, numRows):\n"
            "    result = []\n"
            "    for i in range(numRows):\n"
            "        result.append(s[i::numRows])\n"
            "    return ''.join(result)"
        ),
    },
    {
        "name": "Reverse Integer",
        "difficulty": "Medium",
        "problem": (
            "Given a signed 32-bit integer x, return x with its digits reversed. "
            "If reversing x causes the value to go outside the signed 32-bit integer range "
            "[-2^31, 2^31 - 1], then return 0."
        ),
        "correct": (
            "def reverse(x):\n"
            "    sign = -1 if x < 0 else 1\n"
            "    rev = int(str(abs(x))[::-1])\n"
            "    if rev > 2**31 - 1:\n"
            "        return 0\n"
            "    return sign * rev"
        ),
        "partial": (
            "def reverse(x):\n"
            "    sign = -1 if x < 0 else 1\n"
            "    rev = int(str(abs(x))[::-1])\n"
            "    return sign * rev"
        ),
        "incorrect": (
            "def reverse(x):\n"
            "    return int(str(x)[::-1])"
        ),
    },
    {
        "name": "String to Integer (atoi)",
        "difficulty": "Medium",
        "problem": (
            "Implement the myAtoi(string s) function, which converts a string to a 32-bit signed integer. "
            "Read in and ignore any leading whitespace. "
            "Check if the next character is '-' or '+'. "
            "Read in next characters until a non-digit character is reached. "
            "Clamp the integer to the range [-2^31, 2^31 - 1]."
        ),
        "correct": (
            "def myAtoi(s):\n"
            "    i = 0\n"
            "    while i < len(s) and s[i] == ' ':\n"
            "        i += 1\n"
            "    if i >= len(s):\n"
            "        return 0\n"
            "    sign = 1\n"
            "    if s[i] == '-':\n"
            "        sign = -1\n"
            "        i += 1\n"
            "    elif s[i] == '+':\n"
            "        i += 1\n"
            "    num = 0\n"
            "    while i < len(s) and s[i].isdigit():\n"
            "        num = num * 10 + int(s[i])\n"
            "        i += 1\n"
            "    num *= sign\n"
            "    return max(-2**31, min(num, 2**31 - 1))"
        ),
        "partial": (
            "def myAtoi(s):\n"
            "    s = s.strip()\n"
            "    if not s:\n"
            "        return 0\n"
            "    sign = 1\n"
            "    if s[0] == '-':\n"
            "        sign = -1\n"
            "        s = s[1:]\n"
            "    elif s[0] == '+':\n"
            "        s = s[1:]\n"
            "    num = 0\n"
            "    for c in s:\n"
            "        if c.isdigit():\n"
            "            num = num * 10 + int(c)\n"
            "    return sign * num"
        ),
        "incorrect": (
            "def myAtoi(s):\n"
            "    return int(s)"
        ),
    },
    {
        "name": "Container With Most Water",
        "difficulty": "Medium",
        "problem": (
            "You are given an integer array height of length n. "
            "Find two lines that together with the x-axis form a container, "
            "such that the container contains the most water. "
            "Return the maximum amount of water a container can store."
        ),
        "correct": (
            "def maxArea(height):\n"
            "    left, right = 0, len(height) - 1\n"
            "    max_water = 0\n"
            "    while left < right:\n"
            "        h = min(height[left], height[right])\n"
            "        w = right - left\n"
            "        max_water = max(max_water, h * w)\n"
            "        if height[left] < height[right]:\n"
            "            left += 1\n"
            "        else:\n"
            "            right -= 1\n"
            "    return max_water"
        ),
        "partial": (
            "def maxArea(height):\n"
            "    max_water = 0\n"
            "    for i in range(len(height)):\n"
            "        for j in range(i + 1, len(height)):\n"
            "            h = min(height[i], height[j])\n"
            "            w = j - i\n"
            "            max_water = max(max_water, h * w)\n"
            "    return max_water"
        ),
        "incorrect": (
            "def maxArea(height):\n"
            "    mx = max(height)\n"
            "    return mx * (len(height) - 1)"
        ),
    },
    {
        "name": "Integer to Roman",
        "difficulty": "Medium",
        "problem": (
            "Given an integer, convert it to a Roman numeral. "
            "Roman numerals are formed by appending the conversions of decimal place values "
            "from highest to lowest, following standard subtraction notation rules."
        ),
        "correct": (
            "def intToRoman(num):\n"
            "    values = [\n"
            "        (1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),\n"
            "        (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),\n"
            "        (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')\n"
            "    ]\n"
            "    result = ''\n"
            "    for value, symbol in values:\n"
            "        count, num = divmod(num, value)\n"
            "        result += symbol * count\n"
            "    return result"
        ),
        "partial": (
            "def intToRoman(num):\n"
            "    values = [1000, 500, 100, 50, 10, 5, 1]\n"
            "    symbols = ['M', 'D', 'C', 'L', 'X', 'V', 'I']\n"
            "    result = ''\n"
            "    for v, s in zip(values, symbols):\n"
            "        result += s * (num // v)\n"
            "        num %= v\n"
            "    return result"
        ),
        "incorrect": (
            "def intToRoman(num):\n"
            "    return str(num)"
        ),
    },
    {
        "name": "3Sum",
        "difficulty": "Medium",
        "problem": (
            "Given an integer array nums, return all the triplets [nums[i], nums[j], nums[k]] "
            "such that i != j, i != k, and j != k, and nums[i] + nums[j] + nums[k] == 0. "
            "The solution set must not contain duplicate triplets."
        ),
        "correct": (
            "def threeSum(nums):\n"
            "    nums.sort()\n"
            "    result = []\n"
            "    for i in range(len(nums) - 2):\n"
            "        if i > 0 and nums[i] == nums[i - 1]:\n"
            "            continue\n"
            "        left, right = i + 1, len(nums) - 1\n"
            "        while left < right:\n"
            "            s = nums[i] + nums[left] + nums[right]\n"
            "            if s == 0:\n"
            "                result.append([nums[i], nums[left], nums[right]])\n"
            "                while left < right and nums[left] == nums[left + 1]:\n"
            "                    left += 1\n"
            "                while left < right and nums[right] == nums[right - 1]:\n"
            "                    right -= 1\n"
            "                left += 1\n"
            "                right -= 1\n"
            "            elif s < 0:\n"
            "                left += 1\n"
            "            else:\n"
            "                right -= 1\n"
            "    return result"
        ),
        "partial": (
            "def threeSum(nums):\n"
            "    nums.sort()\n"
            "    result = []\n"
            "    for i in range(len(nums) - 2):\n"
            "        left, right = i + 1, len(nums) - 1\n"
            "        while left < right:\n"
            "            s = nums[i] + nums[left] + nums[right]\n"
            "            if s == 0:\n"
            "                result.append([nums[i], nums[left], nums[right]])\n"
            "                left += 1\n"
            "                right -= 1\n"
            "            elif s < 0:\n"
            "                left += 1\n"
            "            else:\n"
            "                right -= 1\n"
            "    return result"
        ),
        "incorrect": (
            "def threeSum(nums):\n"
            "    result = []\n"
            "    for i in range(len(nums)):\n"
            "        for j in range(len(nums)):\n"
            "            for k in range(len(nums)):\n"
            "                if nums[i] + nums[j] + nums[k] == 0:\n"
            "                    result.append([nums[i], nums[j], nums[k]])\n"
            "    return result"
        ),
    },
    {
        "name": "Letter Combinations of a Phone Number",
        "difficulty": "Medium",
        "problem": (
            "Given a string containing digits from 2-9 inclusive, return all possible letter "
            "combinations that the number could represent. Return the answer in any order. "
            "A mapping of digits to letters is just like on the telephone buttons. "
            "Note that 1 does not map to any letters."
        ),
        "correct": (
            "def letterCombinations(digits):\n"
            "    if not digits:\n"
            "        return []\n"
            "    mapping = {'2': 'abc', '3': 'def', '4': 'ghi', '5': 'jkl',\n"
            "               '6': 'mno', '7': 'pqrs', '8': 'tuv', '9': 'wxyz'}\n"
            "    result = []\n"
            "    def backtrack(i, path):\n"
            "        if i == len(digits):\n"
            "            result.append(path)\n"
            "            return\n"
            "        for ch in mapping[digits[i]]:\n"
            "            backtrack(i + 1, path + ch)\n"
            "    backtrack(0, '')\n"
            "    return result"
        ),
        "partial": (
            "def letterCombinations(digits):\n"
            "    mapping = {'2': 'abc', '3': 'def', '4': 'ghi', '5': 'jkl',\n"
            "               '6': 'mno', '7': 'pqrs', '8': 'tuv', '9': 'wxyz'}\n"
            "    result = ['']\n"
            "    for d in digits:\n"
            "        result = [p + c for p in result for c in mapping.get(d, '')]\n"
            "    return result"
        ),
        "incorrect": (
            "def letterCombinations(digits):\n"
            "    mapping = {'2': 'abc', '3': 'def', '4': 'ghi', '5': 'jkl',\n"
            "               '6': 'mno', '7': 'pqrs', '8': 'tuv', '9': 'wxyz'}\n"
            "    return [mapping[d] for d in digits if d in mapping]"
        ),
    },
    {
        "name": "4Sum",
        "difficulty": "Medium",
        "problem": (
            "Given an array nums of n integers, return an array of all the unique quadruplets "
            "[nums[a], nums[b], nums[c], nums[d]] such that a, b, c, d are distinct indices "
            "and nums[a] + nums[b] + nums[c] + nums[d] == target."
        ),
        "correct": (
            "def fourSum(nums, target):\n"
            "    nums.sort()\n"
            "    result = []\n"
            "    n = len(nums)\n"
            "    for i in range(n - 3):\n"
            "        if i > 0 and nums[i] == nums[i - 1]:\n"
            "            continue\n"
            "        for j in range(i + 1, n - 2):\n"
            "            if j > i + 1 and nums[j] == nums[j - 1]:\n"
            "                continue\n"
            "            left, right = j + 1, n - 1\n"
            "            while left < right:\n"
            "                s = nums[i] + nums[j] + nums[left] + nums[right]\n"
            "                if s == target:\n"
            "                    result.append([nums[i], nums[j], nums[left], nums[right]])\n"
            "                    while left < right and nums[left] == nums[left + 1]:\n"
            "                        left += 1\n"
            "                    while left < right and nums[right] == nums[right - 1]:\n"
            "                        right -= 1\n"
            "                    left += 1\n"
            "                    right -= 1\n"
            "                elif s < target:\n"
            "                    left += 1\n"
            "                else:\n"
            "                    right -= 1\n"
            "    return result"
        ),
        "partial": (
            "def fourSum(nums, target):\n"
            "    nums.sort()\n"
            "    result = []\n"
            "    n = len(nums)\n"
            "    for i in range(n - 3):\n"
            "        for j in range(i + 1, n - 2):\n"
            "            left, right = j + 1, n - 1\n"
            "            while left < right:\n"
            "                s = nums[i] + nums[j] + nums[left] + nums[right]\n"
            "                if s == target:\n"
            "                    result.append([nums[i], nums[j], nums[left], nums[right]])\n"
            "                    left += 1\n"
            "                    right -= 1\n"
            "                elif s < target:\n"
            "                    left += 1\n"
            "                else:\n"
            "                    right -= 1\n"
            "    return result"
        ),
        "incorrect": (
            "def fourSum(nums, target):\n"
            "    result = []\n"
            "    for i in range(len(nums)):\n"
            "        for j in range(len(nums)):\n"
            "            for k in range(len(nums)):\n"
            "                for l in range(len(nums)):\n"
            "                    if nums[i] + nums[j] + nums[k] + nums[l] == target:\n"
            "                        result.append([nums[i], nums[j], nums[k], nums[l]])\n"
            "    return result"
        ),
    },
    {
        "name": "Generate Parentheses",
        "difficulty": "Medium",
        "problem": (
            "Given n pairs of parentheses, write a function to generate all combinations "
            "of well-formed parentheses."
        ),
        "correct": (
            "def generateParenthesis(n):\n"
            "    result = []\n"
            "    def backtrack(s, open_count, close_count):\n"
            "        if len(s) == 2 * n:\n"
            "            result.append(s)\n"
            "            return\n"
            "        if open_count < n:\n"
            "            backtrack(s + '(', open_count + 1, close_count)\n"
            "        if close_count < open_count:\n"
            "            backtrack(s + ')', open_count, close_count + 1)\n"
            "    backtrack('', 0, 0)\n"
            "    return result"
        ),
        "partial": (
            "def generateParenthesis(n):\n"
            "    result = []\n"
            "    def backtrack(s, open_count, close_count):\n"
            "        if len(s) == 2 * n:\n"
            "            result.append(s)\n"
            "            return\n"
            "        if open_count < n:\n"
            "            backtrack(s + '(', open_count + 1, close_count)\n"
            "        if close_count < n:\n"
            "            backtrack(s + ')', open_count, close_count + 1)\n"
            "    backtrack('', 0, 0)\n"
            "    return result"
        ),
        "incorrect": (
            "def generateParenthesis(n):\n"
            "    return ['()' * n]"
        ),
    },
    # ── Hard (10) ─────────────────────────────────────────────────────────
    {
        "name": "Median of Two Sorted Arrays",
        "difficulty": "Hard",
        "problem": (
            "Given two sorted arrays nums1 and nums2 of size m and n respectively, "
            "return the median of the two sorted arrays. "
            "The overall run time complexity should be O(log (m+n))."
        ),
        "correct": (
            "def findMedianSortedArrays(nums1, nums2):\n"
            "    if len(nums1) > len(nums2):\n"
            "        nums1, nums2 = nums2, nums1\n"
            "    m, n = len(nums1), len(nums2)\n"
            "    lo, hi = 0, m\n"
            "    while lo <= hi:\n"
            "        i = (lo + hi) // 2\n"
            "        j = (m + n + 1) // 2 - i\n"
            "        max_left1 = float('-inf') if i == 0 else nums1[i - 1]\n"
            "        min_right1 = float('inf') if i == m else nums1[i]\n"
            "        max_left2 = float('-inf') if j == 0 else nums2[j - 1]\n"
            "        min_right2 = float('inf') if j == n else nums2[j]\n"
            "        if max_left1 <= min_right2 and max_left2 <= min_right1:\n"
            "            if (m + n) % 2 == 0:\n"
            "                return (max(max_left1, max_left2) + min(min_right1, min_right2)) / 2\n"
            "            else:\n"
            "                return max(max_left1, max_left2)\n"
            "        elif max_left1 > min_right2:\n"
            "            hi = i - 1\n"
            "        else:\n"
            "            lo = i + 1"
        ),
        "partial": (
            "def findMedianSortedArrays(nums1, nums2):\n"
            "    merged = sorted(nums1 + nums2)\n"
            "    n = len(merged)\n"
            "    if n % 2 == 0:\n"
            "        return (merged[n // 2 - 1] + merged[n // 2]) / 2\n"
            "    return merged[n // 2]"
        ),
        "incorrect": (
            "def findMedianSortedArrays(nums1, nums2):\n"
            "    m1 = nums1[len(nums1) // 2] if nums1 else 0\n"
            "    m2 = nums2[len(nums2) // 2] if nums2 else 0\n"
            "    return (m1 + m2) / 2"
        ),
    },
    {
        "name": "Regular Expression Matching",
        "difficulty": "Hard",
        "problem": (
            "Given an input string s and a pattern p, implement regular expression matching "
            "with support for '.' and '*' where:\n"
            "'.' Matches any single character.\n"
            "'*' Matches zero or more of the preceding element.\n"
            "The matching should cover the entire input string (not partial)."
        ),
        "correct": (
            "def isMatch(s, p):\n"
            "    memo = {}\n"
            "    def dp(i, j):\n"
            "        if (i, j) not in memo:\n"
            "            if j == len(p):\n"
            "                ans = i == len(s)\n"
            "            else:\n"
            "                first_match = i < len(s) and p[j] in {s[i], '.'}\n"
            "                if j + 1 < len(p) and p[j + 1] == '*':\n"
            "                    ans = dp(i, j + 2) or (first_match and dp(i + 1, j))\n"
            "                else:\n"
            "                    ans = first_match and dp(i + 1, j + 1)\n"
            "            memo[(i, j)] = ans\n"
            "        return memo[(i, j)]\n"
            "    return dp(0, 0)"
        ),
        "partial": (
            "def isMatch(s, p):\n"
            "    if not p:\n"
            "        return not s\n"
            "    first_match = bool(s) and p[0] in {s[0], '.'}\n"
            "    if len(p) >= 2 and p[1] == '*':\n"
            "        return isMatch(s, p[2:]) or (first_match and isMatch(s[1:], p))\n"
            "    return first_match and isMatch(s[1:], p[1:])"
        ),
        "incorrect": (
            "def isMatch(s, p):\n"
            "    import re\n"
            "    return bool(re.match(p, s))"
        ),
    },
    {
        "name": "Trapping Rain Water",
        "difficulty": "Hard",
        "problem": (
            "Given n non-negative integers representing an elevation map where the width of "
            "each bar is 1, compute how much water it can trap after raining."
        ),
        "correct": (
            "def trap(height):\n"
            "    if not height:\n"
            "        return 0\n"
            "    left, right = 0, len(height) - 1\n"
            "    left_max = right_max = 0\n"
            "    water = 0\n"
            "    while left < right:\n"
            "        if height[left] < height[right]:\n"
            "            if height[left] >= left_max:\n"
            "                left_max = height[left]\n"
            "            else:\n"
            "                water += left_max - height[left]\n"
            "            left += 1\n"
            "        else:\n"
            "            if height[right] >= right_max:\n"
            "                right_max = height[right]\n"
            "            else:\n"
            "                water += right_max - height[right]\n"
            "            right -= 1\n"
            "    return water"
        ),
        "partial": (
            "def trap(height):\n"
            "    n = len(height)\n"
            "    left_max = [0] * n\n"
            "    right_max = [0] * n\n"
            "    for i in range(n):\n"
            "        left_max[i] = max(left_max[i - 1], height[i]) if i > 0 else height[i]\n"
            "    for i in range(n - 1, -1, -1):\n"
            "        right_max[i] = max(right_max[i + 1], height[i]) if i < n - 1 else height[i]\n"
            "    return sum(min(left_max[i], right_max[i]) - height[i] for i in range(n))"
        ),
        "incorrect": (
            "def trap(height):\n"
            "    return sum(max(0, height[i] - height[i - 1]) for i in range(1, len(height)))"
        ),
    },
    {
        "name": "First Missing Positive",
        "difficulty": "Hard",
        "problem": (
            "Given an unsorted integer array nums, return the smallest missing positive integer. "
            "You must implement an algorithm that runs in O(n) time and uses O(1) auxiliary space."
        ),
        "correct": (
            "def firstMissingPositive(nums):\n"
            "    n = len(nums)\n"
            "    for i in range(n):\n"
            "        while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:\n"
            "            nums[nums[i] - 1], nums[i] = nums[i], nums[nums[i] - 1]\n"
            "    for i in range(n):\n"
            "        if nums[i] != i + 1:\n"
            "            return i + 1\n"
            "    return n + 1"
        ),
        "partial": (
            "def firstMissingPositive(nums):\n"
            "    s = set(nums)\n"
            "    for i in range(1, len(nums) + 2):\n"
            "        if i not in s:\n"
            "            return i"
        ),
        "incorrect": (
            "def firstMissingPositive(nums):\n"
            "    return max(nums) + 1 if nums else 1"
        ),
    },
    {
        "name": "N-Queens",
        "difficulty": "Hard",
        "problem": (
            "The n-queens puzzle is the problem of placing n queens on an n x n chessboard "
            "such that no two queens attack each other. "
            "Given an integer n, return all distinct solutions to the n-queens puzzle."
        ),
        "correct": (
            "def solveNQueens(n):\n"
            "    result = []\n"
            "    board = [-1] * n\n"
            "    def is_safe(row, col):\n"
            "        for r in range(row):\n"
            "            c = board[r]\n"
            "            if c == col or abs(c - col) == abs(r - row):\n"
            "                return False\n"
            "        return True\n"
            "    def backtrack(row):\n"
            "        if row == n:\n"
            "            result.append(['.' * c + 'Q' + '.' * (n - c - 1) for c in board])\n"
            "            return\n"
            "        for col in range(n):\n"
            "            if is_safe(row, col):\n"
            "                board[row] = col\n"
            "                backtrack(row + 1)\n"
            "                board[row] = -1\n"
            "    backtrack(0)\n"
            "    return result"
        ),
        "partial": (
            "def solveNQueens(n):\n"
            "    result = []\n"
            "    board = [-1] * n\n"
            "    def is_safe(row, col):\n"
            "        for r in range(row):\n"
            "            if board[r] == col:\n"
            "                return False\n"
            "        return True\n"
            "    def backtrack(row):\n"
            "        if row == n:\n"
            "            result.append(['.' * c + 'Q' + '.' * (n - c - 1) for c in board])\n"
            "            return\n"
            "        for col in range(n):\n"
            "            if is_safe(row, col):\n"
            "                board[row] = col\n"
            "                backtrack(row + 1)\n"
            "    backtrack(0)\n"
            "    return result"
        ),
        "incorrect": (
            "def solveNQueens(n):\n"
            "    result = []\n"
            "    board = [-1] * n\n"
            "    def backtrack(row):\n"
            "        if row == n:\n"
            "            result.append(['.' * c + 'Q' + '.' * (n - c - 1) for c in board])\n"
            "            return\n"
            "        for col in range(n):\n"
            "            board[row] = col\n"
            "            backtrack(row + 1)\n"
            "    backtrack(0)\n"
            "    return result"
        ),
    },
    {
        "name": "Wildcard Matching",
        "difficulty": "Hard",
        "problem": (
            "Given an input string s and a pattern p, implement wildcard pattern matching "
            "with support for '?' and '*' where:\n"
            "'?' Matches any single character.\n"
            "'*' Matches any sequence of characters (including the empty sequence).\n"
            "The matching should cover the entire input string (not partial)."
        ),
        "correct": (
            "def isMatch(s, p):\n"
            "    i = j = star = 0\n"
            "    match = -1\n"
            "    while i < len(s):\n"
            "        if j < len(p) and (p[j] == '?' or p[j] == s[i]):\n"
            "            i += 1\n"
            "            j += 1\n"
            "        elif j < len(p) and p[j] == '*':\n"
            "            star = j\n"
            "            match = i\n"
            "            j += 1\n"
            "        elif star != -1:\n"
            "            j = star + 1\n"
            "            match += 1\n"
            "            i = match\n"
            "        else:\n"
            "            return False\n"
            "    while j < len(p) and p[j] == '*':\n"
            "        j += 1\n"
            "    return j == len(p)"
        ),
        "partial": (
            "def isMatch(s, p):\n"
            "    memo = {}\n"
            "    def dp(i, j):\n"
            "        if (i, j) not in memo:\n"
            "            if j == len(p):\n"
            "                ans = i == len(s)\n"
            "            elif i == len(s):\n"
            "                ans = all(c == '*' for c in p[j:])\n"
            "            elif p[j] == '*':\n"
            "                ans = dp(i, j + 1) or dp(i + 1, j)\n"
            "            elif p[j] in {s[i], '?'}:\n"
            "                ans = dp(i + 1, j + 1)\n"
            "            else:\n"
            "                ans = False\n"
            "            memo[(i, j)] = ans\n"
            "        return memo[(i, j)]\n"
            "    return dp(0, 0)"
        ),
        "incorrect": (
            "def isMatch(s, p):\n"
            "    return s == p"
        ),
    },
    {
        "name": "Edit Distance",
        "difficulty": "Hard",
        "problem": (
            "Given two strings word1 and word2, return the minimum number of operations "
            "required to convert word1 to word2. You have three operations: "
            "Insert a character, Delete a character, Replace a character."
        ),
        "correct": (
            "def minDistance(word1, word2):\n"
            "    m, n = len(word1), len(word2)\n"
            "    dp = [[0] * (n + 1) for _ in range(m + 1)]\n"
            "    for i in range(m + 1):\n"
            "        dp[i][0] = i\n"
            "    for j in range(n + 1):\n"
            "        dp[0][j] = j\n"
            "    for i in range(1, m + 1):\n"
            "        for j in range(1, n + 1):\n"
            "            if word1[i - 1] == word2[j - 1]:\n"
            "                dp[i][j] = dp[i - 1][j - 1]\n"
            "            else:\n"
            "                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])\n"
            "    return dp[m][n]"
        ),
        "partial": (
            "def minDistance(word1, word2):\n"
            "    m, n = len(word1), len(word2)\n"
            "    dp = [[0] * (n + 1) for _ in range(m + 1)]\n"
            "    for i in range(m + 1):\n"
            "        dp[i][0] = i\n"
            "    for j in range(n + 1):\n"
            "        dp[0][j] = j\n"
            "    for i in range(1, m + 1):\n"
            "        for j in range(1, n + 1):\n"
            "            if word1[i - 1] == word2[j - 1]:\n"
            "                dp[i][j] = dp[i - 1][j - 1]\n"
            "            else:\n"
            "                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1])\n"
            "    return dp[m][n]"
        ),
        "incorrect": (
            "def minDistance(word1, word2):\n"
            "    return abs(len(word1) - len(word2))"
        ),
    },
    {
        "name": "Minimum Window Substring",
        "difficulty": "Hard",
        "problem": (
            "Given two strings s and t of lengths m and n respectively, return the minimum window "
            "substring of s such that every character in t (including duplicates) is included in "
            "the window. If there is no such substring, return the empty string \"\"."
        ),
        "correct": (
            "def minWindow(s, t):\n"
            "    from collections import Counter\n"
            "    need = Counter(t)\n"
            "    have = Counter()\n"
            "    formed = 0\n"
            "    required = len(need)\n"
            "    left = 0\n"
            "    best = (float('inf'), 0, len(s) - 1)\n"
            "    for right, ch in enumerate(s):\n"
            "        have[ch] += 1\n"
            "        if ch in need and have[ch] == need[ch]:\n"
            "            formed += 1\n"
            "        while formed == required:\n"
            "            if right - left + 1 < best[0]:\n"
            "                best = (right - left + 1, left, right)\n"
            "            have[s[left]] -= 1\n"
            "            if s[left] in need and have[s[left]] < need[s[left]]:\n"
            "                formed -= 1\n"
            "            left += 1\n"
            "    return s[best[1]:best[2] + 1] if best[0] != float('inf') else ''"
        ),
        "partial": (
            "def minWindow(s, t):\n"
            "    from collections import Counter\n"
            "    need = Counter(t)\n"
            "    best = ''\n"
            "    for i in range(len(s)):\n"
            "        for j in range(i + len(t), len(s) + 1):\n"
            "            if Counter(s[i:j]) >= need:\n"
            "                if not best or j - i < len(best):\n"
            "                    best = s[i:j]\n"
            "    return best"
        ),
        "incorrect": (
            "def minWindow(s, t):\n"
            "    return t if t in s else ''"
        ),
    },
    {
        "name": "Largest Rectangle in Histogram",
        "difficulty": "Hard",
        "problem": (
            "Given an array of integers heights representing the histogram's bar height where "
            "the width of each bar is 1, return the area of the largest rectangle in the histogram."
        ),
        "correct": (
            "def largestRectangleArea(heights):\n"
            "    stack = []\n"
            "    max_area = 0\n"
            "    for i, h in enumerate(heights):\n"
            "        start = i\n"
            "        while stack and stack[-1][1] > h:\n"
            "            idx, height = stack.pop()\n"
            "            max_area = max(max_area, height * (i - idx))\n"
            "            start = idx\n"
            "        stack.append((start, h))\n"
            "    for i, h in stack:\n"
            "        max_area = max(max_area, h * (len(heights) - i))\n"
            "    return max_area"
        ),
        "partial": (
            "def largestRectangleArea(heights):\n"
            "    max_area = 0\n"
            "    for i in range(len(heights)):\n"
            "        min_h = heights[i]\n"
            "        for j in range(i, len(heights)):\n"
            "            min_h = min(min_h, heights[j])\n"
            "            max_area = max(max_area, min_h * (j - i + 1))\n"
            "    return max_area"
        ),
        "incorrect": (
            "def largestRectangleArea(heights):\n"
            "    return max(heights) * len(heights)"
        ),
    },
    {
        "name": "Sliding Window Maximum",
        "difficulty": "Hard",
        "problem": (
            "You are given an array of integers nums, and a sliding window of size k which is "
            "moving from the very left of the array to the very right. Return the max value in "
            "each window. You must solve it in O(n) time."
        ),
        "correct": (
            "def maxSlidingWindow(nums, k):\n"
            "    from collections import deque\n"
            "    dq = deque()\n"
            "    result = []\n"
            "    for i, n in enumerate(nums):\n"
            "        while dq and nums[dq[-1]] <= n:\n"
            "            dq.pop()\n"
            "        dq.append(i)\n"
            "        if dq[0] == i - k:\n"
            "            dq.popleft()\n"
            "        if i >= k - 1:\n"
            "            result.append(nums[dq[0]])\n"
            "    return result"
        ),
        "partial": (
            "def maxSlidingWindow(nums, k):\n"
            "    return [max(nums[i:i + k]) for i in range(len(nums) - k + 1)]"
        ),
        "incorrect": (
            "def maxSlidingWindow(nums, k):\n"
            "    return [max(nums)] * (len(nums) - k + 1)"
        ),
    },
]


def main():
    doctor = LLMDoctor()
    total = 0
    correct = 0
    results = []
    checker_fires = Counter()
    blind_spots = []  # (problem, solution_type, expected, got)

    print("=" * 70)
    print("PRODUCTION SCALE TEST — 29 Problems x 3 Solutions = 87 Cases")
    print("=" * 70)

    for prob in PROBLEMS:
        name = prob["name"]
        difficulty = prob["difficulty"]
        problem = prob["problem"]

        print(f"\n{'─' * 70}")
        print(f"  {name} ({difficulty})")
        print(f"{'─' * 70}")

        for sol_type in ["correct", "partial", "incorrect"]:
            total += 1
            code = prob[sol_type]
            prompt = f"PROBLEM: {problem}\n\nSOLUTION:\n{code}"
            result = doctor.predict(prompt)
            predicted = result["label"]
            confidence = result["confidence"]
            bias = result.get("system_bias_indicators", {})
            reasoning = bias.get("llm_reasoning", "")
            issues = bias.get("llm_issues", [])
            details = bias.get("analyzer_details", {})

            # Map expected → what we consider correct:
            # "correct" → "correct"
            # "partial" → "partial"
            # "incorrect" → "incorrect"
            match = (predicted == sol_type)
            if match:
                correct += 1
            else:
                blind_spots.append((name, sol_type, sol_type, predicted))

            marker = "✓" if match else "✗"
            issue_str = f" [{', '.join(issues)}]" if issues else ""
            # Show Layer 2 info if activated
            l2_info = ""
            if bias.get("layer2_activated"):
                l2v = bias.get("layer2_verdict", "?")
                l2pr = bias.get("layer2_pass_rate", 0)
                override = bias.get("conflict_detected", False)
                if override:
                    l2_info = f" [L2 override: {l2v} {l2pr:.0%}]"
            print(f"  [{marker}] {sol_type:12s} -> {predicted:12s} (conf={confidence:.2f}){issue_str}{l2_info}")

            # Track checker fires
            if details:
                for check_name, passed in details.items():
                    if not passed:
                        checker_fires[check_name] += 1

            results.append({
                "problem": name,
                "difficulty": difficulty,
                "solution_type": sol_type,
                "expected": sol_type,
                "predicted": predicted,
                "confidence": confidence,
                "issues": issues,
                "correct": match,
            })

    # ── Summary ──────────────────────────────────────────────────────────
    print(f"\n{'=' * 70}")
    print(f"RESULTS: {correct}/{total} ({correct / total * 100:.1f}%)")
    print(f"{'=' * 70}")

    # By difficulty
    by_diff = {}
    for r in results:
        d = r["difficulty"]
        if d not in by_diff:
            by_diff[d] = {"total": 0, "correct": 0}
        by_diff[d]["total"] += 1
        if r["correct"]:
            by_diff[d]["correct"] += 1

    print(f"\nBy difficulty:")
    for d in ["Easy", "Medium", "Hard"]:
        data = by_diff.get(d, {"total": 0, "correct": 0})
        print(f"  {d:6s}: {data['correct']}/{data['total']} ({data['correct'] / data['total'] * 100:.0f}%)")

    # By solution type
    by_type = {}
    for r in results:
        t = r["solution_type"]
        if t not in by_type:
            by_type[t] = {"total": 0, "correct": 0}
        by_type[t]["total"] += 1
        if r["correct"]:
            by_type[t]["correct"] += 1

    print(f"\nBy solution type:")
    for t in ["correct", "partial", "incorrect"]:
        data = by_type.get(t, {"total": 0, "correct": 0})
        print(f"  {t:12s}: {data['correct']}/{data['total']} ({data['correct'] / data['total'] * 100:.0f}%)")

    # Checker coverage
    print(f"\nChecker coverage (fires across all {total} cases):")
    for checker, count in sorted(checker_fires.items(), key=lambda x: -x[1]):
        print(f"  {checker:40s}: {count:3d} fires ({count / total * 100:.1f}%)")

    # Blind spots
    if blind_spots:
        print(f"\nBlind spots ({len(blind_spots)} misclassifications):")
        for name, sol_type, expected, got in blind_spots:
            print(f"  {name:40s} {sol_type:12s} → {got}")

        # Group by pattern
        from collections import defaultdict
        patterns = defaultdict(list)
        for name, sol_type, expected, got in blind_spots:
            patterns[(expected, got)].append(name)
        print(f"\nMisclassification patterns:")
        for (exp, got), names in sorted(patterns.items()):
            print(f"  {exp:12s} → {got:12s}: {len(names)} cases")
            for n in names:
                print(f"    - {n}")

    # Save results
    output_path = project_root / "tests" / "production_87_results.json"
    with open(output_path, "w") as f:
        json.dump({
            "total": total,
            "correct": correct,
            "accuracy": correct / total,
            "by_difficulty": {d: by_diff.get(d, {}) for d in ["Easy", "Medium", "Hard"]},
            "by_type": by_type,
            "checker_fires": dict(checker_fires),
            "blind_spots": [{"problem": n, "type": s, "expected": e, "got": g}
                            for n, s, e, g in blind_spots],
        }, f, indent=2)
    print(f"\nResults saved to {output_path}")


if __name__ == "__main__":
    main()
