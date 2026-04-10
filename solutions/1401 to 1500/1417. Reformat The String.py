class Solution:
    @staticmethod
    def reformat(s: str) -> str:
        # Initialize empty lists to store characters and digits
        chars, digits = [], []

        # Separate characters and digits from the input string
        for c in s:
            if c.isalpha():  # Check if the character is a letter
                chars.append(c)  # Append the letter to the character list
            else:
                digits.append(c)  # Append the digit to the digit list

        # Check if the absolute difference in lengths is greater than 1
        if abs(len(chars) - len(digits)) > 1:
            return ''  # If the absolute difference is greater than 1, return an empty string

        # Initialize a result list with the same length as the input string
        res = [''] * len(s)

        # Interleave characters and digits in the result list
        # Use slicing to assign characters to even indices and digits to odd indices
        res[0::2], res[1::2] = (chars, digits) if len(chars) > len(digits) else (digits, chars)

        # Join the characters in the result list to form the reformatted string
        return ''.join(res)


print(Solution.reformat(s="covid2019"))
