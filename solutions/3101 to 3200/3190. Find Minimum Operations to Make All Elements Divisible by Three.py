from typing import List


class Solution:
    @staticmethod
    def minimumOperations(nums: List[int]) -> int:
        ans = 0
        for num in nums:
            # If the remainder when num is divided by 3 is 2, add 1 operation
            if num % 3 == 2:
                ans += 1
            # Otherwise, add the remainder itself (could be 0 or 1)
            else:
                ans += (num % 3)
        return ans


if __name__ == '__main__':
    # Example usage
    print(Solution.minimumOperations([1, 2, 3, 4]))  # Output: 3
    print(Solution.minimumOperations([]))  # Output: 0
    print(Solution.minimumOperations([3, 6, 9]))  # Output: 0
    print(Solution.minimumOperations([2, 5, 8, 11]))  # Output: 4
    print(Solution.minimumOperations([999999, 1000001]))  # Output: 2