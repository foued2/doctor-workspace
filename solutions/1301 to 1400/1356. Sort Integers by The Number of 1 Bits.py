from typing import List


class Solution:
    @staticmethod
    def sortByBits(arr: List[int]) -> List[int]:
        """
        Double sort
        """
        # Step 1: Create a list of tuples where each tuple contains the number and its bit count
        bit_counts = [(num, bin(num).count('1')) for num in arr]

        # Step 2: Sort the list of tuples first by the bit count, then by the number itself
        bit_counts.sort(key=lambda x: (x[1], x[0]))

        # Step 3: Extract the sorted numbers from the sorted list of tuples
        sorted_numbers = [num for num, bit_count in bit_counts]

        return sorted_numbers


# Example usage:
arr = [0, 1, 2, 3, 4, 5, 6, 7, 8]
result = Solution.sortByBits(arr)
print(result)  # Output should be [0, 1, 2, 4, 8, 3, 5, 6, 7]

print(Solution.sortByBits(arr=[1024, 512, 256, 128, 64, 32, 16, 8, 4, 2, 1]))
