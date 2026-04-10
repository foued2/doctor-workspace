# Two Pointers // Linear Search // Nested Pointers

class Solution:
    @staticmethod
    def strStr(haystack: str, needle: str) -> int:
        for i in range(len(haystack) - len(needle) + 1):
            if haystack[i: i + len(needle)] == needle:
                return i
        return -1

    print(strStr("baab", "ab"))


"""
KMP Algorithm
"""
# class Solution:
#     @staticmethod
#     def strStr(haystack: str, needle: str) -> int:
#         if not needle:
#             return 0
#
#         # Compute the prefix function for the needle
#         prefix_function = [0] * len(needle)
#         j = 0
#         for i in range(1, len(needle)):
#             while j > 0 and needle[i] != needle[j]:
#                 j = prefix_function[j - 1]
#             if needle[i] == needle[j]:
#                 j += 1
#             prefix_function[i] = j
#
#         # Use the prefix function to perform pattern matching
#         j = 0
#         for i in range(len(haystack)):
#             while j > 0 and haystack[i] != needle[j]:
#                 j = prefix_function[j - 1]
#             if haystack[i] == needle[j]:
#                 j += 1
#             if j == len(needle):
#                 return i - j + 1
#
#         return -1
