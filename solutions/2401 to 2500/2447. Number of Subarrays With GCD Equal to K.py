import math
from typing import List


class Solution:
    @staticmethod
    def subarrayGCD(nums: List[int], k: int) -> int:
        n = len(nums)  # Get the length of the input list `nums`
        res = []  # Initialize a list to store subarrays meeting the criteria

        for i in range(n):  # Iterate through each element in `nums`
            if math.gcd(nums[i]) == k:  # Check if the current element is divisible by `k`
                sub = [nums[i]]  # Initialize a new subarray starting with the current element
                j = i + 1  # Set the next index to check

                # Extend the subarray as long as subsequent elements are divisible by `k`
                while j < n and math.gcd(nums[i], nums[j]) == k:
                    sub.append(nums[j])  # Append the divisible element to the subarray
                    j += 1  # Move to the next index

                res.append(sub)  # After forming the subarray, add it to the results list
        print(res)
        return len(res)  # Return the number of subarrays found


if __name__ == '__main__':
    # Example usage: Print the number of subarrays where all elements are divisible by `k`
    print(Solution().subarrayGCD(nums=[9, 3, 1, 2, 6, 3], k=3))