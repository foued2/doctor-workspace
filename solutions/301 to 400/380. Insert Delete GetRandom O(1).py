from __future__ import annotations

import random
from typing import Any


class RandomizedSet:
    def __init__(self):
        # Initialize a new instance of the RandomizedSet class.
        self.random_set = set()  # Initialize an empty set to store elements

    def insert(self, val: int) -> bool:
        # Inserts an integer val into the set.
        # Args:
        #     val: An integer to insert into the set.
        # Returns:
        #     True if val was not present in the set and was inserted successfully, False otherwise.
        if val in self.random_set:  # Check if val is already present in the set
            return False  # If val is already present, return False
        else:
            self.random_set.add(val)  # If val is not present, add it to the set
            return True  # Return True to indicate successful insertion

    def remove(self, val: int) -> bool:
        # Removes an integer val from the set.
        # Args:
        #     val: An integer to remove from the set.
        # Returns:
        #     True if val was present in the set and was removed successfully, False otherwise.
        if val in self.random_set:  # Check if val is present in the set
            self.random_set.remove(val)  # If val is present, remove it from the set
            return True  # Return True to indicate successful removal
        else:
            return False  # If val is not present, return False

    def getRandom(self) -> Any | None:
        # Returns a random integer from the set.
        # Returns:
        #     A random integer from the set, or None if the set is empty.
        if self.random_set:  # Check if the set is not empty
            return random.choice(list(self.random_set))  # Return a random element from the set
        else:
            return None  # If the set is empty, return None


# Example of input
randomized_set = RandomizedSet()
print(randomized_set.insert(1))  # Inserts 1 into the set
randomized_set.remove(2)  # Removes 2 from the set (not present, returns False)
randomized_set.insert(2)  # Inserts 2 into the set
randomized_set.getRandom()  # Gets a random element from the set
