class Solution:
    @staticmethod
    def isPalindrome(s: str) -> bool:
        start, end = 0, len(s) - 1
        while start < end:
            while start < end and not s[start].isalnum():  # Skip non-alphanumeric characters from the start
                start += 1
            while start < end and not s[end].isalnum():  # Skip non-alphanumeric characters from the end
                end -= 1
            if s[start].lower() != s[end].lower():  # Check if characters are equal (case-insensitive)
                return False
            start += 1  # Move start pointer forward
            end -= 1  # Move end pointer backward
        return True


# Test the isPalindrome function
print(Solution.isPalindrome(s="ab"))
