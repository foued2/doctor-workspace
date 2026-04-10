class Solution:
    @staticmethod
    def reformatNumber(number: str) -> str:
        # Iterate through each character in the input string
        for char in number:
            # If the character is a space or hyphen, remove it from the string
            if char == ' ' or char == '-':
                number = number.replace(char, '')

        # Calculate the length of the cleaned number string
        n = len(number)

        # Initialize an empty list to hold the parts of the reformatted number
        res = []

        # If the length of the number is 2 or 3, append the entire number as a single part
        if n == 2 or n == 3:
            res.append(number)

        # If the length of the number is 4, split it into two parts of 2 digits each
        elif n == 4:
            for i in range(0, n, 2):
                res.append(number[i:i + 2])

        # If the length of the number is greater than 4
        else:
            # Calculate the quotient and remainder when the length is divided by 3
            quotient, remainder = divmod(n, 3)

            # If the remainder is 1, handle the case where we need to avoid a single digit part
            if remainder == 1:
                # Add parts of 3 digits each until we have 4 digits left
                for i in range(quotient - 1):
                    res.append(number[i * 3: (i + 1) * 3])
                # Add the last 4 digits as two parts of 2 digits each
                for i in range(n - 4, n, 2):
                    res.append(number[i:i + 2])
            else:
                # Add parts of 3 digits each for the entire number
                for i in range(0, n, 3):
                    res.append(number[i:i + 3])

        # Join the parts with hyphens to form the final reformatted number
        res = '-'.join(res)
        return res


print(Solution.reformatNumber(number="123 4-5678"))
