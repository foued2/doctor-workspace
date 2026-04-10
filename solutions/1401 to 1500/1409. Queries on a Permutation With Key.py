from typing import List


class Solution:
    @staticmethod
    def processQueries(queries: List[int], m: int) -> List[int]:
        # Initialize the result list
        res = []

        # Create the initial permutation list p with elements from 1 to m
        p = [i for i in range(1, m + 1)]

        # Iterate through each query in the queries list
        for i, num in enumerate(queries):
            # Find the index of the current query number in the permutation list p
            idx = p.index(num)

            # Append the index to the result list
            res.append(idx)

            # Remove the element at idx from p and insert it at the beginning
            p.insert(0, p.pop(idx))

        # Return the result list
        return res


print(Solution.processQueries(queries=[7, 5, 5, 8, 3], m=8))


class FenwickTree:
    def __init__(self, size: int):
        # Initialize the Fenwick Tree with the given size (1-based indexing)
        self.size = size
        self.tree = [0] * (size + 1)

    def update(self, index: int, delta: int):
        # Update the tree with the delta value at the given index
        while index <= self.size:
            self.tree[index] += delta
            index += index & -index

    def query(self, index: int) -> int:
        # Query the prefix sum up to the given index
        sum_ = 0
        while index > 0:
            sum_ += self.tree[index]
            index -= index & -index
        return sum_


class Solution:
    @staticmethod
    def processQueries(queries: List[int], m: int) -> List[int]:
        # Initialize the result list
        res = []

        # Initialize the Fenwick Tree with a size of m + len(queries)
        fenwick_tree = FenwickTree(m + len(queries))

        # Create a position map to keep track of the current positions of the elements
        pos = {i: m + i for i in range(1, m + 1)}

        # Update the Fenwick Tree with initial positions
        for i in range(1, m + 1):
            fenwick_tree.update(m + i, 1)

        # Iterate through each query
        for i, query in enumerate(queries):
            # Get the current position of the query element
            current_pos = pos[query]

            # Find the number of elements before the current position
            num_elements_before = fenwick_tree.query(current_pos) - 1

            # Append the result
            res.append(num_elements_before)

            # Update the position of the query element to the front
            fenwick_tree.update(current_pos, -1)
            new_pos = m - i
            fenwick_tree.update(new_pos, 1)
            pos[query] = new_pos

        # Return the result list
        return res


# Example usage:
solution = Solution()
print(solution.processQueries([3, 1, 2, 1], 5))  # Output: [2, 1, 2, 1]
