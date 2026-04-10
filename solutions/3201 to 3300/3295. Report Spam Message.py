from typing import List


class Solution:
    @staticmethod
    def reportSpam(message: List[str], bannedWords: List[str]) -> bool:
        # Convert the list of banned words into a set for O(1) average-time complexity lookups
        s = set(bannedWords)
        count = 0

        # Iterate over each word in the message
        for word in message:
            # Check if the word is in the set of banned words
            if word in s:
                count += 1
                # If at least two banned words are found, return True indicating spam
                if count >= 2:
                    return True

        # If less than two banned words are found, return False indicating no spam
        return False


if __name__ == '__main__':
    # Testing the static method with sample messages and banned words
    print(Solution().reportSpam(message=["hello", "world", "leetcode"],
                                bannedWords=["world", "hello"]))  # Should return True
    print(Solution().reportSpam(message=["hello", "programming", "fun"],
                                bannedWords=["world", "programming", "leetcode"]))  # Should return False