class Solution:
    @staticmethod
    def checkOnesSegment(s: str) -> bool:
        # Strip leading and trailing zeros from the string
        s = s.strip("0")
        # Print the intermediate string after stripping for debugging purposes
        print(s)
        # Check if there are any '0' characters left in the string
        # If there are no '0' characters, it means there is only one segment of ones
        return "0" not in s


print(Solution.checkOnesSegment(s="1100111"))
