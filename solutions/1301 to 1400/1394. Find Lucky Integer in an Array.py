from typing import List


class Solution:
    @staticmethod
    def findLucky(arr: List[int]) -> int:
        """
        Hash Table
        """
        # Dictionary to store the frequency of each number
        num_frequency = {}
        # Maximum lucky number found
        max_lucky_number = -1

        # Count the frequency of each number in the array
        for num in arr:
            num_frequency[num] = num_frequency.get(num, 0) + 1

        # Iterate through each unique number and its frequency
        for num, frequency in num_frequency.items():
            # Check if the number is equal to its frequency (lucky number)
            if num == frequency:
                # Update the maximum lucky number found
                max_lucky_number = max(max_lucky_number, num)

        # Return the maximum lucky number found
        return max_lucky_number


if __name__ == '__main__':
    print(Solution.findLucky([2, 2, 2, 3, 3]))
