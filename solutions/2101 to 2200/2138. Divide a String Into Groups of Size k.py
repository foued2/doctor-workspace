from typing import List


class Solution:
    @staticmethod
    def divideString(s: str, k: int, fill: str) -> List[str]:
        # Initialize the result list to store the final substrings
        res = []

        # Calculate the length of the input string
        n = len(s)

        # Calculate the number of characters needed to fill the last group to reach the length k
        refill = (k - (n % k)) % k

        # Append the necessary number of fill characters to the end of the string
        s += fill * refill

        # Loop through the string in steps of k to divide it into substrings of length k
        for i in range(0, len(s), k):
            # Append each substring of length k to the result list
            res.append(s[i:i + k])

        # Return the list of substrings
        return res


print(Solution.divideString(s="abcdefghij", k=3, fill="x"))
