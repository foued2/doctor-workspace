class Solution:
    @staticmethod
    def isValid(word: str) -> bool:
        """
        Boolean flag
        """
        # A word is considered valid if:
        # 1. It contains a minimum of 3 characters.
        minimum_length = len(word) >= 3

        # 2. It contains only digits (0-9) and English letters (uppercase and lowercase).
        all_alnum = True

        # 3. It includes at least one vowel.
        vowels = {'a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U'}
        one_vowel = False

        # 4. It includes at least one consonant.
        one_consonant = False

        for char in word:
            if char in vowels:
                one_vowel = True
            elif char.isalpha() and char not in vowels:
                one_consonant = True
            elif not char.isalnum():
                all_alnum = False

        # Return True if all conditions are met
        return minimum_length and all_alnum and one_vowel and one_consonant


# Example usage:
solution = Solution()
print(solution.isValid("apple"))  # Expected output: True
print(solution.isValid("abc"))  # Expected output: True
print(solution.isValid("a1c"))  # Expected output: False
print(solution.isValid("AeI"))  # Expected output: False

print(Solution.isValid(word="234Adas"))
