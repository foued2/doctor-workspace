class Solution:
    @staticmethod
    def countSubstrings(s: str, c: str) -> int:
        # Count the number of occurrences of character 'c' in string 's'
        count = s.count(c)

        # Calculate the number of substrings that can be formed from 'count' occurrences
        # Using the formula for the sum of the first 'count' natural numbers: count * (count + 1) // 2
        ans = count * (count + 1) // 2

        # Return the calculated number of substrings
        return ans


print(Solution.countSubstrings(s="abada", c="a"))
