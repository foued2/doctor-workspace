class Solution:
    @staticmethod
    def numberOfCuts(n: int) -> int:
        # If there is only one piece, no cuts are needed
        if n == 1:
            return 0

        # If the number of pieces is even, the minimum number of cuts needed is half the number of pieces
        if n % 2 == 0:
            ans = n // 2
        # If the number of pieces is odd, we need n cuts
        else:
            ans = n

        # Return the calculated number of cuts
        return ans


# Test cases
print(Solution.numberOfCuts(1))  # Output: 0
print(Solution.numberOfCuts(4))  # Output: 2
print(Solution.numberOfCuts(5))  # Output: 5
