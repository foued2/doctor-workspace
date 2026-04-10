from collections import Counter  # Importing Counter from collections to count occurrences of elements
from typing import List  # Importing List for type hinting


class Solution:
    @staticmethod
    def duplicateNumbersXOR(nums: List[int]) -> int:
        # Initialize the variable to store the XOR result of elements that appear exactly twice
        ans = 0

        # Create a counter-object to count occurrences of each element in the nums list
        counter = Counter(nums)

        # Iterate over the items (key-value pairs) in the counter-dictionary
        for key, value in counter.items():
            # Check if the element appears exactly twice
            if value == 2:
                # XOR the element with ans.
                # XORing twice cancels out the element, leaving only elements that appear exactly twice
                ans ^= key

        # Return the result which is the XOR of all elements that appear exactly twice
        return ans


print(Solution.duplicateNumbersXOR(nums=[1, 2, 1, 3]))
