class Solution:
    @staticmethod
    def maxScore(s: str) -> int:
        """
        Prefix sum
        """
        # Calculate the total number of '1's in the string
        total_sum = sum([int(i) for i in s])

        # Initialize max_score to 0 to keep track of the maximum score
        max_score = 0

        # Initialize zeroes_count to count the number of '0's in the left part
        zeroes_count = 0

        # Iterate through the string except for the last character
        for bit in s[:-1]:
            # If the current bit is '0', increment the zeroes_count
            if bit == '0':
                zeroes_count += 1
            else:
                # If the current bit is '1', decrement total_sum (moving '1' to the left part)
                total_sum -= 1

            # Calculate the current score as the sum of zeroes_count and total_sum
            score = zeroes_count + total_sum

            # Update max_score if the current score is greater than or equal to it
            if score >= max_score:
                max_score = score

        # Return the maximum score found
        return max_score


print(Solution.maxScore(s="1111"))
