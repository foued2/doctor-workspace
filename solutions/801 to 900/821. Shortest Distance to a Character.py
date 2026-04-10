class Solution:
    @staticmethod
    def shortestToChar(s: str, c: str) -> list[float]:
        # Length of the input string
        n = len(s)

        # Initialize distances array with a large number
        distances = [float('inf')] * n

        # Initialize a variable to store the distance from the left side
        prev_position = float('inf')

        # First pass: left to right
        for i in range(n):
            if s[i] == c:
                prev_position = i
            distances[i] = min(distances[i], abs(i - prev_position))

        # Re-initialize the variable to store the distance from the right side
        prev_position = float('inf')

        # Second pass: right to left
        for i in range(n - 1, -1, -1):
            if s[i] == c:
                prev_position = i
            distances[i] = min(distances[i], abs(i - prev_position))

        return distances


s = "loveleetcode"
c = 'e'
print(Solution.shortestToChar(s, c))
