from typing import List


class Solution:
    @staticmethod
    def maximumPrimeDifference(nums: List[int]) -> int:
        # Helper function to determine if a number is prime
        def isPrime(n: int) -> bool:
            # Check if the number has any divisors other than 1 and itself
            for i in range(2, int(n ** 0.5) + 1):
                if n % i == 0:
                    return False
            return True

        # Initialize the answer to 0 (default value if no prime difference is found)
        ans = 0
        # Get the length of the input list
        n = len(nums)
        # Initialize two pointers: one at the start and one at the end of the list
        i, j = 0, n - 1

        # Use a while loop to iterate until the two pointers meet
        while i <= j:
            # Check if the number at index i is prime
            if isPrime(nums[i]):
                # If it is prime, check if the number at index j is also prime
                if isPrime(nums[j]):
                    # If both are prime, calculate the difference in indices
                    ans = j - i
                    # Break the loop as we have found the maximum prime difference
                    break
                else:
                    # If the number at index j is not prime, move the pointer j to the left
                    j -= 1
            else:
                # If the number at index i is not prime, move the pointer i to the right
                i += 1

        # Return the maximum difference found
        return ans


# Example usage:
sol = Solution()
print(sol.maximumPrimeDifference([1, 2, 3, 5, 7, 11]))  # Expected output: 5
print(sol.maximumPrimeDifference([4, 6, 8, 10, 13, 17]))  # Expected output: 1
print(sol.maximumPrimeDifference([4, 6, 8, 10]))  # Expected output: 0 (no primes found)

print(Solution.maximumPrimeDifference(nums=[4, 8, 2, 8]))
