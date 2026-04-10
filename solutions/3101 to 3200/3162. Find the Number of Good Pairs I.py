from typing import List


class Solution:
    @staticmethod
    def numberOfPairs(nums1: List[int], nums2: List[int], k: int) -> int:
        # Initialize the answer variable to count valid pairs
        ans = 0
        # Get the lengths of the input lists
        n = len(nums1)
        m = len(nums2)

        # Iterate over each element in nums1
        for i in range(n):
            # Iterate over each element in nums2
            for j in range(m):
                # Check if the element in nums1 is divisible by the product of the element in nums2 and k
                if nums1[i] % (nums2[j] * k) == 0:
                    # If the condition is met, increment the answer counter
                    ans += 1

        # Return the total count of valid pairs
        return ans


# Example usage
solution = Solution()
print(solution.numberOfPairs([12, 18, 24], [2, 3, 4], 3))  # Output: 4
print(solution.numberOfPairs([10, 15, 20], [1, 5], 5))  # Output: 2

print(Solution.numberOfPairs(nums1=[1, 3, 4], nums2=[1, 3, 4], k=1))
