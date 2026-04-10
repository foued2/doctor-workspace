class Solution:
    @staticmethod
    def maximum69Number(num: int) -> int:
        # Convert the integer to a list of its digits
        digits = [digit for digit in str(num)]

        # Iterate over the digits
        for i in range(len(digits)):
            # If the current digit is '6'
            if digits[i] == '6':
                # Change it to '9' to get the maximum number
                digits[i] = '9'
                # Convert the list of digits back to an integer and return it
                return int(''.join(digits))


print(Solution.maximum69Number(num=9669))
