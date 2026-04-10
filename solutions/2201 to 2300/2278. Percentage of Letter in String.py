class Solution:
    @staticmethod
    def percentageLetter(s: str, letter: str) -> int:
        n = len(s)  # Get the length of the string
        count = 0  # Initialize a counter for the occurrences of the given letter

        # Iterate through each character in the string
        for char in s:
            # If the current character matches the given letter, increment the counter
            if char == letter:
                count += 1

        # Calculate the percentage of occurrences of the given letter
        percentage = (count / n) * 100

        # Return the percentage as an integer
        return int(percentage)


if __name__ == '__main__':
    print(Solution.percentageLetter(s="foobar", letter="o"))
