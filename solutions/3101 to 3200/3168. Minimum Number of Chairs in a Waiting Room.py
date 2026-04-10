class Solution:
    @staticmethod
    def minimumChairs(s: str) -> int:
        # Initialize the answer to store the maximum number of occupied chairs needed
        ans = 0
        # Initialize the counter for currently occupied chairs
        occupied = 0
        # Get the length of the string
        n = len(s)
        # Iterate through each character in the string
        for i in range(n):
            # If the character is 'E' (Enter), increment the occupied counter
            if s[i] == 'E':
                occupied += 1
            # If the character is 'L' (Leave) and there are occupied chairs, decrement the occupied counter
            elif occupied and s[i] == 'L':
                occupied -= 1
            # Update the answer to be the maximum of the current occupied count and the previous maximum
            ans = max(occupied, ans)
        # Return the maximum number of occupied chairs needed
        return ans


print(Solution.minimumChairs(s="ELELEEL"))
