class Solution:
    @staticmethod
    def countAsterisks(s: str) -> int:
        # Initialize the counter for asterisks
        ans = 0
        # Initialize a flag to track whether we are between pairs of '|'
        within_pipes = False

        # Iterate through each character in the string
        for char in s:
            # If the character is '|', toggle the within_pipes flag
            if char == '|':
                within_pipes = not within_pipes
            # If the character is '*', and we are not within pipes, increment the counter
            elif char == '*' and not within_pipes:
                ans += 1

        # Return the total count of asterisks outside pipes
        return ans


# Example usage
solution = Solution()
print(solution.countAsterisks("l|*e*et|c**o|*de|"))  # Expected output: 2
print(solution.countAsterisks("iam|*your|computer"))  # Expected output: 1
print(solution.countAsterisks("**|**|**"))  # Expected output: 0
print(solution.countAsterisks("|||||*||"))  # Expected output: 0
print(solution.countAsterisks("*|*|"))  # Expected output: 1


class Solution:
    @staticmethod
    def countAsterisks(s: str) -> int:
        # Split the string `s` by the pipe character '|'
        # and consider only the segments outside the pairs of pipes
        segments = s.split("|")[::2]

        # Sum the number of asterisks in the selected segments
        return sum(segment.count("*") for segment in segments)


# Example usage
solution = Solution()
print(solution.countAsterisks("l|*e*et|c**o|*de|"))  # Expected output: 2
print(solution.countAsterisks("iam|*your|computer"))  # Expected output: 1
print(solution.countAsterisks("**|**|**"))  # Expected output: 0
print(solution.countAsterisks("|||||*||"))  # Expected output: 0
print(solution.countAsterisks("*|*|"))  # Expected output: 1
