class Solution:
    @staticmethod
    def thousandSeparator(n: int) -> str:
        # Convert the integer n to a string and reverse it
        n_str = str(n)
        # Check if the length of the string is 3 or less
        if len(n_str) <= 3:
            return n_str  # No need for separator if number has 3 or fewer digits

        result = []  # Initialize an empty list to store formatted characters
        # Iterate through the reversed string
        for i, digit in enumerate(reversed(n_str)):
            # Insert a dot after every third digit (except for the first group)
            if i > 0 and i % 3 == 0:
                result.append('.')  # Insert dot
            result.append(digit)  # Append the current digit to the result list

        # Join the characters back together and reverse the result to get the final formatted string
        return ''.join(reversed(result))


# Example usage:
solution = Solution()
print(solution.thousandSeparator(1234567))  # Output: "1.234.567"

print(Solution.thousandSeparator(n=1234567))
