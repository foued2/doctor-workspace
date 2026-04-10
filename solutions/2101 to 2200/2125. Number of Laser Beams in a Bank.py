from typing import List


class Solution:
    @staticmethod
    def numberOfBeams(bank: List[str]) -> int:
        # Initialize total_lazer_count to store the total number of laser beams
        total_lazer_count = 0

        # Initialize prev_lazer_count to store the number of devices in the previous non-empty row
        prev_lazer_count = 0

        # Iterate through each row in the bank
        for row in bank:
            # Count the number of '1's (devices) in the current row
            lazer_count = row.count('1')

            # If there are devices in the current row, calculate the beams generated
            total_lazer_count += prev_lazer_count * lazer_count

            # If the current row is not empty, update prev_lazer_count for the next iteration
            if lazer_count != 0:
                prev_lazer_count = lazer_count

        # Return the total number of laser beams calculated
        return total_lazer_count


print(Solution.numberOfBeams(bank=["011001", "000000", "010100", "001000"]))
