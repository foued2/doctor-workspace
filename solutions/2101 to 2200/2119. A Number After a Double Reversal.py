class Solution:
    @staticmethod
    def isSameAfterReversals(num: int) -> bool:
        # Convert the number to a string to perform string operations
        num_str = str(num)

        # Check if the length of the number is greater than 1 and the last digit is not '0'
        if len(num_str) > 1 and num_str[-1] == '0':
            return False
        return True


print(Solution.isSameAfterReversals(num=1800))
