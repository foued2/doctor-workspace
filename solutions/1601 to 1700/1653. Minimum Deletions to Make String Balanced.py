class Solution:
    @staticmethod
    def minimumDeletions(s: str) -> int:
        # Initialize the answer to 0 and a counter for 'b' characters
        minimum_deletions = 0
        count_b = 0

        # Loop through each character in the string
        for char in s:
            if char == 'b':
                # If the current character is 'b', increment the 'b' counter
                count_b += 1
            else:
                # If the current character is 'a', compute the minimum of:
                # 1. Current minimum deletions + 1 (assuming deleting current 'a')
                # 2. The Number of 'b' characters encountered so far
                # This step ensures we take the minimum deletions needed to keep the string without 'ba' substring
                minimum_deletions = min(minimum_deletions + 1, count_b)

        # Return the computed minimum deletions
        return minimum_deletions


if __name__ == '__main__':
    print(Solution.minimumDeletions("baba"))
