from typing import List


class Solution:
    @staticmethod
    def arrayRankTransform(arr: List[int]) -> List[int]:
        # Step 1: Sort the unique elements of arr
        sorted_unique = sorted(set(arr))

        # Step 2: Create a dictionary mapping each element to its rank
        rank_dict = {num: rank + 1 for rank, num in enumerate(sorted_unique)}

        # Step 3: Transform the original array to its rank representation
        rank_transformed = [rank_dict[num] for num in arr]

        return rank_transformed


if __name__ == '__main__':
    print(Solution.arrayRankTransform([37, 12, 28, 9, 100, 56, 80, 5, 12]))
