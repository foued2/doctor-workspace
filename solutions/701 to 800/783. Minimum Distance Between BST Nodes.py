# Definition for a binary tree node.
from typing import Optional, List


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    @staticmethod
    def minDiffInBST(root: Optional[TreeNode]) -> int:
        # Helper function to perform in-order traversal and collect node values
        def inOrderTraversal(node: Optional[TreeNode], values: List[int]):
            if not node:
                return
            # Traverse the left subtree
            inOrderTraversal(node.left, values)
            # Add the node value to the list
            values.append(node.val)
            # Traverse the right subtree
            inOrderTraversal(node.right, values)

        # List to store the values of the nodes in in-order
        values = []
        inOrderTraversal(root, values)

        # Initialize the minimum difference to a large value
        min_diff = float('inf')

        # Iterate through the sorted values to find the minimum difference between consecutive nodes
        for i in range(1, len(values)):
            # Calculate the difference between consecutive values
            diff = values[i] - values[i - 1]
            # Update the minimum difference if the current difference is smaller
            if diff < min_diff:
                min_diff = diff

        # Return the minimum difference found
        return min_diff


# Helper function to create a binary tree from a list
def insertLevelOrder(arr, root, i, n):
    if i < n:
        if arr[i] is None:
            return None
        temp = TreeNode(val=arr[i])
        root = temp
        root.left = insertLevelOrder(arr, root.left, 2 * i + 1, n)
        root.right = insertLevelOrder(arr, root.right, 2 * i + 2, n)
    return root


# Input: root = [1, 0, 48, None, None, 12, 49]
arr = [1, 0, 48, None, None, 12, 49]
n = len(arr)
root = insertLevelOrder(arr, None, 0, n)

# Instantiate the solution and find the minimum difference in BST
solution = Solution()
min_diff = solution.minDiffInBST(root)
print("The minimum difference in the BST is:", min_diff)
