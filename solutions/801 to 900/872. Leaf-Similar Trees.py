from typing import Optional


# Definition for a binary tree node.
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    @staticmethod
    def leafSimilar(root1: Optional[TreeNode], root2: Optional[TreeNode]) -> bool:
        def collectLeafNodes(root):
            """
            Binary Tree, DFS, Preorder Traversal
            Helper function to collect leaf nodes using DFS traversal.
            """
            if not root:
                return []
            if not root.left and not root.right:
                return [root.val]
            left_leaves = collectLeafNodes(root.left)
            right_leaves = collectLeafNodes(root.right)
            return left_leaves + right_leaves

        # Collect leaf nodes for both trees
        leaves1 = collectLeafNodes(root1)
        leaves2 = collectLeafNodes(root2)

        # Compare the collected leaf nodes
        return leaves1 == leaves2


# Example usage:
# Constructing binary trees:
# Tree 1:
#        3
#       / \
#      5   1
#     / \   \
#    6   2   9
#       /
#      7
root1 = TreeNode(3)
root1.left = TreeNode(5)
root1.right = TreeNode(1)
root1.left.left = TreeNode(6)
root1.left.right = TreeNode(2)
root1.right.right = TreeNode(9)
root1.left.right.left = TreeNode(7)

# Tree 2:
#        3
#       / \
#      5   1
#     / \
#    6   2
#       /
#      7
root2 = TreeNode(3)
root2.left = TreeNode(5)
root2.right = TreeNode(1)
root2.left.left = TreeNode(6)
root2.left.right = TreeNode(2)
root2.left.right.left = TreeNode(7)

# Check if trees root1 and root2 are leaf similar
print(Solution.leafSimilar(root1, root2))  # Output: True
