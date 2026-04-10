class Solution:
    @staticmethod
    def romanToInt(s: str) -> int:
        # Define a hash map to map Roman numerals to their integer values
        roman_to_int = {
            'I': 1,
            'V': 5,
            'X': 10,
            'L': 50,
            'C': 100,
            'D': 500,
            'M': 1000
        }

        # Initialize the result variable to store the converted integer
        result = 0
        # Get the length of the input string
        length = len(s)
        # Initialize the index variable for iteration
        index = 0

        # Iterate through the input string
        while index < length:
            # Check if the current Roman numeral is smaller than the next one
            if index + 1 < length and roman_to_int[s[index]] < roman_to_int[s[index + 1]]:
                # Subtract the current value from the next value
                result += (roman_to_int[s[index + 1]] - roman_to_int[s[index]])
                # Move the index two steps ahead for the next iteration
                index += 2
            else:
                # Add the current value to the result
                result += roman_to_int[s[index]]
                # Move the index one step ahead for the next iteration
                index += 1

        # Return the final result
        return result

    print(romanToInt(s="MCMXCIV"))
