from typing import List


class Solution:
    @staticmethod
    def dailyTemperatures(temperatures: List[int]) -> List[int]:
        # Initialize the result array with the same length as temperatures,
        # all elements set to 0 (default value if no warmer day is found in future).
        res = [0] * len(temperatures)

        # Stack to keep track of indices of the temperatures list
        # where we haven't found a warmer day yet.
        stack = []

        # Iterate through the list of temperatures
        for i in range(len(temperatures)):
            # Process elements in the stack as long as the stack is not empty
            # and the current temperature is warmer than the temperature at
            # the index at the top of the stack.
            while stack and temperatures[stack[-1]] < temperatures[i]:
                # Pop the index from the stack and set the result for that day.
                index = stack.pop()
                res[index] = i - index

            # Add the current day's index to the stack
            # as we need to find a warmer day for this day.
            stack.append(i)

        # Return the result array containing days to wait until warmer temperature.
        return res


if __name__ == '__main__':
    # Example usage of the Solution class to find the number of days
    # until a warmer temperature for the given list of temperatures.
    print(Solution().dailyTemperatures([73, 74, 75, 71, 69, 72, 76, 73]))