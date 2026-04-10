from typing import List


class Solution:
    @staticmethod
    def splitWordsBySeparator(words: List[str], separator: str) -> List[str]:
        result = []  # Initialize an empty list to store the non-empty parts

        for word in words:  # Iterate through each word in the input list 'words'
            parts = word.split(separator)  # Split the word by the separator 'separator'

            for part in parts:  # Iterate through the parts obtained from splitting
                if part:  # Check if the split part 'part' is non-empty
                    result.append(part)  # If non-empty, append it to the result list 'result'

        return result  # Return the result list containing only non-empty parts


print(Solution.splitWordsBySeparator(words=["$easy$", "$problem$"], separator="$"))
