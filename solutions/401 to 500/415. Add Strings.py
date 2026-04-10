class Solution:
    @staticmethod
    def addStrings(num1: str, num2: str) -> str:
        # Convert both string representations of numbers to integers
        # Add the integer values
        # Convert the result back to a string and return it
        return str(int(num1) + int(num2))


# Create an instance of the Solution class
s = Solution()

# Example usage: Adding the string representations of "123" and "456"
# This should output "579" as the result
print(s.addStrings("123", "456"))