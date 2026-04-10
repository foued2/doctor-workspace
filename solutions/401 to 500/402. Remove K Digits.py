class Solution:
    @staticmethod
    def removeKdigits(num: str, k: int) -> str:
        # Initialize a stack to store the digits
        stack = []

        for digit in num:
            # Remove digits from the top of the stack while the current digit is smaller than the top of the stack
            while k > 0 and stack and digit < stack[-1]:
                stack.pop()
                k -= 1
            # Add the current digit to the stack
            stack.append(digit)

        # If there are still remaining digits to be removed (k > 0), remove them from the end of the stack
        while k > 0:
            stack.pop()
            k -= 1

        # Convert the stack to a string and remove leading zeros
        result = ''.join(map(str, stack)).lstrip('0')

        # If the result is empty, return '0'
        return result if result else '0'


if __name__ == '__main__':
    # Test cases
    print(Solution.removeKdigits(num="1432219", k=3))  # Output: "1219"
    print(Solution.removeKdigits(num="10200", k=1))  # Output: "200"

