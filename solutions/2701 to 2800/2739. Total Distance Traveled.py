class Solution:
    @staticmethod
    def distanceTraveled(mainTank: int, additionalTank: int) -> int:
        # Calculate the number of additional units of fuel that can be used
        # (mainTank - 1) // 4 determines how many times 4 full units can be taken from the mainTank,
        # effectively giving us the number of times we can use 1 unit from the additionalTank
        additional_used = min((mainTank - 1) // 4, additionalTank)

        # Calculate the total distance
        # Each unit of fuel (mainTank + additional_used) allows traveling 10 kilometers
        total_distance = (mainTank + additional_used) * 10

        return total_distance


# Example usage:
mainTank = 9
additionalTank = 2
result = Solution().distanceTraveled(mainTank, additionalTank)
print(result)  # Output should be 110

print(Solution.distanceTraveled(additionalTank=5))
