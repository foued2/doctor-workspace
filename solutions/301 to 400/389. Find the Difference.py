class Solution:
    @staticmethod
    def findTheDifference(s: str, t: str) -> str:
        """
        Bit Manipulation
        """
        xor_sum = 0
        # XOR all characters in both s and t
        for char in s + t:
            xor_sum ^= ord(char)
        # The remaining xor_sum will be the ASCII of the extra character
        return chr(xor_sum)


print(Solution.findTheDifference(s="abcd", t="abcde"))
