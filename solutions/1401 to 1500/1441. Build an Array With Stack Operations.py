from typing import List


class Solution:
    @staticmethod
    def buildArray(target: List[int], n: int) -> List[str]:
        # Initialize an empty list to store the operations
        res = []
        # Initialize a variable to track the current number
        num = 1
        # Iterate until the current number reaches the last element in the target array
        while num <= target[-1]:
            # If the current number is not in the target array, it must be pushed and then popped
            if num not in target:
                res.append("Push")
                res.append("Pop")
            # If the current number is in the target array, it must be pushed
            else:
                res.append("Push")
            # Increment the current number
            num += 1
        # Return the list of operations
        return res


print(Solution.buildArray(target=[1, 3], n=3))
