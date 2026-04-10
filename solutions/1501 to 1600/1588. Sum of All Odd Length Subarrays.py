from typing import List


class Solution:
    @staticmethod
    def sumOddLengthSubarrays(arr: List[int]) -> int:
        # Get the length of the input array
        n = len(arr)

        # Initialize the variable to accumulate the total sum of odd-length subarrays
        ans = 0

        # Start with the smallest odd subarray length (1)
        sub = 1

        # Iterate over all possible odd subarray lengths
        while sub <= n:
            # Iterate through all valid starting indices for the current subarray length
            for i in range(n - sub + 1):
                # Add the sum of the current subarray to the total
                ans += sum(arr[i:i + sub])

            # Increment to the next odd subarray length
            sub += 2

        # Return the accumulated sum of all odd-length subarrays
        return ans


if __name__ == '__main__':
    # Test cases
    print(Solution.sumOddLengthSubarrays(arr=[1, 4, 2, 5, 3, 7]))  # Example test case
    print(Solution.sumOddLengthSubarrays(arr=[1]))  # Edge case with single element


class Solution:
    @staticmethod
    def sumOddLengthSubarrays(arr: List[int]) -> int:
        """
        Prefix sum array solution
        """
        n = len(arr)  # Get the length of the input array
        ans = 0  # Initialize the total sum accumulator

        # Initialize the prefix sum array
        prefix_sum = [0] * (n + 1)

        # Compute the prefix sums
        for i in range(n):
            prefix_sum[i + 1] = prefix_sum[i] + arr[i]

        # Iterate over each starting index of subarrays
        for start in range(n):
            # Iterate over each ending index of subarrays
            for end in range(start, n):
                # Check if the subarray length is odd
                if (end - start) % 2 == 0:
                    # Compute subarray sum using prefix sums and add to total
                    ans += prefix_sum[end + 1] - prefix_sum[start]

        # Return the accumulated sum of all odd-length subarrays
        return ans


if __name__ == '__main__':
    # Test cases
    print(Solution.sumOddLengthSubarrays(arr=[1, 4, 2, 5, 3, 7]))  # Example test case
    print(Solution.sumOddLengthSubarrays(arr=[1]))  # Edge case with single element


class Solution:
    @staticmethod
    def sumOddLengthSubarrays(arr: List[int]) -> int:
        """
        Math, frequency contribution
        """
        # Initialize result accumulator and frequency counter
        res = 0
        freq = 0
        n = len(arr)  # Get the length of the input array

        # Iterate through each element in the array
        for i in range(n):
            # Update frequency: the formula accounts for presence in odd-length subarrays
            freq = freq - (i + 1) // 2 + (n - i + 1) // 2

            # Add the contribution of the current element to the result
            res += freq * arr[i]

        # Return the final accumulated result
        return res


if __name__ == '__main__':
    # Test cases
    print(Solution().sumOddLengthSubarrays(arr=[1, 4, 2, 5, 3, 7]))  # Example test case
    print(Solution().sumOddLengthSubarrays(arr=[1]))  # Edge case with single element