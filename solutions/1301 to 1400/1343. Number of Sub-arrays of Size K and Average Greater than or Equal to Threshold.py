from typing import List


class Solution:
    @staticmethod
    def numOfSubarrays(arr: List[int], k: int, threshold: int) -> int:
        # Initialize the count of valid subarrays to zero.
        ans = 0
        # Get the length of the input array.
        n = len(arr)
        # Calculate the threshold sum to compare against.
        bar = k * threshold
        # Initialize the index for the sliding window.
        i = 1
        # Calculate the sum of the first 'k' elements.
        curr_sum = sum(arr[:k])

        # Check if the sum of the first 'k' elements meets or exceeds the threshold.
        if curr_sum >= bar:
            ans += 1

        # Slide the window across the array, one element at a time.
        while k < n:
            # Subtract the element leaving the window.
            curr_sum -= arr[i - 1]
            # Add the new element entering the window.
            curr_sum += arr[k]

            # Check if the new window sum meets or exceeds the threshold.
            if curr_sum >= bar:
                ans += 1

            # Move the window one element forward.
            i += 1
            k += 1

        # Return the total count of valid subarrays.
        return ans


print(Solution.numOfSubarrays(arr=[11, 13, 17, 23, 29, 31, 7, 5, 2, 3], k=3, threshold=5))
