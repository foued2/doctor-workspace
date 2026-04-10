class Solution:
    @staticmethod
    def largestGoodInteger(num: str) -> str:
        # Initialize 'ans' with an empty string to track the largest good integer found
        ans = ''
        # Get the length of the input string 'num'
        n = len(num)

        # Loop through the string, but only up to the third-last character
        for i in range(n - 2):
            # Extract a substring of three characters
            trio = num[i:i + 3]
            # Check if all three characters in the substring are the same
            if trio[0] == trio[1] == trio[2]:
                # Update 'ans' to the largest of the current 'ans' and the found trio
                ans = max(ans, trio)

        # Return the largest good integer found, or an empty string if none was found
        return ans


print(Solution.largestGoodInteger(num="6777133339"))
