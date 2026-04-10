from typing import List


class Solution:
    @staticmethod
    def similarPairs(words: List[str]) -> int:
        # Initialize the answer variable to keep track of the number of similar pairs
        ans = 0

        # Create a dictionary to store the unique representation of each word
        table = {}

        # Iterate over each word in the input list
        for word in words:
            # Convert the word into a set to get unique characters, sort them,
            # and join back into a string to get a unique representation of the word
            word = ''.join(sorted(set(list(word))))

            # If this unique representation is already in the table, increment its count
            if word in table:
                table[word] += 1
            # If this unique representation is not in the table, add it with a count of 1
            else:
                table[word] = 1

        # Iterate over the counts of each unique word representation in the table
        for value in table.values():
            # For each count, calculate the number of ways to pick 2 items from the count
            # This is done using the combination formula nC2 = n*(n-1)/2
            ans += (value * (value - 1)) // 2

        # Return the final calculated number of similar pairs
        return ans


# Test the function with the provided example list
print(Solution.similarPairs(words=["aabb", "ab", "ba"]))

