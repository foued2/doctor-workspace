class Solution:
    @staticmethod
    def reverseStr(s: str, k: int) -> str:
        n = len(s)  # Get the length of the string

        # If the entire string length is less than k, reverse the whole string
        if n < k:
            return s[::-1]

        # If the string length is between k and 2k, reverse the first k characters and keep the rest unchanged
        if k <= n < 2 * k:
            return s[:k][::-1] + s[k:]

        else:
            # For strings longer than 2k, iterate in chunks of 2k
            for i in range(0, n, 2 * k):
                # Reverse the first k characters in each 2k chunk
                s = s[:i] + s[i:i + k][::-1] + s[i + k:]
            return s  # Return the modified string


if __name__ == '__main__':
    # Example usage of the function
    print(Solution().reverseStr(s="abcdefg", k=2))  # Expected output: "bacdfeg"