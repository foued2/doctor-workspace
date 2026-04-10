class Solution:
    @staticmethod
    def numberOfSubstrings(s: str, k: int) -> int:
        # Initialize the length of the string, the count of valid substrings,
        # and a dictionary to keep track of character frequencies
        n = len(s)
        count = 0
        char_count = {}
        left = 0  # Start of the sliding window

        # Loop through each character with the right pointer to expand the window
        for right in range(n):
            # Add the current character to the window or increment its count
            current_char = s[right]
            char_count[current_char] = char_count.get(current_char, 0) + 1

            # Check if any character in the current window has at least `k` occurrences
            while max(char_count.values(), default=0) >= k:
                # Since character with at least `k` occurrences is found, calculate
                # the number of valid substrings starting between `left` and `right`
                # and ending anywhere past `right`.
                count += (n - right)

                # Shrink the window from the left to try for other valid substrings
                char_count[s[left]] -= 1
                # If the frequency of left character becomes zero, remove it from count
                if char_count[s[left]] == 0:
                    del char_count[s[left]]
                # Move the left pointer to right
                left += 1

        return count


if __name__ == "__main__":
    # Example usage:
    s = "hxccgfp"
    k = 1
    print(Solution.numberOfSubstrings(s, k))  # Output: 28
