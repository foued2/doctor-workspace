from typing import List


class Solution:
    @staticmethod
    def sortArrayByParityII(nums: List[int]) -> List[int]:
        """
        Two pointers, In place space complexity
        """
        # Initialize two pointers: one for even indices and one for odd indices
        even, odd = 0, 1
        # Get the length of the input list
        n = len(nums)
        # Continue swapping elements until one of the pointers exceeds the length of the list
        while even < n and odd < n:
            # Move the even pointer to the next even index
            while even < n and nums[even] % 2 == 0:
                even += 2
            # Move the odd pointer to the next odd index
            while odd < n and nums[odd] % 2 != 0:
                odd += 2
            # If both pointers are within the bounds of the list, swap the elements at their positions
            if even < n and odd < n:
                nums[even], nums[odd] = nums[odd], nums[even]
            # Move both pointers to the next even and odd indices respectively
            even += 2
            odd += 2
        # Return the modified list
        return nums


print(Solution.sortArrayByParityII(nums=[4, 2, 5, 7]))
