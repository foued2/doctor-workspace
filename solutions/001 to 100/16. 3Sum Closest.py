# Import List for type hinting in the function signature
from typing import List


# Define the class Solution
class Solution:

    # Use the @staticmethod decorator to signify the next method is static and doesn't require a self-parameter
    @staticmethod
    # Define the method "threeSumClosest" which takes a list, "nums", and an integer, "target", returning an integer
    def threeSumClosest(nums: List[int], target: int) -> int:

        # If the length of list "nums" is less than three
        if len(nums) < 3:
            # Return None
            return 0

        # Sort the list "nums"
        nums.sort()

        # Initialize the variable "closest_sum" as the sum of the first three numbers in "nums"
        closest_sum = sum(nums[:3])

        # For each index in the range of the length of "nums" minus two
        for i in range(len(nums) - 2):

            # Initialize j as the next index from i and k as the last index
            j, k = i + 1, len(nums) - 1

            # Until the index j is less than the index k
            while j < k:

                # Calculate the sum of the numbers at the indices i, j, and k in "nums"
                current_sum = nums[i] + nums[j] + nums[k]

                # If the current_sum equals the target
                if current_sum == target:
                    # Return the current_sum
                    return current_sum

                # If the absolute difference between the current_sum and target is less than between the
                # closest_sum and target
                if abs(current_sum - target) < abs(closest_sum - target):
                    # Update the closest_sum to the current_sum
                    closest_sum = current_sum

                    # If the current_sum is less than the target
                if current_sum < target:

                    # Increment j
                    j += 1

                # If the current_sum is greater than the target
                elif current_sum > target:

                    # Decrement k
                    k -= 1

        # Outside the for loop, return the closest_sum
        return closest_sum


# Print the result of "threeSumClosest" method when it's called on the Solution class
print(Solution.threeSumClosest(
    [833, 736, 953, -584, -448, 207, 128, -445, 126, 248, 871, 860, 333, -899, 463, 488, -50, -331, 903, 575, 265,
     162, -733, 648, 678, 549, 579, -172, -897, 562, -503, -508, 858, 259, -347, -162, -505, -694, 300, -40, -147,
     383, -221, -28, -699, 36, -229, 960, 317, -585, 879, 406, 2, 409, -393, -934, 67, 71, -312, 787, 161, 514, 865,
     60, 555, 843, -725, -966, -352, 862, 821, 803, -835, -635, 476, -704, -78, 393, 212, 767, -833, 543, 923, -993,
     274, -839, 389, 447, 741, 999, -87, 599, -349, -515, -553, -14, -421, -294, -204, -713, 497, 168, 337, -345,
     -948, 145, 625, 901, 34, -306, -546, -536, 332, -467, -729, 229, -170, -915, 407, 450, 159, -385, 163, -420,
     58, 869, 308, -494, 367, -33, 205, -823, -869, 478, -238, -375, 352, 113, -741, -970, -990, 802, -173, -977,
     464, -801, -408, -77, 694, -58, -796, -599, -918, 643, -651, -555, 864, -274, 534, 211, -910, 815, -102, 24,
     -461, -146], -7111))
