# Time:  O(n)
# Space: O(n)

# Design and implement a TwoSum class. It should support the following operations: add and find.
#
# add - Add the number to an internal data structure.
# find - Find if there exists any pair of numbers which sum is equal to the value.
#
# For example,
# add(1); add(3); add(5);
# find(4) -> true
# find(7) -> false

from collections import defaultdict


class TwoSum(object):

    def __init__(self):
        """
        Initialize your data structure here.
        """
        # We use a defaultdict to store the count of each number added.
        self.lookup = defaultdict(int)

    def add(self, number):
        """
        Add the number to an internal data structure.
        """
        # Increment the count of the number in the defaultdict.
        self.lookup[number] += 1

    def find(self, value):
        """
        Find if there exists any pair of numbers which sum is equal to the value.
        """
        # Iterate through each key in the defaultdict.
        for key in self.lookup:
            # Compute the difference between the value and the current key.
            num = value - key
            # Check if the difference exists in the defaultdict, and
            # ensure that the same number is not being used twice unless it's available more than once.
            if num in self.lookup and (num != key or self.lookup[key] > 1):
                return True
        return False


if __name__ == "__main__":
    # Create an instance of the TwoSum class.
    Sol = TwoSum()

    # Add numbers to the internal data structure.
    for i in (1, 3, 5):
        Sol.add(i)

    # Find if there exists any pair of numbers which sum is equal to the given value.
    for i in (4, 7):
        print(Sol.find(i))

