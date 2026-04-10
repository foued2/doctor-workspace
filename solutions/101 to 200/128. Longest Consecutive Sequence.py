from typing import List


class UnionFind:
    def __init__(self, nums: List[int]):
        # Initialize parents and sizes dictionaries
        self.parents = {num: num for num in nums}
        self.sizes = {num: 1 for num in nums}

    def find(self, x: int) -> int:
        # Find operation with path compression
        if self.parents[x] != x:
            self.parents[x] = self.find(self.parents[x])
        return self.parents[x]

    def union(self, x: int, y: int) -> None:
        # Union operation with union by rank
        root_x = self.find(x)
        root_y = self.find(y)
        if root_x != root_y:
            if self.sizes[root_x] < self.sizes[root_y]:
                self.parents[root_x] = root_y
                self.sizes[root_y] += self.sizes[root_x]
            else:
                self.parents[root_y] = root_x
                self.sizes[root_x] += self.sizes[root_y]


class Solution:
    @staticmethod
    def longestConsecutive(nums: List[int]) -> int:
        if not nums:
            return 0

        # Initialize UnionFind object
        uf = UnionFind(nums)

        # Record the frequency of each number
        num_freq = {num: 1 for num in nums}

        max_length = 1
        for num in nums:
            # Check if the consecutive number exists
            if num + 1 in num_freq:
                uf.union(num, num + 1)
                max_length = max(max_length, uf.sizes[uf.find(num)])

        return max_length


# Test the function with a sample list of numbers and print the result
print(Solution.longestConsecutive(nums=[100, 4, 200, 1, 3, 2]))
