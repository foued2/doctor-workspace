class Solution:
    @staticmethod
    def isPalindrome(number: int) -> bool:
        # Convert a number to a list of its digits
        if number < 0:
            return False

        if number == 0:
            return True

        digit_list = []

        while number > 0:
            digit = number % 10  # Get the last digit
            digit_list.insert(0, digit)  # Insert it at the beginning of the list
            number //= 10  # Remove the last digit

        for i in range(len(digit_list)):
            if digit_list[i] != digit_list[-1 - i]:
                return False
        return True


# Create an instance of the Solution class
solution = Solution()
number = int(input("x = "))

# Call the isPalindrome method on the instance
result = solution.isPalindrome(number)

# Print the result
print(result)
