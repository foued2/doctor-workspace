class Solution:
    @staticmethod
    def brokenKeyboard(s: str, keyboard: str) -> int:
        # Calculate the length of the input string
        n = len(s)
        # Initialize the variable to store the answer
        ans = 0
        # Initialize a counter variable
        c = 0
        # Iterate through each character in the input string
        for i in range(n):
            # Check if the current character is in the keyboard
            if s[i] in keyboard:
                # If the character is in the keyboard, increment the counter
                c += 1
                # Add the current value of the counter to the answer
                ans += c
            else:
                # If the character is not in the keyboard, reset the counter
                c = 0
        # Return the final answer
        return ans


if __name__ == '__main__':
    # Read inputs from standard input and split them by space
    n, k = input().strip().split(' ')
    # Read the input string
    s = input()
    # Read the keyboard layout
    keyboard = input().strip()
    # Calculate the answer using the brokenKeyboard method and print it
    answer = Solution.brokenKeyboard(s, keyboard)
    print(answer)
