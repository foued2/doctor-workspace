class Solution:
    @staticmethod
    def halvesAreAlike(s: str) -> bool:
        # Determine the length of the string
        n = len(s)
        # Define the set of vowels (considering both lowercase and uppercase)
        vowels = set('aeiouAEIOU')
        # Split the string into two halves
        a, b = s[:n // 2], s[n // 2:]
        # Count vowels in the first half
        count_a = sum(1 for char in a if char in vowels)
        # Count vowels in the second half
        count_b = sum(1 for char in b if char in vowels)
        # Compare the counts and return the result
        return count_a == count_b


# Test cases
print(Solution.halvesAreAlike("book"))  # Expected output: True
print(Solution.halvesAreAlike("textbook"))  # Expected output: False
print(Solution.halvesAreAlike("MerryChristmas"))  # Expected output: False
print(Solution.halvesAreAlike("AbCdEfGh"))  # Expected output: True
