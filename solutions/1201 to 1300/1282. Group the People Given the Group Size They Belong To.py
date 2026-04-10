from typing import List
from collections import defaultdict


class Solution:
    @staticmethod
    def groupThePeople(groupSizes: List[int]) -> List[List[int]]:
        # Dictionary to hold lists of people's indices for each group size
        groups = defaultdict(list)

        # Result list to store the final groups
        result = []

        # Iterate over each person's group size
        for person_index, group_size in enumerate(groupSizes):
            # Append the person's index to the list corresponding to their group size
            groups[group_size].append(person_index)

            # If the list for this group size reaches the required size
            if len(groups[group_size]) == group_size:
                # Append this list to the result as a completed group
                result.append(groups.pop(group_size))

        # Return the list of groups
        return result


print(Solution.groupThePeople(groupSizes=[3, 3, 3, 3, 3, 1, 3]))
