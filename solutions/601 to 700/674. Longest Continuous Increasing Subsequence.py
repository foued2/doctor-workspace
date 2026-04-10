from typing import List


class Solution:
    @staticmethod
    def findLengthOfLCIS(nums: List[int]) -> int:
        """
        Sliding Window
        """
        longest = 0  # Initialize the maximum length of LCIS
        current = 0  # Initialize the current length of LCIS
        n = len(nums)  # Get the length of the input list

        for i in range(n):
            # Check if we are at the start or current element is larger than the previous one
            # For the first element, there's no previous element to compare it with.
            # In this case, nums[i - 1] < nums[i] does not make sense since nums[-1] would refer
            # to an element that doesn't exist in the context of checking for a strictly increasing subsequence.
            if i == 0 or nums[i - 1] < nums[i]:
                current += 1  # Increment the current length of LCIS
                # Update the longest if current length of LCIS is greater
                longest = max(longest, current)
            else:
                current = 1  # Reset current length of LCIS to 1

        return longest  # Return the length of the longest continuous increasing subsequence


# Example usage
if __name__ == "__main__":
    print(Solution().findLengthOfLCIS([1, 3, 5, 4, 7]))  # Output: 3


class Solution:
    @staticmethod
    def findLengthOfLCIS(nums: List[int]) -> int:
        """
        Dynamic Programming
        """
        if not nums:
            return 0

        n = len(nums)
        dp = [1] * n  # Initialize DP array
        for i in range(1, n):
            if nums[i] > nums[i - 1]:
                dp[i] = dp[i - 1] + 1  # Transition relation

        # The answer will be the maximum value in the DP array
        return max(dp)


if __name__ == "__main__":
    print(Solution().findLengthOfLCIS([1, 3, 5, 4, 7]))  # Output: 3


from itertools import accumulate, starmap, pairwise
from operator import lt


class Solution:
    @staticmethod
    def findLengthOfLCIS(nums: list[int]) -> int:
        # pairwise(nums) generates pairs of consecutive elements from the nums list.
        # For example, pairwise([1, 3, 5, 4, 7]) will produce: [(1, 3), (3, 5), (5, 4), (4, 7)]
        pairs = pairwise(nums)

        # starmap(lt, pairwise(nums)) applies the 'lt' (less than) operator to each pair.
        # It produces an iterable of Boolean values indicating if the first element of the pair is less than the second.
        # For example, starmap(lt, [(1, 3), (3, 5), (5, 4), (4, 7)]) will produce: [True, True, False, True]
        is_increasing = starmap(lt, pairs)

        # accumulate(is_increasing, lambda a, x: a * x + 1, initial=1) processes the iterable of Booleans to count the length
        # of continuous increasing subsequences and immediately find the max length.
        # The function (lambda a, x: a * x + 1) updates the running total:
        # - If 'x' is True (the sequence is increasing), it increments the count by 1.
        # - If 'x' is False (the sequence is not increasing), it resets the running total to 1.
        # The 'initial=1' parameter starts the count from 1.

        # Example breakdown for accumulate([True, True, False, True], lambda a, x: a * x + 1, initial=1):
        # - Start with initial=1.
        # - First element (True): 1 * True + 1 = 2
        # - Second element (True): 2 * True + 1 = 3
        # - Third element (False): 3 * False + 1 = 1 (reset count)
        # - Fourth element (True): 1 * True + 1 = 2

        # The final result from 'accumulate' will be an iterable: [1, 2, 3, 1, 2]

        # The max function finds the maximum value in this iterable, which is the length of LCIS.
        max_length = max(accumulate(is_increasing, lambda a, x: a * x + 1, initial=1))

        return max_length  # Return the length of the longest continuous increasing subsequence


# Example usage
if __name__ == "__main__":
    print(Solution().findLengthOfLCIS([1, 3, 5, 4, 7]))  # Output: 3