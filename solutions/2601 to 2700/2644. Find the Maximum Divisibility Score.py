from typing import List


class Solution:
    @staticmethod
    def maxDivScore(nums: List[int], divisors: List[int]) -> int:
        # Convert the list of divisors to a set to remove duplicates and allow for efficient lookup
        div_set = set(divisors)

        # Initialize the result variable to store the divisor with the maximum score
        res = 0

        # Initialize the maximum value variable to store the highest score found
        max_val = 0

        # Sort the set of divisors and consider only the first 8 for efficiency
        # If there are fewer than 8 divisors, it will consider all available
        for divisor in sorted(div_set)[:8]:
            # Initialize the current score for the current divisor
            cur = 0

            # Check each number in the list to see if it is divisible by the current divisor
            for num in nums:
                if num % divisor == 0:
                    # Increment the current score if the number is divisible by the current divisor
                    cur += 1

            # If the current score is greater than the maximum value found so far
            if cur > max_val:
                # Update the maximum value with the current score
                max_val = cur

                # Update the result with the current divisor
                res = divisor

        # If no divisor was found that divides any number in the list, return the smallest divisor
        if res == 0:
            return min(div_set)

        # Return the divisor with the maximum score
        return res


print(Solution.maxDivScore(
    nums = [56, 22, 79, 41, 8, 39, 81, 59, 74, 14, 45, 49, 15, 10, 28, 16, 77, 22, 65, 8, 36, 79, 94, 44, 80, 72, 8, 96,
            78],
    divisors = [39, 92, 69, 55, 9, 44, 26, 76, 40, 77, 16, 69, 40, 64, 12, 48, 66, 7, 59, 10, 33, 72, 97, 60, 79, 68,
                25,
                63]))
