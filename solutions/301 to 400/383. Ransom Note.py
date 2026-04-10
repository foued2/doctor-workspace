from collections import defaultdict


class Solution:
    @staticmethod
    def canConstruct(ransomNote: str, magazine: str) -> bool:
        # Initialize a default-dict to store character counts in magazine
        magazine_counts = defaultdict(int)

        # Count occurrences of characters in magazine
        for char in magazine:
            magazine_counts[char] += 1

        # Check if ransomNote can be constructed from magazine
        for char in ransomNote:
            # If the character is not in the magazine or its count is 0, return False
            if magazine_counts[char] == 0:
                return False
            # Decrement the count of the character in the magazine
            magazine_counts[char] -= 1

        # If we reach this point, ransomNote can be constructed from magazine
        return True


# Test the implementation
sol = Solution()
ransomNote = "aab"
magazine = "baa"
print(sol.canConstruct(ransomNote, magazine))  # Output: True
