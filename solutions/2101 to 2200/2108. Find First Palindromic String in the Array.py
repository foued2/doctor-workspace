from typing import List


class Solution:
    @staticmethod
    def firstPalindrome(words: List[str]) -> str:
        """
        Two pointers
        """
        ans = ''
        for word in words:
            i = 0
            j = len(word) - 1
            # Reset the found flag for each word
            found = True
            # Use while loop to check for palindrome
            while i <= j:
                if word[i] != word[j]:
                    found = False
                    break  # Exit the loop if characters don't match
                i += 1
                j -= 1
            # Check if the word is a palindrome
            if found:
                ans = word
                break  # Exit the loop if a palindrome is found
        return ans


print(Solution.firstPalindrome(words=["abc", "car", "ada", "racecar", "cool"]))
