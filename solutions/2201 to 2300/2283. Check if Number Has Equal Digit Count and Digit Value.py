from collections import Counter


class Solution:
    @staticmethod
    def digitCount(num: str) -> bool:
        # Create a Counter object to count the frequency of each digit in the input string
        table = Counter(num)

        # Get the length of the input string
        n = len(num)

        # Iterate over each position in the string
        for i in range(n):
            # Count the occurrences of the digit equal to the current index in the string
            # and compare it with the integer value at the current index
            # If they don't match, return False
            if num.count(str(i)) != int(num[i]):
                return False

        # If all checks pass, return True
        return True


print(Solution.digitCount(num="1210"))
