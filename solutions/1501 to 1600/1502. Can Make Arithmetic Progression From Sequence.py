from typing import List


class Solution:
    @staticmethod
    def canMakeArithmeticProgression(arr: List[int]) -> bool:
        # Sort the input list
        arr = sorted(arr)

        # Calculate the common difference between consecutive elements
        diff = arr[1] - arr[0]

        # Iterate through the list starting from the second element
        for i in range(1, len(arr) - 1):
            # Check if the difference between consecutive elements is equal to the common difference
            if arr[i + 1] - arr[i] != diff:
                # If not, the list does not form an arithmetic progression
                return False

        # If all differences are equal to the common difference, the list forms an arithmetic progression
        return True


if __name__ == '__main__':
    print(Solution.canMakeArithmeticProgression(arr=[1, 2, 4]))
