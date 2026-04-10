class Solution:
    @staticmethod
    def checkZeroOnes(s: str) -> bool:
        # Initialize variables to store the maximum counts of consecutive ones and zeroes,
        # as well as the current counts of consecutive ones and zeroes
        best_one, best_zero, current_one, current_zero = 0, 0, 0, 0

        # Iterate through each character in the string
        for i in s:
            # If the current character is '1', update counts accordingly
            if i == "1":
                current_zero = 0  # Reset the count of consecutive zeroes
                current_one += 1  # Increment the count of consecutive ones
            # If the current character is '0', update counts accordingly
            else:
                current_zero += 1  # Increment the count of consecutive zeroes
                current_one = 0  # Reset the count of consecutive ones

            # Update the maximum counts of consecutive ones and zeroes
            best_one = max(best_one, current_one)
            best_zero = max(best_zero, current_zero)

        # Return True if the maximum count of consecutive ones is greater than the maximum count of consecutive zeroes
        return best_one > best_zero


print(Solution.checkZeroOnes(s="1101"))
