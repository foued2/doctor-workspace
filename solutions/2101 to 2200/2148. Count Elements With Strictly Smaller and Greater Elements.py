from typing import List


class Solution:
    @staticmethod
    def countElements(nums: List[int]) -> int:
        # If the length of nums is 1 or 2, there are not enough elements to form pairs, so return 0
        if len(nums) == 1 or len(nums) == 2:
            return 0

        # Find the minimum and maximum values in nums
        min_v = min(nums)
        max_v = max(nums)

        # Initialize a variable to store the count of elements that are counted
        ans = len(nums)

        # Iterate through each element in nums
        for num in nums:
            # If the current element is equal to the minimum or maximum value, decrease the count
            if num == min_v or num == max_v:
                ans -= 1

        # Return the count of elements after excluding the minimum and maximum values
        return ans


print(Solution.countElements(nums=[-71, -71, 93, -71, 40]))
