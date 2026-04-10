from typing import List


class Solution:
    @staticmethod
    def totalFruit(fruits: List[int]) -> int:
        n = len(fruits)  # Length of the list of fruits
        trees = dict()  # Dictionary to track the count of each type of fruit
        i, j = 0, 0  # Two pointers to define the window [i, j]
        max_fruit = 0  # Variable to store the maximum number of fruits collected

        # Loop through the list of fruits using the 'j' pointer
        while j < n:
            # Add the current fruit to the tree dictionary and update its count
            if fruits[j] not in trees:
                trees[fruits[j]] = 0
            trees[fruits[j]] += 1

            # Shrink the window if there are more than two types of fruits in the window
            while len(trees) > 2:
                # Remove the fruit at the 'i' pointer from the window and update its count
                trees[fruits[i]] -= 1
                # If the count of the fruit becomes zero, remove it from the dictionary
                if trees[fruits[i]] == 0:
                    del trees[fruits[i]]
                # Move the 'i' pointer to shrink the window
                i += 1

            # Update the maximum fruit count by comparing it with the current window size
            max_fruit = max(max_fruit, j - i + 1)

            # Move the 'j' pointer to expand the window
            j += 1

        # Return the maximum number of fruits collected
        return max_fruit


if __name__ == '__main__':
    print(Solution.totalFruit(fruits=[1, 2, 1]))  # Output: 3
    print(Solution.totalFruit(fruits=[1, 2, 3, 2, 2]))  # Output: 4
    print(Solution.totalFruit(fruits=[0, 1, 2, 2]))  # Output: 3
