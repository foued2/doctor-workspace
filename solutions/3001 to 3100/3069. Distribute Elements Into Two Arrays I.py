from typing import List


class Solution:
    @staticmethod
    def resultArray(nums: List[int]) -> List[int]:
        # Check if nums has less than 2 elements
        if len(nums) < 2:
            return nums  # Nothing to split if nums has less than 2 elements

        # Initialize arr1 and arr2 with the first two elements of nums
        arr1, arr2 = [nums[0]], [nums[1]]

        # Iterate through the remaining elements of nums
        for i in range(2, len(nums)):
            # Compare the last elements of arr1 and arr2
            if arr1[-1] > arr2[-1]:
                # Append the current element to arr1 if its last element is greater
                arr1.append(nums[i])
            else:
                # Otherwise, append the current element to arr2
                arr2.append(nums[i])

        # Concatenate arr1 and arr2 and return the result
        return arr1 + arr2


# Test the method
print(Solution.resultArray(nums=[5, 4, 3, 8]))
