class Solution:
    @staticmethod
    def calculateTime(keyboard: str, word: str) -> int:
        time = 0
        prev_index = 0  # Initialize the previous index as the index of the first character on the keyboard
        for char in word:
            # Calculate the time taken to type the current character
            time += abs(keyboard.index(char) - prev_index)
            # Update the previous index for the next iteration
            prev_index = keyboard.index(char)
        return time


print(Solution.calculateTime(keyboard="pqrstuvwxyzabcdefghijklmno", word="leetcode"))
