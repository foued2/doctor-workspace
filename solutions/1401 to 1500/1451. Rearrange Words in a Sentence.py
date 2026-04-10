class Solution:
    @staticmethod
    def arrangeWords(text: str) -> str:
        # Split the input text into a list of words
        words = text.split()

        # Convert the first word to lowercase to ensure proper ordering
        words[0] = words[0].lower()

        # Sort the words by their length
        words = sorted(words, key=lambda x: len(x))

        # Join the sorted words into a single string
        arranged_text = ' '.join(words)

        # Capitalize the first letter of the arranged text
        arranged_text = arranged_text.capitalize()

        return arranged_text


# Test case
text = "Leetcode is cool"

# Create an instance of Solution and test the method
solution = Solution()
output = solution.arrangeWords(text)
print(output)  # Expected: "Is cool leetcode"

print(Solution.arrangeWords(text="Keep calm and code on"))
