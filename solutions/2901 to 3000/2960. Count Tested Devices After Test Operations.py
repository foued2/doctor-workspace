from typing import List

class Solution:
    @staticmethod
    def countTestedDevices(batteryPercentages: List[int]) -> int:
        # Initialize a variable to store the count of tested devices
        ans = 0

        # Iterate through the battery percentages
        for batteryPercentage in batteryPercentages:
            # Check if the difference between the battery percentage and the current count is greater than 0
            if batteryPercentage - ans > 0:
                # If so, increment the count
                ans += 1

        # Return the final count of tested devices
        return ans


print(Solution.countTestedDevices(batteryPercentages=[0,1,2]))
