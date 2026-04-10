from typing import List

class Solution:
    @staticmethod
    def countMatches(items: List[List[str]], ruleKey: str, ruleValue: str) -> int:
        # Define the order of keys for easy indexing
        keys = ["type", "color", "name"]
        # Initialize a counter for the matches
        count = 0
        # Iterate through each item in the list of items
        for item in items:
            # Check if the value of the specified ruleKey matches the ruleValue for the current item
            if item[keys.index(ruleKey)] == ruleValue:
                # Increment the count if there is a match
                count += 1
        # Return the total count of matches
        return count


print(Solution.countMatches(
    items=[["phone", "blue", "pixel"], ["computer", "silver", "phone"], ["phone", "gold", "iphone"]], ruleKey="type",
    ruleValue="phone"))
