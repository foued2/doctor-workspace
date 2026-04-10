class Solution:
    @staticmethod
    def reverseVowels(s: str) -> str:
        # Define a set of vowels in both lowercase and uppercase
        vowels = {'a', 'A', 'e', 'E', 'i', 'I', 'o', 'O', 'u', 'U'}
        # Convert the input string to a list of characters
        s = list(s)
        # Initialize pointers for the left and right ends of the string
        left, right = 0, len(s) - 1
        # Loop until the pointers meet
        while left < right:
            # Check if the character at the left pointer is a vowel
            if s[left] in vowels:
                # If so, check if the character at the right pointer is also a vowel
                if s[right] in vowels:
                    # If both are vowels, swap them
                    s[left], s[right] = s[right], s[left]
                    # Move the pointers towards the center
                    left += 1
                    right -= 1
                else:
                    # If the character at the right pointer is not a vowel, move the right pointer to the left
                    right -= 1
            else:
                # If the character at the left pointer is not a vowel, move the left pointer to the right
                left += 1
        # Convert the list of characters back to a string and return
        return ''.join(s)


if __name__ == '__main__':
    print(Solution.reverseVowels(s="leetcode"))
    print(Solution.reverseVowels(s="Ui"))
