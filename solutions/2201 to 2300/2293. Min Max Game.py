from typing import List


class Solution:
    @staticmethod
    def minMaxGame(nums: List[int]) -> int:
        """
        Recursion
        """
        # Base case: if there's only one element, return it
        if len(nums) == 1:
            return nums[0]

        # Calculate the new list based on min-max rules
        new_nums = []
        for i in range(len(nums) // 2):
            if i % 2 == 0:
                # For even index pairs (0, 2, 4, ...), use min
                new_nums.append(min(nums[2 * i], nums[2 * i + 1]))
            else:
                # For odd index pairs (1, 3, 5, ...), use max
                new_nums.append(max(nums[2 * i], nums[2 * i + 1]))

        # Recursively call the function with the new list
        return Solution.minMaxGame(new_nums)


# Example usage
solution = Solution()
nums = [93, 40]
print(solution.minMaxGame(nums))  # Output: 40

print(Solution.minMaxGame(nums=[1, 3, 5, 2, 4, 8, 2, 2]))
