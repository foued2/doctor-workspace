from collections import Counter
from typing import List


class Solution:
    @staticmethod
    def countWords(words1: List[str], words2: List[str]) -> int:
        # Initialize the answer to 0, this will count the common words appearing exactly once in both lists
        ans = 0

        # Create a counter for the words in words2 to count the occurrences of each word
        counter2 = Counter(words2)

        # Create a counter for the words in words1 to count the occurrences of each word
        counter1 = Counter(words1)

        # Loop through each word and its count in counter1
        for key, value in counter1.items():
            # Check if the word is also in counter2
            if key in counter2:
                # Check if the word appears exactly once in both lists
                if value == counter2[key] == 1:
                    # Increment the answer count since this word meets the criteria
                    ans += 1

        # Return the final count of words that appear exactly once in both lists
        return ans


print(Solution.countWords(words1=["leetcode", "is", "amazing", "as", "is"], words2=["amazing", "leetcode", "is"]))
