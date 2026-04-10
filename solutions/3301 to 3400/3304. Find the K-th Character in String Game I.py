class Solution:
    @staticmethod
    def kthCharacter(k: int) -> str:
        # Initialize the sequence with the first character 'a'
        word = 'a'

        # Generate a list of letters from 'a' to 'z'
        alphabet = [chr(ord('a') + i) for i in range(26)]

        # Continue generating the sequence until its length is at least k
        while len(word) < k:
            for char in word:
                # Append the next character in the alphabet to the sequence
                # The (alphabet.index(char) % len(alphabet)) + 1 ensures we don't go out of bounds
                word += alphabet[(alphabet.index(char) % len(alphabet)) + 1]
            # Uncomment the line below to see the sequence growth step by step
            # print(word)

        # Return the k-th character in the sequence (1-based index)
        return word[k - 1]


if __name__ == "__main__":
    # Example usage: prints the 5th character in the generated sequence
    print(Solution().kthCharacter(k=5))