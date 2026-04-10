class Solution:
    @staticmethod
    def divisorSubstrings(num: int, k: int) -> int:
        """
        Sliding window
        """
        # Initialize a counter to keep track of the number of valid substrings
        ans = 0

        # Convert the number to a string for easier manipulation of substrings
        str_num = str(num)

        # Determine the length of the string representation of the number
        n = len(str_num)

        # Loop through the string representation of the number
        for i in range(n - k + 1):  # Ensure we have enough characters left for a full window of size k
            # Extract a substring of length k starting at index i
            window = str_num[i:i + k]

            # Convert the substring back to an integer
            window_num = int(window)

            # If the substring converted to integer is 0, skip to avoid division by zero
            if window_num == 0:
                continue

            # Check if the original number is divisible by the integer value of the substring
            if num % window_num == 0:
                # If divisible, increment the counter
                ans += 1

        # Return the total count of valid substrings
        return ans


print(Solution.divisorSubstrings(num=30003, k=2))
