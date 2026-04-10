from typing import List


class Solution:
    @staticmethod
    def permute(nums: List[int]) -> List[List[int]]:
        def backtrack(start, path, nums, k):
            # Base case
            if k == 0:
                result.append(path[:])
                return

            for j in range(start, len(nums)):
                # Make choice
                path.append(nums[j])

                # Recur with the next element
                backtrack(start, path, nums[:j] + nums[j + 1:], k - 1)

                # Undo choice
                path.pop()

        result = []
        backtrack(0, [], nums, 4)
        return result


# Example usage
solution = Solution()
print(solution.permute([1, 2, 3, 4, 5, 6, 7]))
