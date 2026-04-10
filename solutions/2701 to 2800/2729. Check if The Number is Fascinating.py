class Solution:
    @staticmethod
    def isFascinating(n: int) -> bool:
        # Concatenate the number, its double, and its triple into a single string
        curr = str(n) + str(2 * n) + str(3 * n)

        # Sort the concatenated string and compare with "123456789"
        # This checks if all digits from 1 to 9 are present exactly once
        return "123456789" == ''.join(sorted(curr))


# Example usage
solution = Solution()
print(solution.isFascinating(192))  # Output: True (since 192, 384, and 576 contain all digits from 1 to 9)
print(solution.isFascinating(100))  # Output: False (since the concatenation does not contain all digits from 1 to 9)
