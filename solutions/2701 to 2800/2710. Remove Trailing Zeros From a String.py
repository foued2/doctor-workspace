class Solution:
    @staticmethod
    def removeTrailingZeros(num: str) -> str:
        # Using the rstrip() method to remove trailing zeros from the string
        return num.rstrip('0')


if __name__ == '__main__':
    print(Solution.removeTrailingZeros(num="51230100"))
