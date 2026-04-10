from collections import Counter


class Solution:
    @staticmethod
    def rearrangeCharacters(s: str, target: str) -> int:
        # Create a counter to count the frequency of each character in the string s
        s_counter = Counter(s)

        # Create a counter to count the frequency of each character in the target string
        target_counter = Counter(target)

        # Initialize the minimum count to a large number (infinity) to find the minimum frequency
        min_count = float('inf')

        # Iterate through each character and its frequency in the target_counter
        for char, freq in target_counter.items():
            # Check if the character exists in s_counter
            if char in s_counter:
                # Calculate how many times the character in s can fulfill the frequency requirement in target
                count = s_counter[char] // freq
                # Update min_count with the smallest count
                min_count = min(min_count, count)
            else:
                # If the character is not found in s, target cannot be formed at all
                return 0

        # Return the minimum count which represents the maximum number of times target can be formed
        return min_count


print(Solution.rearrangeCharacters(s="abbaccaddaeea", target="aaaaa"))
