class Solution:
    @staticmethod
    def numDifferentIntegers(word: str) -> int:
        # Initialize the answer to 0
        ans = 0
        # Initialize an empty dictionary to keep track of unique integers
        table = {}

        # Iterate through each character in the input string
        for char in word:
            # If the character is an alphabet, replace it with a space
            if char.isalpha():
                word = word.replace(char, ' ')

        # Split the modified string by spaces to get all number substrings
        nums = word.split()

        # Iterate through each number substring
        for num in nums:
            # Convert the substring to an integer
            num = int(num)
            # If the integer is already in the table, increment its count
            if num in table:
                table[num] += 1
            # If the integer is not in the table, add it and increment the answer
            else:
                table[num] = 1
                ans += 1

        # Return the total count of unique integers
        return ans


print(Solution.numDifferentIntegers(word="a1b01c001"))
