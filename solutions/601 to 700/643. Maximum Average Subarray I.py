from typing import List


class Solution:
    @staticmethod
    def findMaxAverage(nums: List[int], k: int) -> float:
        # Calculate the sum of the first k elements
        window_sum = sum(nums[:k])
        max_aver_value = window_sum / k  # Initialize max average

        # Iterate through the array starting from index k
        for i in range(k, len(nums)):
            # Slide the window by one element
            window_sum += nums[i] - nums[i - k]
            # Calculate the average of the current window
            max_aver_count = window_sum / k
            # Update max average if necessary
            max_aver_value = max(max_aver_value, max_aver_count)

        return max_aver_value


if __name__ == '__main__':
    print(Solution.findMaxAverage(nums=[1, 12, -5, -6, 50, 3], k=4))
