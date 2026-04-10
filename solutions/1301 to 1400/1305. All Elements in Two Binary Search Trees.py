from typing import List


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    @staticmethod
    def getAllElements(root1: TreeNode, root2: TreeNode) -> List[int]:
        # Initialize an empty list to store elements from both trees
        elements = []

        # Define a stack for iterative pre-order traversal
        stack = [root1]

        # Traverse the first tree in pre-order
        while stack:
            node = stack.pop()
            if node:
                # Visit the current node
                elements.append(node.val)
                # Push right and left children to the stack (right first, because stack is LIFO)
                stack.append(node.right)
                stack.append(node.left)

        # Reuse the stack for the second tree
        stack = [root2]

        # Traverse the second tree in pre-order
        while stack:
            node = stack.pop()
            if node:
                # Visit the current node
                elements.append(node.val)
                # Push right and left children to the stack (right first, because stack is LIFO)
                stack.append(node.right)
                stack.append(node.left)

        # Sort the collected elements
        elements.sort()

        return elements


# Example usage:
# Example tree 1:
#     2
#    / \
#   1   4
root_1 = TreeNode(2)
root_1.left = TreeNode(1)
root_1.right = TreeNode(4)

# Example tree 2:
#     1
#    / \
#   0   3
root_2 = TreeNode(1)
root_2.left = TreeNode()
root_2.right = TreeNode(3)

# Get all elements from both trees
result = Solution.getAllElements(root_1, root_2)
print(result)  # Output should be: [0, 1, 1, 2, 3, 4]
