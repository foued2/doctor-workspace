from typing import List


class Solution:
    @staticmethod
    def findDisappearedNumbers(nums: List[int]) -> List[int]:
        res = []
        num_set = set(nums)  # Create a set of unique numbers in the array

        # Iterate from 1 to the length of the array
        for i in range(1, len(nums) + 1):
            # If the current number is not in the set, it's a disappeared number
            if i not in num_set:
                res.append(i)

        return res


# Example usage:
if __name__ == "__main__":
    solution = Solution()
    print(solution.findDisappearedNumbers(nums=[4, 3, 2, 7, 8, 2, 3, 1]))  # Output: [5, 6]
    print(solution.findDisappearedNumbers(nums=[1, 1]))  # Output: [2]
