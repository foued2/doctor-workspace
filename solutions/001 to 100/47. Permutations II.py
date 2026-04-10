from typing import List


class Solution:
    @staticmethod
    def permuteUnique(nums: List[int]) -> List[List[int]]:
        def backtrack(start, path, nums, k):
            # Base case
            if k == 0:
                result.append(path[:])
                return

            for j in range(start, len(nums)):
                # Skip duplicates to avoid duplicate combinations
                if j > start and nums[j] == nums[j - 1]:
                    continue

                # Make choice
                path.append(nums[j])

                # Recur with the next element
                backtrack(start, path, nums[:j] + nums[j + 1:], k - 1)

                # Undo choice
                path.pop()

        result = []
        # Sort candidates to handle duplicates and for a more organized output
        nums = sorted(nums)
        backtrack(0, [], nums, len(nums))
        return result


# Example usage
solution = Solution()
print(solution.permuteUnique(nums=[3, 3, 0, 3]))
