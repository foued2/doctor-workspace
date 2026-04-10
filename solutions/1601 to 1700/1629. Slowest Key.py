from typing import List


class Solution:
    @staticmethod
    def slowestKey(releaseTimes: List[int], keysPressed: str) -> str:
        # Initialize the maximum duration with the first key press duration
        max_duration = releaseTimes[0]

        # Initialize the slowest key with the first key pressed
        slowest_key = keysPressed[0]

        # Get the number of key presses
        n = len(releaseTimes)

        # Iterate over the remaining key presses starting from the second one
        for i in range(1, n):
            # Calculate the duration of the current key press
            duration = releaseTimes[i] - releaseTimes[i - 1]

            # Check if the current duration is greater than the maximum duration
            if duration > max_duration:
                # Update the maximum duration and the slowest key
                max_duration = duration
                slowest_key = keysPressed[i]
            # Check if the current duration is equal to the maximum duration
            elif duration == max_duration:
                # Update the slowest key to the lexicographically larger one
                slowest_key = max(slowest_key, keysPressed[i])

        # Return the slowest key
        return slowest_key


print(Solution.slowestKey(releaseTimes=[9, 29, 49, 50], keysPressed="cbcd"))
