from typing import List


class Solution:
    @staticmethod
    def sortEvenOdd(nums: List[int]) -> List[int]:
        """
        Sorting
        """
        # Initialize two lists to store elements at even and odd indices
        even_indexed_elements = []
        odd_indexed_elements = []

        # Separate the elements based on their indices
        for i in range(len(nums)):
            if i % 2 == 0:
                # Append elements at even indices to even_indexed_elements
                even_indexed_elements.append(nums[i])
            else:
                # Append elements at odd indices to odd_indexed_elements
                odd_indexed_elements.append(nums[i])

        # Sort even indexed elements in descending order
        even_indexed_elements = sorted(even_indexed_elements, reverse=True)
        # Sort odd indexed elements in ascending order
        odd_indexed_elements = sorted(odd_indexed_elements)

        # Initialize the result list
        result = []

        # Merge the sorted even and odd indexed elements back into the result list
        for i in range(len(nums)):
            if i % 2 == 0:
                # Pop from the end of even_indexed_elements and append to result
                result.append(even_indexed_elements.pop())
            else:
                # Pop from the end of odd_indexed_elements and append to result
                result.append(odd_indexed_elements.pop())

        return result


# Example usage
solution = Solution()
print(solution.sortEvenOdd([4, 1, 2, 3]))  # Expected output: [2, 1, 4, 3]
print(solution.sortEvenOdd([2, 1]))  # Expected output: [2, 1]
print(solution.sortEvenOdd([3, 5, 2, 8, 1, 4]))  # Expected output: [2, 1, 3, 4, 8, 5]
