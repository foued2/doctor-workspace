class BinaryIndexedTree:
    def __init__(self, n):
        # Adjust the size based on the problem offset
        self.size = n + int(1e5 + 1)
        # Initialize the binary indexed tree with zeros
        self.tree = [0] * (self.size + 1)

    def update(self, index, delta):
        # Adjust the index for the problem offset
        index += int(1e5 + 1)
        # Update the tree by adding 'delta' to each node along the path
        while index <= self.size:
            self.tree[index] += delta
            # Move to the next index to update
            # low bit function is inlined for performance
            index += index & -index

    def query(self, index):
        # Adjust the index for the problem offset
        index += int(1e5 + 1)
        result = 0
        # Sum the values in the tree along the path to the root node
        while index > 0:
            result += self.tree[index]
            # Move to the parent index to continue the sum
            # low bit function is inlined for performance
            index -= index & -index
        return result


class Solution:
    @staticmethod
    def subarraysWithMoreZerosThanOnes(nums):
        # Calculate the length of the given 'nums' array
        length = len(nums)

        prefix_sums = [0]
        # Compute prefix sums, decrementing for zeros and incrementing for ones
        for value in nums:
            prefix_sums.append(prefix_sums[-1] + (value or -1))

        # Instantiate a `BinaryIndexedTree` with length of our prefix sums
        tree = BinaryIndexedTree(length + 1)
        # Define the modulo for result to keep it within bounds
        MOD = int(1e9 + 7)
        # Initialize answer to 0
        answer = 0

        # Iterate over the prefix sums
        for value in prefix_sums:
            # Query the tree for the range up to value - 1
            # and update the answer considering MOD
            answer = (answer + tree.query(value - 1)) % MOD
            # Update the tree with the current prefix sum value
            tree.update(value, 1)

        # Return the final answer
        return answer


if __name__ == '__main__':
    print(Solution.subarraysWithMoreZerosThanOnes([0, 1, 1, 0, 1, ]))
