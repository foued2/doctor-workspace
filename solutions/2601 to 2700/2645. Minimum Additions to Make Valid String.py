from collections import Counter


class Solution:
    @staticmethod
    def addMinimum(word: str) -> int:
        # Count the frequency of each character in the input word
        count = Counter(word)

        # Get the list of frequencies of each character
        frequencies = list(count.values())

        # Calculate the minimum number of additions needed to equalize the frequencies
        ans = (max(frequencies) * 3) - sum(frequencies)

        return ans


# Example usage
if __name__ == '__main__':
    print(Solution.addMinimum(word="aaa"))  # Output: 6