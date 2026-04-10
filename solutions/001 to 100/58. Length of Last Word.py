class Solution:
    @staticmethod
    def lengthOfLastWord(s: str) -> int:
        s = s[:: -1]
        counter = 0
        for i in range(len(s)):
            if s[i].isspace():
                continue
            else:
                counter += 1
            if i + 1 < len(s) and s[i + 1].isspace():
                return counter
        return counter

    print(lengthOfLastWord("l"))

# class Solution:
#     def lengthOfLastWord(self, s: str) -> int:
#         return len(s.strip().split(' ')[-1])
