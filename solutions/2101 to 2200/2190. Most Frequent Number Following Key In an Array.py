from typing import List


class Solution:
    @staticmethod
    def mostFrequent(nums: List[int], key: int) -> int:
        # Dictionary to keep track of the count of each number that follows the key
        count_map = {}

        # Iterate through the list, except the last element, to avoid out-of-bounds error
        for i in range(len(nums) - 1):
            # If the current number is the key
            if nums[i] == key:
                # The number immediately following the key
                target = nums[i + 1]
                # Update the count of the target number in the dictionary
                if target in count_map:
                    count_map[target] += 1
                else:
                    count_map[target] = 1

        # Initialize variables to find the number with the maximum frequency
        ans = -1
        max_count = 0
        # Iterate through the count_map to find the most frequent target number
        for target, count in count_map.items():
            if count > max_count:
                max_count = count
                ans = target

        return ans


# Test case
print(Solution.mostFrequent(nums = [3,2,2,3], key = 2))  # Output should be 2

print(Solution.mostFrequent(nums=[1, 100, 200, 1, 100], key=1))
