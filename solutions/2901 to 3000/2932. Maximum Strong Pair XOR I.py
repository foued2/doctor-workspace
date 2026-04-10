from typing import List


class Solution:
    @staticmethod
    def maximumStrongPairXor(nums: List[int]) -> int:
        """
        Sliding window
        """
        # Initialize the maximum XOR to the smallest possible value
        ans = -float('inf')
        # Get the length of the input list
        n = len(nums)
        # Initialize the left and right pointers
        i, j = 0, 0

        # Iterate while the right pointer is within the bounds of the list
        while i < n:
            while j < n:
                # Check if the current window satisfies the condition
                if abs(nums[i] - nums[j]) <= min(nums[i], nums[j]):
                    # Calculate the XOR of the current pair
                    xor = nums[i] ^ nums[j]
                    # Update the maximum XOR if the current XOR is greater
                    ans = max(ans, xor)
                    # Print the current pair and the current maximum XOR for debugging
                    print(nums[i], nums[j], ans)
                j += 1
            # Move the left pointer to the right and reset the right pointer
            i += 1
            j = i

        # Return the maximum XOR found
        return ans


# Example usage:
nums = [1, 2, 3, 4, 5]
print(Solution.maximumStrongPairXor(nums))  # Expected output: 7


class Node:
    def __init__(self):
        # Initialize the children to None and count to 0
        self.children = [None, None]
        self.cnt = 0


class Trie:
    # The highest bit position considered in the integers (0 to 127 for 7-bit numbers)
    HIGH_BIT = 6

    def __init__(self):
        # Initialize the root node of the Trie
        self.root = Node()

    def insert(self, val: int):
        # Start from the root node
        cur = self.root
        # Insert each bit of the value from highest to lowest
        for i in range(self.HIGH_BIT, -1, -1):
            # Get the current bit (either 0 or 1)
            bit = (val >> i) & 1
            # If the child node for this bit doesn't exist, create it
            if cur.children[bit] is None:
                cur.children[bit] = Node()
            # Move to the child node
            cur = cur.children[bit]
            # Increment the count of the current node
            cur.cnt += 1

    def delete(self, val: int):
        # Start from the root node
        cur = self.root
        # Delete each bit of the value from highest to lowest
        for i in range(self.HIGH_BIT, -1, -1):
            # Get the current bit (either 0 or 1)
            bit = (val >> i) & 1
            # Move to the child node
            if cur.children[bit] is not None:
                cur = cur.children[bit]
                cur.cnt -= 1

    def max_xor(self, val: int) -> int:
        # Start from the root node
        cur = self.root
        # Initialize the result to 0
        res = 0
        # Compute the maximum XOR by traversing the Trie
        for i in range(self.HIGH_BIT, -1, -1):
            # Get the current bit (either 0 or 1)
            bit = (val >> i) & 1
            # Check if we can take the opposite bit (to maximize XOR)
            if cur.children[bit ^ 1] and cur.children[bit ^ 1].cnt > 0:
                # If the opposite bit exists and has count > 0, include this bit in the result
                res |= 1 << i
                # Move to the opposite child node
                cur = cur.children[bit ^ 1]
            else:
                # Move to the child node corresponding to the current bit
                cur = cur.children[bit]
        return res


class Solution:
    @staticmethod
    def maximumStrongPairXor(nums: List[int]) -> int:
        """
        Trie
        """
        # Sort the input list to facilitate the sliding window approach
        nums.sort()
        # Initialize the Trie
        trie = Trie()
        # Initialize the maximum XOR result to 0
        ans = 0
        # Initialize the left pointer of the sliding window
        left = 0

        # Iterate through each number in the sorted list
        for x in nums:
            # Insert the current number into the Trie
            trie.insert(x)
            # Adjust the left pointer to ensure the condition x <= 2 * nums[left] holds
            while x > 2 * nums[left]:
                # Remove numbers from the Trie that do not satisfy the condition
                trie.delete(nums[left])
                # Move the left pointer to the right
                left += 1
            # Calculate the maximum XOR with the current number
            ans = max(ans, trie.max_xor(x))
        return ans


# Example usage:
nums = [1, 2, 3, 4, 5]
print(Solution().maximumStrongPairXor(nums))  # Expected output: 7
