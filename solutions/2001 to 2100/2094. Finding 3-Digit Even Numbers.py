from typing import List


class Solution:
    @staticmethod
    def findEvenNumbers(digits: List[int]) -> List[int]:
        # Declare and initialize a dictionary to count occurrences of each digit (0-9)
        digit_counts = {}
        for n in range(0, 10):
            digit_counts[n] = 0

        # Count occurrences of each digit in the input list
        for digit in digits:
            digit_counts[digit] += 1

        # Initialize an empty list to store the valid 3-digit even numbers
        out = []

        # Iterate through possible hundreds place digits (1-9)
        for hundreds in range(1, 10):
            if digit_counts[hundreds] == 0:
                # Skip if the current digit is not available
                continue
            digit_counts[hundreds] -= 1

            # Iterate through possible tens place digits (0-9)
            for tens in range(0, 10):
                if digit_counts[tens] == 0:
                    # Skip if the current digit is not available
                    continue
                digit_counts[tens] -= 1

                # Iterate through possible ones place digits (0-9), but only even numbers (0, 2, 4, 6, 8)
                for ones in range(0, 10, 2):
                    if digit_counts[ones] == 0:
                        # Skip if the current digit is not available
                        continue

                    # Append the valid 3-digit even number to the output list
                    out.append(hundreds * 100 + tens * 10 + ones)

                # Restore the count of the tens place digit for subsequent iterations
                digit_counts[tens] += 1

            # Restore the count of the hundreds place digit for subsequent iterations
            digit_counts[hundreds] += 1

        # Return the list of all found 3-digit even numbers
        return out


if __name__ == '__main__':
    print(Solution.findEvenNumbers(digits=[2, 4, 6, 3]))
