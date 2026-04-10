from typing import Optional


# Definition for a binary tree node.
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    @staticmethod
    def rangeSumBST(root: Optional[TreeNode], low: int, high: int) -> int:
        # Define a helper function for in-order traversal
        def inOrderTraversal(node: Optional[TreeNode]) -> int:
            # Base case: if the current node is None, return 0
            if not node:
                return 0

            # Initialize sum to 0
            sum_ = 0

            # Traverse the left subtree if the current node's value is greater than low
            if node.val > low:
                sum_ += inOrderTraversal(node.left)

            # Include the current node's value if it is within the range [low, high]
            if low <= node.val <= high:
                sum_ += node.val

            # Traverse the right subtree if the current node's value is less than high
            if node.val < high:
                sum_ += inOrderTraversal(node.right)

            return sum_

        # Call the helper function starting from the root
        return inOrderTraversal(root)


# Helper function to create a binary tree from a list (for testing purposes)
def insertLevelOrder(arr, root, i, n):
    # Base case for recursion
    if i < n:
        # If the element is None, return None
        if arr[i] is None:
            return None

        # Create a new TreeNode
        temp = TreeNode(val=arr[i])
        root = temp

        # Recursively insert the left child
        root.left = insertLevelOrder(arr, root.left, 2 * i + 1, n)

        # Recursively insert the right child
        root.right = insertLevelOrder(arr, root.right, 2 * i + 2, n)

    return root


# Example usage
# Input: root = [10, 5, 15, 3, 7, None, 18]
arr = [10, 5, 15, 3, 7, None, 18]
n = len(arr)
root = insertLevelOrder(arr, None, 0, n)
low = 7
high = 15

# Instantiate the solution and evaluate the tree
solution = Solution()
result = solution.rangeSumBST(root, low, high)
print("The evaluation of the tree is:", result)
