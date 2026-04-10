class Solution:
    @staticmethod
    def countOdds(low: int, high: int) -> int:
        # Initialize the count of odd numbers to 0 (this is actually redundant)
        count = 0

        # Calculate the number of odd numbers in the range [low, high]
        # (high + 1) // 2 gives the number of odd numbers from 0 to high
        # low // 2 gives the number of odd numbers from 0 to low-1
        # Subtracting these two gives the number of odd numbers in the range [low, high]
        count = (high + 1) // 2 - low // 2

        # Return the final count of odd numbers in the range
        return count


print(Solution.countOdds(low=3, high=10))
