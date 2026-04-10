from typing import List


class Solution:
    @staticmethod
    def checkArithmeticSubarrays(nums: List[int], l: List[int], r: List[int]) -> List[bool]:
        res = []  # Initialize the result list to store boolean values for each query

        # Iterate through each start and end index in the query ranges
        for start, end in zip(l, r):
            subarray = nums[start:end + 1]  # Extract the subarray for the current query range

            # Check if subarray length is less than or equal to 1 (trivially arithmetic)
            if len(subarray) <= 1:
                res.append(True)  # Single element or empty subarrays are arithmetic
                continue  # Move to the next query

            # Determine the minimum and maximum values in the subarray
            min_val, max_val = min(subarray), max(subarray)

            # Check if the interval between min and max can be evenly divided
            if (max_val - min_val) % (len(subarray) - 1) != 0:
                res.append(False)  # If not, it cannot form an arithmetic sequence
                continue  # Move to the next query

            # Calculate the common difference for an arithmetic sequence
            diff = (max_val - min_val) // (len(subarray) - 1)

            # Generate the set of expected values in the arithmetic sequence
            expected_values = set(min_val + i * diff for i in range(len(subarray)))

            # Check if all the elements in the subarray match the expected values
            if set(subarray) == expected_values:
                res.append(True)  # Subarray forms an arithmetic sequence
            else:
                res.append(False)  # Subarray does not form an arithmetic sequence

        # Return the result list containing boolean values for each query
        return res


# Example usage
if __name__ == '__main__':
    print(Solution.checkArithmeticSubarrays(nums=[4, 6, 5, 9, 3, 7], l=[0, 0, 2], r=[2, 3, 5]))
