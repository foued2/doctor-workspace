import sys
sys.path.insert(0, '.')
from doctor import solution_normalizer

test_cases = [
    # 1. Raw function
    ('Raw function', '''def twoSum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
'''),

    # 2. Class-wrapped with typing
    ('Class + typing', '''from typing import List
class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        seen = {}
        for i, num in enumerate(nums):
            complement = target - num
            if complement in seen:
                return [seen[complement], i]
            seen[num] = i
        return []
'''),

    # 3. Class-wrapped with docstring
    ('Class + docstring', '''class Solution:
    def twoSum(self, nums, target):
        """Find two indices that add to target."""
        seen = {}
        for i, num in enumerate(nums):
            complement = target - num
            if complement in seen:
                return [seen[complement], i]
            seen[num] = i
        return []
'''),

    # 4. With List from typing shadowing
    ('Typing shadow', '''from typing import List, Optional
def mergeTwoLists(l1, l2):
    dummy = ListNode()
    curr = dummy
    while l1 and l2:
        if l1.val <= l2.val:
            curr.next = l1
            l1 = l1.next
        else:
            curr.next = l2
            l2 = l2.next
        curr = curr.next
    curr.next = l1 or l2
    return dummy.next
'''),

    # 5. Multiple classes
    ('Multiple classes', '''class Helper:
    def process(self, x):
        return x * 2

class Solution:
    def twoSum(self, nums, target):
        seen = {}
        for i, num in enumerate(nums):
            complement = target - num
            if complement in seen:
                return [seen[complement], i]
            seen[num] = i
        return []
'''),

    # 6. Nested type hints
    ('Nested hints', '''from typing import List, Dict, Tuple
class Solution:
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
        groups = {}
        for s in strs:
            key = tuple(sorted(s))
            if key not in groups:
                groups[key] = []
            groups[key].append(s)
        return list(groups.values())
'''),
]

print('='*60)
print('SOLUTION NORMALIZER TEST RESULTS')
print('='*60)

all_passed = True
for name, code in test_cases:
    try:
        normalizer = solution_normalizer.SolutionNormalizer()
        normalized = normalizer.normalize(code)
        func = solution_normalizer.extract_function(normalized)
        if func:
            print(f'[PASS] {name}: extracted {func.__name__}')
        else:
            print(f'[FAIL] {name}: no function extracted')
            all_passed = False
    except Exception as e:
        print(f'[FAIL] {name}: {str(e)[:60]}')
        all_passed = False

print('='*60)
print(f'Results: {"ALL PASSED" if all_passed else "SOME FAILED"}')
