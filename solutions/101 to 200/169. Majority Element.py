from typing import List


class Solution:
    @staticmethod
    def majorityElement(nums: List[int]) -> int:
        # Boyer-Moore Majority Vote Algorithm:
        # Step 1: Initialize variables to keep track of the candidate and its count.
        candidate = None
        count = 0

        # Step 2: Find the potential candidate for the majority element.
        # Traverse through the array.
        for num in nums:
            # If the count is 0, the current element becomes a potential candidate.
            if count == 0:
                candidate = num
            # If the current element equals the candidate, increment the count.
            if num == candidate:
                count += 1
            else:
                count -= 1

        # Step 3: Verify if the candidate is the majority element by counting its occurrences.
        count = 0
        for num in nums:
            if num == candidate:
                count += 1

        # If the count of the candidate exceeds half the length of the array,
        # return it as the majority element; otherwise, return -1.
        if count > len(nums) / 2:
            return candidate
        else:
            return -1  # No majority element found


# Test the majorityElement method
print(Solution.majorityElement([2, 2, 1, 1, 1, 2, 2]))  # Output should be 2
