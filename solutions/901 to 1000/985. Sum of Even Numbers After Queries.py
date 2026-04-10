from typing import List


class Solution:
    @staticmethod
    def sumEvenAfterQueries(nums: List[int], queries: List[List[int]]) -> List[int]:
        # Initialize ans with the sum of even numbers in nums
        ans = sum(num for num in nums if num % 2 == 0)
        # Initialize the result list
        res = []
        # Iterate through each query
        for query in queries:
            val, idx = query
            first = nums[idx]
            # Update nums with the query value
            nums[idx] += val
            second = nums[idx]
            # Update ans based on changes in nums
            if first % 2 == 0:
                if second % 2 == 0:
                    # Update ans by adding the difference between second and first
                    ans += (second - first)
                else:
                    # Update ans by subtracting the first if second becomes odd
                    ans -= first
            elif second % 2 == 0:
                # Update ans by adding the second if first was odd and second becomes even
                ans += second
            # Append the updated ans to the result list
            res.append(ans)
        # Return the result list
        return res


print(Solution.sumEvenAfterQueries(nums=[3, 2], queries=[[4, 0], [3, 0]]))
