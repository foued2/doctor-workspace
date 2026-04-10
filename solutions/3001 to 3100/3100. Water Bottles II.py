class Solution:
    @staticmethod
    def maxBottlesDrunk(numBottles: int, numExchange: int) -> int:
        ans = numBottles
        empty_bottles = numBottles

        # Keep exchanging bottles while there are enough empty bottles for at least one exchange
        while empty_bottles >= numExchange:
            quotient, remainder = divmod(empty_bottles, numExchange)
            ans += quotient
            empty_bottles = quotient + remainder

        return ans


if __name__ == '__main__':
    print(Solution.maxBottlesDrunk(numBottles=20, numExchange=1))