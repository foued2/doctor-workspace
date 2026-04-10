class Solution:
    @staticmethod
    def largestOddNumber(num: str) -> str:
        # rstrip removes all trailing characters that match '02468' (even digits)
        return num.rstrip('02468')


# Example usage:
solution = Solution()
print(solution.largestOddNumber("52"))  # Expected output: "5"
print(solution.largestOddNumber("4206"))  # Expected output: ""
print(solution.largestOddNumber("35427"))  # Expected output: "35427"
print(solution.largestOddNumber("46825014"))  # Expected output: "46825"
