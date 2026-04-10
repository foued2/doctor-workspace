class Solution:
    @staticmethod
    def canBeTypedWords(text: str, brokenLetters: str) -> int:
        # Initialize the answer counter to 0
        ans = 0

        # Split the input text into individual words using space as the delimiter
        for word in text.split():
            # Assume the word can be typed initially
            flag = True

            # Check each character in the word
            for char in word:
                # If the character is in the brokenLetters string
                if char in brokenLetters:
                    # Set the flag to False indicating the word cannot be typed
                    flag = False
                    # Break the inner loop as we found a broken letter
                    break

            # If the flag is still True, it means the word can be typed
            if flag:
                # Increment the answer counter
                ans += 1

        # Return the number of words that can be typed
        return ans


# Example usage
print(Solution.canBeTypedWords(text="leet code", brokenLetters="lt"))


class Solution:
    @staticmethod
    def canBeTypedWords(text: str, brokenLetters: str) -> int:
        # Split the input text into individual words using space as the delimiter
        words = text.split(" ")

        # Convert the brokenLetters string into a set for efficient look-up
        broken_set = set(brokenLetters)

        # Use a list comprehension to check each word
        # set(word).isdisjoint(broken_set) returns True if word has no characters in broken_set
        # sum(...) will count the number of True values in the list comprehension result
        return sum([set(word).isdisjoint(broken_set) for word in words])


# Example usage
solution = Solution()
print(solution.canBeTypedWords("hello world", "ad"))  # Output: 1
print(solution.canBeTypedWords("leet code", "lt"))  # Output: 1
print(solution.canBeTypedWords("leet code", "e"))  # Output: 0
