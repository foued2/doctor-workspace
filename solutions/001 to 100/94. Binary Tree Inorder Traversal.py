from typing import Optional, List


# Define the TreeNode class
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def inorderTraversal(self, root: Optional[TreeNode]) -> List[int]:
        # Initialize an empty list to store the result
        result = []

        # Check if the root exists
        if root:
            # Recursively traverse the left subtree
            result += self.inorderTraversal(root.left)
            # Append the value of the current node to the result list
            result.append(root.val)
            # Recursively traverse the right subtree
            result += self.inorderTraversal(root.right)

        # Return the final result list
        return result

