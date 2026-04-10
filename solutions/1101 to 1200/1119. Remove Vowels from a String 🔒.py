class Solution:
    @staticmethod
    def removeVowels(s: str) -> str:
        vowels = ('a', 'e', 'i', 'o', 'u')
        # Iterate over each vowel and replace it with an empty string
        for vowel in vowels:
            s = s.replace(vowel, '')
        return s


print(Solution.removeVowels("leetcodeisacommunityforcoders"))