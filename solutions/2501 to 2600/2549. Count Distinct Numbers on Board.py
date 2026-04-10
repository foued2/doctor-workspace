class Solution:
    @staticmethod
    def distinctIntegers(n: int) -> int:
        # If n is 1, the distinct integers count is 1
        if n == 1:
            return n  # Return 1 when n is 1
        else:
            # For n greater than 1, the distinct integers count is n - 1
            return n - 1


print(Solution.distinctIntegers(n=5))
