class Solution:
    @staticmethod
    def intToRoman(num: int) -> str:
        # Define a hash map to map Roman numerals to their integer values
        roman_numerals = {
            1000: 'M',
            900: 'CM',
            500: 'D',
            400: 'CD',
            100: 'C',
            90: 'XC',
            50: 'L',
            40: 'XL',
            10: 'X',
            9: 'IX',
            5: 'V',
            4: 'IV',
            1: 'I'
        }

        roman = ''

        for n in roman_numerals:
            while num >= n:
                roman += roman_numerals[n]
                num -= n

        return roman


# Create an instance of the Solution class
solution_instance = Solution()

# Call the intToRoman method and print the result
print(solution_instance.intToRoman(num=3999))
