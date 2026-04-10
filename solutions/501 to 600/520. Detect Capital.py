class Solution:
    @staticmethod
    def detectCapitalUse(word: str) -> bool:
        # Check if the entire word is in uppercase
        if word.isupper():
            return True

        # Check if the entire word is in lowercase
        if word.islower():
            return True

        # Check if the word is in title case (first letter uppercase and the rest lowercase)
        if word.istitle():
            return True

        # If none of the above conditions are met, the capital usage is incorrect
        return False


if __name__ == '__main__':
    # Create an instance of the Solution class
    s = Solution()

    # Test the detectCapitalUse method with the word "USA" and print the result
    print(s.detectCapitalUse("USA"))  # Should output True, since "USA" is all uppercase