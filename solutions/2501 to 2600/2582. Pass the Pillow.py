class Solution:
    @staticmethod
    def passThePillow(n: int, time: int) -> int:
        # If time is less than the number of people, simply return time + 1
        if time < n:
            ans = time + 1
        else:
            # Calculate the number of complete laps (back and forth)
            lap = time // (n - 1)
            # Check if the lap count is even or odd
            if lap % 2 == 0:
                # Even lap count means the pillow is moving forward
                ans = (time % (n - 1)) + 1
            else:
                # Odd lap count means the pillow is moving backward
                ans = n - (time % (n - 1))

        # Return the final position
        return ans


# Example usage:
solution = Solution()
print(solution.passThePillow(5, 8))  # Output: 4
print(solution.passThePillow(4, 5))  # Output: 3


print(Solution.passThePillow(n=9, time=131))
