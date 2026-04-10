class Solution:
    @staticmethod
    def getLucky(s: str, k: int) -> int:
        # Convert the characters in the string to numbers based on their position in the alphabet
        convert = ''
        for char in s:
            convert += str(ord(char) - (ord('a') - 1))

        # Initialize the transformation with the converted string
        transform = convert

        # Perform the transformation 'k' times
        for _ in range(k):
            # Convert the string to a list of integers and sum them up
            transform = sum(int(char) for char in transform)
            # Convert the sum back to a string
            transform = str(transform)

        # Convert the final transformed string back to an integer and return it
        return int(transform)


print(Solution.getLucky(s="leetcode", k=2))
