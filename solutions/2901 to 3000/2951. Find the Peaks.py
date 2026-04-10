from typing import List


class Solution:
    @staticmethod
    def findPeaks(mountain: List[int]) -> List[int]:
        # Get the length of the mountain list
        n = len(mountain)
        # Initialize a list to store the indices of peaks
        peak_indices = []

        # Iterate over the mountain list, excluding the first and last elements
        for i in range(1, n - 1):
            # Check if the current element is greater than its adjacent neighbors
            if mountain[i] > mountain[i - 1] and mountain[i] > mountain[i + 1]:
                # If so, it's a peak, so add its index to the peak_indices list
                peak_indices.append(i)

        # Return the list of peak indices
        return peak_indices


print(Solution.findPeaks(mountain=[1, 4, 3, 8, 5]))
