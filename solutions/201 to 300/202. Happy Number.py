class Solution:
    @staticmethod
    def isHappy(n: int) -> bool:
        # Define a function to calculate the sum of squares of digits of a number
        def sumSquares(num: int) -> int:
            return sum([int(i) ** 2 for i in str(num)])

        # Initialize slow and fast pointers with the initial number and its square sum
        #  Floyd's cycle detection algorithm:
        slow = n
        fast = sumSquares(n)

        # Continue the process until the fast pointer reaches 1 or slow and fast pointers meet
        while fast != 1 and slow != fast:
            # Move the slow pointer one step forward
            slow = sumSquares(slow)
            # Move the fast pointer two steps forward
            fast = sumSquares(sumSquares(fast))

        # If the fast pointer reaches 1, the number is a happy number
        return fast == 1

    print(isHappy(12))
