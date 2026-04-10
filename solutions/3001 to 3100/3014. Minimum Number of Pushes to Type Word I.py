from collections import defaultdict


class Solution:
    @staticmethod
    def minimumPushes(word: str) -> int:
        # Initialize result to store the total number of pushes
        result = 0

        # Create a hash_map to store the characters mapped to each number key
        hash_map = defaultdict(str)

        # Start the number mapping from 2 (as per typical phone keypads)
        number = 2

        # First pass: Populate the hash_map with characters for each number key
        for char in word:
            # Add the character to the corresponding number's string in the hash_map
            hash_map[number] += char

            # Move to the next number
            number += 1

            # Reset number to 2 if it exceeds 9 (as phone keypads only go from 2 to 9)
            if number == 10:
                number = 2

        # Second pass: Calculate the number of pushes required for each character
        for char in word:
            # Iterate through number keys 2 to 9
            for num in range(2, 10):
                # Check if the character is in the string mapped to the current number key
                if char in hash_map[num]:
                    # The number of pushes is the position of the character in the string + 1
                    result += hash_map[num].index(char) + 1
                    break

        # Return the total number of pushes required
        return result


# Example usage
solution = Solution()
print(solution.minimumPushes("hello"))  # Example output

print(Solution.minimumPushes(word="xycdefghxij"))
