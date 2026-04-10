from typing import List


class Solution:
    @staticmethod
    def maxSubarrayLength(nums: List[int], k: int) -> int:
        """
        Sliding window solution, Hash Table
        """
        counter = {}
        n = len(nums)

        left = 0
        right = 0

        largest = 0

        while right < n:
            # Expand the window and update the frequency count
            counter[nums[right]] = counter.get(nums[right], 0) + 1

            # Shrink the window until the frequency condition is satisfied
            while counter[nums[right]] > k:
                counter[nums[left]] -= 1
                left += 1

            # Update the length of the longest good subarray
            largest = max(largest, right - left + 1)

            # Move the right pointer to expand the window
            right += 1

        return largest


# Test the Solution class with the provided test cases
if __name__ == '__main__':
    print(Solution.maxSubarrayLength(nums=[1, 2, 3, 1, 2, 3, 1, 2], k=2))
    print(Solution.maxSubarrayLength(nums=[1, 2, 1, 2, 1, 2, 1, 2], k=1))
    print(Solution.maxSubarrayLength(nums=[5, 5, 5, 5, 5, 5, 5], k=4))
