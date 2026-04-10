class Solution:
    @staticmethod
    def numWaterBottles(numBottles: int, numExchange: int) -> int:
        # Initialize the total number of bottles drunk to the initial number of bottles
        ans = numBottles

        # While we have enough empty bottles to exchange for at least one full bottle
        while numBottles >= numExchange:
            # Compute how many full bottles we can get by exchanging
            quotient, remainder = divmod(numBottles, numExchange)

            # Add the number of full bottles obtained by exchange to the total count
            ans += quotient

            # Update the number of bottles we have:
            # - quotient: new full bottles we just got by exchange
            # - remainder: remaining empty bottles that couldn't be exchanged
            numBottles = quotient + remainder

        # Return the total number of bottles drunk
        return ans


print(Solution.numWaterBottles(numBottles=9, numExchange=3))
