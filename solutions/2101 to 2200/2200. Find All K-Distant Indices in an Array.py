from typing import List


class Solution:
    @staticmethod
    def findKDistantIndices(nums: List[int], key: int, k: int) -> List[int]:
        # Get the length of the input list
        length = len(nums)

        # Initialize a list to store the indices where the key occurs
        # Adding float('-inf') at the beginning to handle edge cases
        key_indices = [float('-inf')]

        # Iterate through the list with both index and value
        for index, value in enumerate(nums):
            # If the current value is equal to the key
            if value == key:
                # Append the current index to the list key_indices
                key_indices.append(index)

        # Append float('inf') at the end to handle edge cases
        key_indices.append(float('inf'))

        # Initialize a pointer to track the current position in list key_indices
        current_key_index = 0

        # Initialize an empty list to store the result indices
        k_distant_indices = []

        # Iterate through all indices of the input list
        for i in range(length):
            # Check if the current index i is within k distance of key_indices[current_key_index] or key_indices[
            # current_key_index + 1]
            if i <= key_indices[current_key_index] + k or key_indices[current_key_index + 1] - k <= i:
                # If it is, add the index i to the result list
                k_distant_indices.append(i)

            # If the current index matches key_indices[current_key_index + 1], move the pointer to the next key index
            if key_indices[current_key_index + 1] == i:
                current_key_index += 1

        # Return the list of k-distant indices
        return k_distant_indices


# Example usage:
solution = Solution()
print(solution.findKDistantIndices([1, 2, 3, 4, 5], 3, 1))  # Example output: [1, 2, 3, 4]
