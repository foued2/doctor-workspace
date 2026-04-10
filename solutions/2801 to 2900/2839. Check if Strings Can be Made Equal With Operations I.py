class Solution:
    @staticmethod
    def canBeEqual(s1: str, s2: str) -> bool:
        # Iterate through the characters of the strings
        for i in range(4):
            # Check if the current characters are not equal
            if s1[i] != s2[i]:
                # Check if swapping the characters at the current index and at an index two positions away can make
                # the strings equal
                if s1[i] != s2[i + (2 if i < 2 else -2)]:
                    return False  # If not, return False

        # If all characters can be paired up to make the strings equal, return True
        return True


print(Solution.canBeEqual(s1="abcd", s2="cdab"))
