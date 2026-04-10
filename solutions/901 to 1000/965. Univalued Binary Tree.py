from typing import Optional


# Definition for a binary tree node.
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def isUnivalTree(self, root: Optional[TreeNode]) -> bool:
        """
        Binary tree, Depth-First Search DFS, Preorder Traversal
        """
        # Base case: If the root is None, return True
        if root is None:
            return True

        # Check if the root value is different from its left child or right child
        if root.left and root.left.val != root.val:
            return False
        if root.right and root.right.val != root.val:
            return False

        # Recursively check if the left subtree and right subtree are univalued
        return self.isUnivalTree(root.left) and self.isUnivalTree(root.right)
