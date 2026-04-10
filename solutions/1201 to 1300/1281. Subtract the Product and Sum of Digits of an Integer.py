class Solution:
    @staticmethod
    def subtractProductAndSum(n: int) -> int:
        # Initialize variables to store the product and sum of the digits
        p = 1
        s = 0

        # Iterate through each digit of the number
        while n > 0:
            # Add the current digit to the sum
            s += n % 10
            # Multiply the current digit to the product
            p *= n % 10
            # Remove the last digit from the number
            n //= 10

        # Return the difference between the product and the sum
        return p - s


if __name__ == '__main__':
    print(Solution.subtractProductAndSum(n=234))
