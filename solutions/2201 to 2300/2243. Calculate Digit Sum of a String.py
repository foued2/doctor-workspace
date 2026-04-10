class Solution:
    @staticmethod
    def digitSum(s: str, k: int) -> str:
        # Get the initial length of the string
        n = len(s)

        # Continue processing as long as the length of the string is greater than k
        while n > k:
            # Initialize an empty string to store the merged result
            merge = ''

            # Iterate over the string in chunks of size k
            for i in range(0, n, k):
                # Get the current chunk of size k (or less if at the end of the string)
                divide = s[i:i + k]

                # Calculate the sum of the digits in the current chunk
                replace = str(sum(int(char) for char in divide))

                # Append the sum to the merged result
                merge += replace

            # Update the string s to be the new merged result
            s = merge

            # Update the length of the string
            n = len(merge)

        # Return the final string after processing
        return s


# Example usage:
s = "1111122222"
k = 3
solution = Solution()
print(solution.digitSum(s, k))  # Output should be "135" after several iterations

print(Solution.digitSum(s="00000000", k=3))
