from typing import Optional, List


# Definition for a binary tree node.
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    @staticmethod
    def getLonelyNodes(root: Optional[TreeNode]) -> List[int]:
        result = []
        # Base case: If the root is None, return True
        if root is None:
            return result
        if root.left is None and root.right is None:
            result.append(root.val)
        return result + Solution.getLonelyNodes(root.left) + Solution.getLonelyNodes(root.right)


if __name__ == '__main__':
    root = TreeNode(1)
    root.left = TreeNode(2)
    root.right = TreeNode(3)
    root.left.left = TreeNode(4)
    root.left.right = TreeNode(5)
    print(Solution.getLonelyNodes(root))


