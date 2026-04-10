class Solution:
    @staticmethod
    def areAlmostEqual(s1: str, s2: str) -> bool:
        n = len(s1)
        diff = []

        # Iterate through the characters of both strings
        for i in range(n):
            if s1[i] != s2[i]:
                diff.append((s1[i], s2[i]))

        # If there are no differing positions, the strings are already equal
        if len(diff) == 0:
            return True

        # If there are exactly two differing positions, check if swapping can make the strings equal
        if len(diff) == 2 and diff[0] == diff[1][::-1]:
            return True

        # If the conditions are not met, one swap cannot make the strings equal
        return False


print(Solution.areAlmostEqual(s1="bank", s2="kanb"))
