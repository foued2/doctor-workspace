from typing import List


class Solution:
    @staticmethod
    def findNonMinOrMax(nums: List[int]) -> int:
        # Check if the length of the list is greater than 2
        if len(nums) > 2:
            # If it is, sort the first three elements of the list and return the middle one
            return sorted(nums)[1]
        else:
            # If the length of the list is not greater than 2, return -1
            return -1


if __name__ == '__main__':
    print(Solution.findNonMinOrMax(nums=[3, 2, 1, 4]))


from typing import List, Optional


class Solution:
    @staticmethod
    def findNonMinOrMax(nums: List[int]) -> Optional[int]:
        if len(nums) < 3:
            return None
        min_val = min(nums)
        max_val = max(nums)
        for num in nums:
            if num != min_val and num != max_val:
                return num
        return None


if __name__ == "__main__":
    # Test cases to verify the implementation
    print(Solution().findNonMinOrMax([3, 1, 2]))  # Expected Output: 2
    print(Solution().findNonMinOrMax([5, 3]))  # Expected Output: None