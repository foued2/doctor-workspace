class Solution:
    @staticmethod
    def numberCount(a: int, b: int) -> int:
        """
        Hash Table, Dynamic Programming
        """
        # Initialize a variable to count the numbers with unique digits
        count = 0

        # Iterate through the range from 'a' to 'b', inclusive
        for num in range(a, b + 1):
            # Convert the number to a string to easily check for unique digits
            num_str = str(num)
            # Initialize a set to keep track of digits seen so far
            digit_set = set()
            # Initialize a flag to track if the number has unique digits
            unique = True

            # Iterate through each digit in the number
            for digit in num_str:
                # If the digit is already in the set, the number doesn't have unique digits
                if digit in digit_set:
                    # Set the flag to False and break out of the loop
                    unique = False
                    break
                # Add the digit to the set
                digit_set.add(digit)

            # If the number has unique digits, increment the count
            if unique:
                count += 1

        # Return the count of numbers with unique digits in the range [a, b]
        return count

    # Example usage:

    a = 10
    b = 20
    print(numberCount(a, b))  # Output: 10
    
