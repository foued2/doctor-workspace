from typing import List


class Solution:
    @staticmethod
    def combinationSum(candidates: List[int], target: int) -> List[List[int]]:
        def backtrack(start, path, current_sum):
            # Base case
            if current_sum == target:
                result.append(path[:])
                return

            # Explore choices
            for i in range(start, len(candidates)):
                # Pruning: Skip candidates that would exceed the target
                if current_sum + candidates[i] > target:
                    continue

                # Make choice
                path.append(candidates[i])

                # Recur with the same problem size (current_sum)
                backtrack(i, path, current_sum + candidates[i])

                # Undo choice
                path.pop()

        # Initialize result list
        result = []

        # Sort candidates to handle duplicates and for a more organized output
        candidates = sorted(candidates)

        # Start the backtracking process
        backtrack(0, [], 0)

        return result


# Example usage
sol = Solution()
print(sol.combinationSum([2, 3, 5], 8))
