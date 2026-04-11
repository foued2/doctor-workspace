from typing import List


class Solution:
    @staticmethod
    def median(n: int, nums: List[int]) -> int:
        # If the list has less than 2 elements, the median is assumed to be 1
        if len(nums) < 2:
            return 1

        ans = 1  # Initialize the answer variable with 1
        nums = sorted(nums)  # Sort the list of numbers
        med = (n - 1) // 2  # Calculate the index of the median element

        # Increment the value of the element at the median index by 1
        nums[med] += 1

        # Loop through the elements after the median index
        for i in range(med + 1, len(nums)):
            # Check if the current element is less than the previous element
            if nums[i] < nums[i - 1]:
                # Calculate the difference between the previous element and the current element
                diff = nums[i - 1] - nums[i]
                # Increment the answer by the calculated difference
                ans += diff
                # Update the current element by adding the difference to it
                nums[i] += diff

        # Return the final answer
        return ans


if __name__ == '__main__':
    t = int(input())  # Input the number of test cases
    for _ in range(t):
        n = int(input())  # Input the number of elements in the list
        nums = list(map(int, input().split()))  # Input the list of numbers
        print(Solution.median(n, nums))  # Print the median of the list
