# Definition for a binary tree node.
from typing import Optional


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    @staticmethod
    def evaluateTree(root: Optional[TreeNode]) -> bool:
        def postOrderTraversal(node: Optional[TreeNode], stack: list):
            # Base case: if the current node is None, return
            if not node:
                return

            # Recursively traverse the left subtree
            postOrderTraversal(node.left, stack)
            # Recursively traverse the right subtree
            postOrderTraversal(node.right, stack)

            # Process the current node based on its value
            if node.val == 0:
                # 0 represents False
                stack.append(False)
            elif node.val == 1:
                # 1 represents True
                stack.append(True)
            elif node.val == 2:
                # 2 represents the 'Or' operator
                right = stack.pop()
                left = stack.pop()
                stack.append(left or right)
            elif node.val == 3:
                # 3 represents the 'And' operator
                right = stack.pop()
                left = stack.pop()
                stack.append(left and right)

        # Initialize an empty stack to hold boolean values and operators
        stack = []
        # Start the post-order traversal from the root
        postOrderTraversal(root, stack)
        # Return the final result, which should be the only element left in the stack
        return stack[0] if stack else False


# Helper function to create a binary tree from a list (for testing purposes)
def insertLevelOrder(arr, root, i, n):
    if i < n:
        if arr[i] is None:
            return None
        temp = TreeNode(val=arr[i])
        root = temp
        root.left = insertLevelOrder(arr, root.left, 2 * i + 1, n)
        root.right = insertLevelOrder(arr, root.right, 2 * i + 2, n)
    return root


# Example usage
# Input: root = [1, 0, 48, None, None, 12, 49]
arr = [2, 1, 3, None, None, 0, 1]
n = len(arr)
root = insertLevelOrder(arr, None, 0, n)

# Instantiate the solution and evaluate the tree
solution = Solution()
result = solution.evaluateTree(root)
print("The evaluation of the tree is:", result)
