class Solution:
    @staticmethod
    def theMaximumAchievableX(num: int, t: int) -> int:
        # The maximum achievable value of num is obtained by adding 2 * t to it
        return num + (2 * t)


print(Solution.theMaximumAchievableX(num=3, t=2))
