class Solution:
    @staticmethod
    def getEncryptedString(s: str, k: int) -> str:
        # Initialize the result string as empty
        res = ''

        # Calculate the length of the input string
        n = len(s)

        # # Convert the string to a list of characters for easier manipulation
        # s = list(s)

        # Iterate through each character of the string
        for i in range(n):
            # Calculate the new index by shifting k positions, wrapping around using modulo n
            new_index = (i + k) % n

            # Append the character at the new index to the result string
            res += s[new_index]

        # Return the final encrypted string
        return res


if __name__ == "__main__":
    # Example usage: Encrypting the string "dart" with a rotation of 3
    print(Solution().getEncryptedString(s="dart", k=3))  # Output: "tdar"