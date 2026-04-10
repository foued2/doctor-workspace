class Solution:
    @staticmethod
    def balancedStringSplit(s: str) -> int:
        # Initialize a balance counter
        balance = 0
        # Initialize a counter for the number of balanced substrings
        ans = 0

        # Iterate over each character in the string
        for char in s:
            # Increment balance if the character is 'R'
            if char == 'R':
                balance += 1
            # Decrement balance if the character is 'L'
            else:
                balance -= 1

            # Whenever balance is 0, we have a balanced substring
            if balance == 0:
                ans += 1

        # Return the total number of balanced substrings found
        return ans


print(Solution.balancedStringSplit(s="RLRRLLRLRL"))
