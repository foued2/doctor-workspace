from typing import List


class Solution:
    @staticmethod
    def dietPlanPerformance(calories: List[int], k: int, lower: int, upper: int) -> int:
        # Get the length of the calorie list
        n = len(calories)

        # Initialize the total diet plan performance
        total = 0

        # Iterate through the calorie list with a step size of k
        for i in range(0, n, k):
            # Calculate the sum of calories for the current window of size k
            window_sum = sum(calories[i:i + k])

            # If the sum is less than the lower limit, decrease the total by 1
            if window_sum < lower:
                total -= 1
            # If the sum is greater than the upper limit, increase the total by 1
            elif window_sum > upper:
                total += 1

        # Return the total diet plan performance
        return total


if __name__ == '__main__':
    print(Solution.dietPlanPerformance(calories=[1, 2, 3, 4, 5], k=1, lower=3, upper=3))
    print(Solution.dietPlanPerformance(calories=[3, 2], k=2, lower=0, upper=1))
    print(Solution.dietPlanPerformance(calories=[6, 5, 0, 0], k=2, lower=1, upper=5))
