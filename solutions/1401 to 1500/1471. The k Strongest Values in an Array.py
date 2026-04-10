from typing import List


class Solution:
    @staticmethod
    def getStrongest(arr: List[int], k: int) -> List[int]:
        # Sort the array to find the median
        arr = sorted(arr)

        # Find the median value
        n = len(arr)
        m = arr[(n - 1) // 2]

        # Initialize two pointers
        left, right = 0, n - 1
        result = []

        # Use two pointers to find the k strongest values
        while k > 0:
            if abs(arr[left] - m) > abs(arr[right] - m):
                result.append(arr[left])
                left += 1
            else:
                result.append(arr[right])
                right -= 1
            k -= 1

        return result


# Example Usage
arr = [1, 2, 3, 4, 5]
k = 2

# Create an instance of Solution and call the getStrongest method
solution = Solution()
result = solution.getStrongest(arr, k)

# Print the result
print(result)  # Output: [5, 1]

print(Solution.getStrongest(arr=[1, 2, 3, 4, 5], k=2))
