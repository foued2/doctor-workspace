class Solution:
    @staticmethod
    def numberOfSpecialChars(word: str) -> int:
        count = 0
        # Iterate over each lowercase letter in the alphabet
        for char in 'abcdefghijklmnopqrstuvwxyz':
            # Check if both lowercase and uppercase versions of the character are in the word
            if char in word and char.upper() in word:
                # Check if the position of the lowercase character is before the uppercase character
                if word.rfind(char) < word.find(char.upper()):
                    count += 1  # Increment the count if the condition is met
        return count


if __name__ == '__main__':
    # Test the numberOfSpecialChars method with the example word "cCceDC"
    print(Solution().numberOfSpecialChars(word="cCceDC"))