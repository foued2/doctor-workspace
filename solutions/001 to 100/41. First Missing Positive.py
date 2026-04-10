class Solution:
    @staticmethod
    def firstMissingPositive(nums):
        n = len(nums)

        # Rearrange the array
        for i in range(n):
            while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:
                nums[nums[i] - 1], nums[i] = nums[i], nums[nums[i] - 1]

        # Find the first missing positive integer
        for i in range(n):
            if nums[i] != i + 1:
                return i + 1

        return n + 1

    print(firstMissingPositive(nums=[3, 4, -1, 1]))
