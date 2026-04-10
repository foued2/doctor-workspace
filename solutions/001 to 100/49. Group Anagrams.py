from typing import List


class Solution:
    @staticmethod
    def groupAnagrams(strs: List[str]) -> List[List[str]]:
        # Initialize an empty dictionary to store groups of anagrams
        anagrams = {}

        # Iterate through the list of words
        for word in strs:
            # Sort the characters of the word alphabetically
            sorted_word = ''.join(sorted(word))

            # Check if the sorted word is already a key in the dictionary
            if sorted_word in anagrams:
                # If the key exists, append the word to the list of anagrams
                anagrams[sorted_word].append(word)
            else:
                # If the key does not exist, create a new key and initialize it with a list containing the word
                anagrams[sorted_word] = [word]

        # Convert the values of the dictionary to a list and return
        return list(anagrams.values())


# Example usage:
if __name__ == "__main__":
    # Create an instance of the Solution class
    solution = Solution()

    # Test the groupAnagrams method with sample input
    print(solution.groupAnagrams(strs=["eat", "tea", "tan", "ate", "nat", "bat"]))
