from typing import List


class Solution:
    @staticmethod
    def combinationSum(candidates: List[int], target: int) -> List[List[int]]:
        def backtrack(start, path, current_sum):
            if current_sum == target:
                result.append(path[:])
                return

            for i in range(start, len(candidates)):
                # Skip duplicates to avoid duplicate combinations
                if i > start and candidates[i] == candidates[i - 1]:
                    continue

                # Prune the search space if remaining is not achievable
                if current_sum + candidates[i] > target:
                    continue

                # Make choice
                path.append(candidates[i])

                # Recur with the next index (i + 1) to avoid using the same element again
                backtrack(i + 1, path, current_sum + candidates[i])

                # Undo choice
                path.pop()

        result = []
        candidates.sort()  # Sort to group duplicates together
        backtrack(0, [], 0)
        return result


# Example usage
sol = Solution()
print(sol.combinationSum(
    [14, 6, 25, 9, 30, 20, 33, 34, 28, 30, 16, 12, 31, 9, 9, 12, 34, 16, 25, 32, 8, 7, 30, 12, 33, 20, 21, 29, 24, 17,
     27, 34, 11, 17, 30, 6, 32, 21, 27, 17, 16, 8, 24, 12, 12, 28, 11, 33, 10, 32, 22, 13, 34, 18, 12],
    27))
