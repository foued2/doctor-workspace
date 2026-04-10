class Solution:
    @staticmethod
    def minimumSum(num: int) -> int:
        # Convert the number to a string and then to a list of characters (digits)
        num = list(str(num))

        # Create two empty lists to hold the digits for the two new numbers
        new = [[], []]

        # Loop twice to distribute the digits into the two new numbers
        for _ in range(2):
            for i in range(2):
                # Find the minimum digit from the remaining digits in num
                min_digit = min(num)
                # Append the minimum digit to one of the new lists
                new[i].append(min_digit)
                # Remove the used minimum digit from num to avoid reusing it
                num.remove(min_digit)

        # Join the lists to form two numbers and convert them to integers
        num1 = int(''.join(new[0]))
        num2 = int(''.join(new[1]))

        # Calculate the sum of the two new numbers
        ans = num1 + num2

        # Return the result
        return ans


print(Solution.minimumSum(num=2932))
