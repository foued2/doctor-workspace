class Solution:
    @staticmethod
    def reverseWords(s: str) -> str:
        res = []  # Initialize an empty list to store the reversed words
        for word in s.split():  # Split the input string into words
            word = word[::-1]  # Reverse the current word
            res.append(word)  # Append the reversed word to the result list
        return " ".join(res)  # Join the reversed words with a space and return the result


if __name__ == '__main__':
    # Example usage of the function
    print(Solution().reverseWords("Let's take LeetCode contest"))