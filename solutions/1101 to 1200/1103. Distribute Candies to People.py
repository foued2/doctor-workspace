from typing import List


class Solution:
    @staticmethod
    def distributeCandies(candies: int, num_people: int) -> List[int]:
        # Initialize a list to store the candies each person gets
        distribution = [0] * num_people

        # Start distributing candies with an initial amount
        give_out = 1
        index = 0

        # Continue distributing candies until we run out
        while candies > 0:
            # Distribute candies to the current person
            distribution[index] += min(candies, give_out)
            candies -= give_out
            give_out += 1  # Increase the next amount to distribute
            index = (index + 1) % num_people

        return distribution


print(Solution.distributeCandies(candies=10, num_people=3))

#  1  2   3   4   5       (n * 0) + 1 * (i + 1)
#  7  9  11  13  15       (n * 1) + 2 * (i + 2)
# 18 21  24  27  30       (n * 3) + 3 * (i + 3)
# 34 38  42  46  50       (n * 6) + 4 * (i + 4)


class Solution:
    @staticmethod
    def distributeCandies(candies: int, num_people: int) -> List[int]:
        # Step 1: Calculate the maximum number of complete rounds (k) of distribution possible
        # The formula k = int(0.5 * (-1 + (1 + 8 * candies) ** 0.5)) derives from solving the quadratic equation
        # for the sum of the first k natural numbers such that the sum <= candies.
        k = int(0.5 * (-1 + (1 + 8 * candies) ** 0.5))

        # Step 2: Calculate the number of full passes (rounds) and remaining candies
        passes, rem = divmod(k, num_people)

        # Step 3: Compute prefix sums for total candies each person gets after (passes-1) and passes rounds
        preT0 = (passes - 1) * passes // 2  # Sum of first (passes-1) rounds for each person
        preT1 = preT0 + passes  # Sum of first passes rounds for each person

        # Step 4: Distribute candies based on full passes and the remaining rounds
        # Create the distribution array where each element represents candies received by a person
        arr = [
            preT1 * num_people + (passes + 1) * (i + 1) if i < rem else preT0 * num_people + passes * (i + 1)
            for i in range(num_people)
        ]

        # Step 5: Add remaining candies to the appropriate person
        arr[rem] += candies - (k * (k + 1)) // 2

        return arr


# Example usage:
solution = Solution()
print(solution.distributeCandies(7, 4))  # Output: [1, 2, 3, 1]
