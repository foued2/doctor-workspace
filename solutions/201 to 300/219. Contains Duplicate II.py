from typing import List


class Solution:
    @staticmethod
    def containsNearbyDuplicate(nums: List[int], k: int) -> bool:
        seen = set()
        left = 0

        for right in range(len(nums)):
            # If the current element is already in the set, return True
            if nums[right] in seen:
                return True
            # Add the current element to the set
            seen.add(nums[right])

            # If the size of the window exceeds k, remove the leftmost element
            if right - left >= k:
                seen.remove(nums[left])
                left += 1

        return False


# Test the function
solution = Solution()
print(solution.containsNearbyDuplicate(nums=[1, 2, 3, 1], k=3))  # Output: True


# class Solution:
#     def containsNearbyDuplicate(self, nums: List[int], k: int) -> bool:
#         num_index = {}  # Dictionary to store the last index of each element
#
#         for i, num in enumerate(nums):
#             # Check if the current element has been seen before and its last index is within the range k
#             if num in num_index and i - num_index[num] <= k:
#                 return True
#             # Update the last index of the current element
#             num_index[num] = i
#
#         # No duplicate found within the given range k
#         return False
#
#
# # Test the function
# solution = Solution()
# print(solution.containsNearbyDuplicate(nums=[1, 2, 3, 1], k=3))  # Output: True
