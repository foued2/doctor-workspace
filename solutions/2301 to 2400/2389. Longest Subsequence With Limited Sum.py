from typing import List


class Solution:
    @staticmethod
    def answerQueries(nums: List[int], queries: List[int]) -> List[int]:
        n, m = len(nums), len(queries)
        res = [0] * m  # Initialize result list for storing answers to queries

        nums.sort()  # Sort nums in non-decreasing order
        for i in range(m):  # Iterate over each query
            sum_query = 0  # Initialize sum for the current query
            for j in range(n):  # Iterate over each number in sorted nums
                if sum_query + nums[j] <= queries[i]:  # Check if adding nums[j] is within the limit
                    sum_query += nums[j]  # Add nums[j] to the current sum
                    res[i] = j + 1  # Update the result for the current query
                else:
                    break  # Exit the loop if the sum exceeds the query limit
        return res  # Return the results for all queries


if __name__ == '__main__':
    print(Solution().answerQueries(nums=[4, 5, 2, 1], queries=[3, 10, 21]))


class Solution:
    @staticmethod
    def answerQueries(nums: List[int], queries: List[int]) -> List[int]:
        """
        Binary Search, Prefix Sum
        """
        # Count Elements With Prefix Sum
        def count_elements_with_prefix_sum(prefix_sum: List[int], target: int) -> int:
            """
            Counts how many elements in the prefix sums array can be summed without exceeding the target.
            Uses binary search to determine the maximum number of elements.
            """
            left, right = 0, len(prefix_sum) - 1
            while left <= right:  # Binary search loop
                mid = left + (right - left) // 2  # Find middle index
                if prefix_sum[mid] <= target:  # Check if prefix sum is within the target
                    left = mid + 1  # Move left boundary rightward
                else:
                    right = mid - 1  # Move right boundary leftward
            return right  # Number of elements that can be summed without exceeding the target

        # Sort nums in non-decreasing order
        nums.sort()

        # Create a prefix sum array
        prefix_sums = [0] * (len(nums) + 1)
        for i in range(len(nums)):  # Compute prefix sums
            prefix_sums[i + 1] = prefix_sums[i] + nums[i]  # Cumulative sum up to i-th element

        m = len(queries)
        res = [0] * m  # Initialize result list for storing answers to queries

        # For each query, find how many elements can be summed without exceeding the query value
        for i in range(m):  # Iterate over each query
            res[i] = count_elements_with_prefix_sum(prefix_sums, queries[i])  # Use helper function for result

        return res  # Return the results for all queries


if __name__ == '__main__':
    print(Solution().answerQueries(nums=[4, 5, 2, 1], queries=[3, 10, 21]))