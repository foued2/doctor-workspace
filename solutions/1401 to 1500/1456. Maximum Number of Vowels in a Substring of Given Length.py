class Solution:
    @staticmethod
    def maxVowels(s: str, k: int) -> int:
        # Set of vowels for quick lookup
        vowels = set('aeiou')

        # Initialize the number of vowels in the first window of size k
        count = sum(1 for char in s[:k] if char in vowels)

        # Set the initial maximum number of vowels found to the current count
        max_vowels = count

        # Use the sliding window technique
        for i in range(k, len(s)):
            # If the character at the start of the previous window is a vowel, decrement count
            if s[i - k] in vowels:
                count -= 1

            # If the character at the end of the current window is a vowel, increment count
            if s[i] in vowels:
                count += 1

            # Update max_vowels if the current count is greater
            if count > max_vowels:
                max_vowels = count

        return max_vowels


print(Solution.maxVowels(s="ibpbhixfiouhdljnjfflpapptrxgcomvnb", k=33))
