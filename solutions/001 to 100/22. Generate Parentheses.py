from typing import List


class Solution:
    @staticmethod
    def generateParenthesis(n: int) -> List[str]:
        """
        :param n:
        :return:
        """
        # Initialize a DP table to store intermediate results
        dp = {}

        def dp_backtrack(open_count, close_count):
            # Check if the result is already memoized
            if (open_count, close_count) in dp:
                return dp[(open_count, close_count)]

            # Base case: if the combination is complete, add it to the result
            if open_count == n and close_count == n:
                return ['']

            result = []

            # Try adding an open parenthesis if allowed
            if open_count < n:
                combinations = dp_backtrack(open_count + 1, close_count)
                result.extend(['(' + combo for combo in combinations])

            # Try adding a closing parenthesis if allowed
            if close_count < open_count:
                combinations = dp_backtrack(open_count, close_count + 1)
                result.extend([')' + combo for combo in combinations])

            # Memoize the result before returning
            dp[(open_count, close_count)] = result
            return result

        return dp_backtrack(0, 0)

    print(generateParenthesis(4))
