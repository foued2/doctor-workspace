from typing import List


class Solution:
    @staticmethod
    def productExceptSelf(nums: List[int]) -> List[int]:
        n = len(nums)
        result = [1] * n

        # Calculate prefix products
        prefix_product = 1
        for i in range(n):
            result[i] *= prefix_product  # Multiply current result by prefix product
            prefix_product *= nums[i]  # Update prefix product for the next iteration

        # Calculate suffix products
        suffix_product = 1
        for i in range(n - 1, -1, -1):
            result[i] *= suffix_product  # Multiply current result by suffix product
            suffix_product *= nums[i]  # Update suffix product for the next iteration

        return result


if __name__ == '__main__':
    s = Solution()
    print(s.productExceptSelf([-1, 1, 0, -3, 3]))
