from collections import deque
from typing import Optional, Tuple


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    @staticmethod
    def isCousins(root: Optional[TreeNode], x: int, y: int) -> bool:
        # If the tree is empty, return False
        if not root:
            return False

        # Initialize a queue to perform level order traversal
        # The queue contains tuples of (node, parent)
        queue: deque[Tuple[TreeNode, Optional[TreeNode]]] = deque([(root, None)])

        while queue:
            # Initialize variables to track if x and y are found at the current level
            x_found = y_found = None
            level_length = len(queue)

            for _ in range(level_length):
                # Dequeue a node from the front of the queue
                node, parent = queue.popleft()

                # Check if the current node is x or y
                if node.val == x:
                    x_found = parent
                if node.val == y:
                    y_found = parent

                # Enqueue the left child if it exists
                if node.left:
                    queue.append((node.left, node))

                # Enqueue the right child if it exists
                if node.right:
                    queue.append((node.right, node))

            # After processing all nodes at the current level, check if both x and y were found
            if x_found and y_found:
                # They are cousins if they have different parents
                return x_found != y_found
            if x_found or y_found:
                # If only one of x or y was found at this level, they can't be cousins
                return False

        # If neither x nor y are found, return False
        return False


# Example usage:
root = TreeNode(1)
root.left = TreeNode(2)
root.right = TreeNode(3)
root.left.right = TreeNode(4)
root.right.right = TreeNode(5)

solution = Solution()
print(solution.isCousins(root, 4, 5))  # Output: True
