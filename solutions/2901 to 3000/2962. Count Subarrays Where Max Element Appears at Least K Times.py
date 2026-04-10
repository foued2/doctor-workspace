from typing import List


class Solution:
    @staticmethod
    def countSubarrays(nums: List[int], k: int) -> int:
        """
        Sliding Window
        """
        # Initialize the maximum element found so far and its positions
        max_element = nums[0]
        max_positions = [0]
        n = len(nums)

        # Iterate through the list to find the maximum element and its positions
        for i in range(1, n):
            if nums[i] > max_element:
                max_element = nums[i]
                max_positions = [i]
            elif nums[i] == max_element:
                max_positions.append(i)

        # If the number of positions where the maximum element appears is less than 'k', no subarrays can satisfy the
        # condition
        if len(max_positions) < k:
            return 0

        # Initialize the count of subarrays and the index of the last position
        subarray_count = 0
        last_position_index = -1

        # Iterate through the positions where the maximum element appears
        for left in range(len(max_positions) - k + 1):
            # Calculate the count of subarrays that satisfy the condition
            subarray_count += (n - max_positions[left + k - 1]) * (max_positions[left] - last_position_index)
            # Update the index of the last position
            last_position_index = max_positions[left]

        return subarray_count


if __name__ == '__main__':
    print(Solution.countSubarrays(nums=[1, 3, 2, 3, 3], k=2))
    print(Solution.countSubarrays(nums=[1, 4, 2, 1], k=3))
    print(Solution.countSubarrays(nums=[61, 23, 38, 23, 56, 40, 82, 56, 82], k=2))
    print(Solution.countSubarrays(
        nums=[61, 23, 38, 23, 56, 40, 82, 56, 82, 82, 82, 70, 8, 69, 8, 7, 19, 14, 58, 42, 82, 10, 82, 78, 15, 82],
        k=2))
