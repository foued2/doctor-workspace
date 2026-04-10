from collections import deque
from typing import Optional


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def listToBinaryTree(lst):
    # If the list is empty, return None (no tree)
    if not lst:
        return None

    # Initialize the root of the tree
    root = TreeNode(lst[0])
    queue = deque([root])

    # Index in the list for the current node's children
    i = 1

    # Loop until the queue is empty, or we run out of list elements
    while queue and i < len(lst):
        # Get the current node from the queue
        current_node = queue.popleft()

        # Check if there's a left child
        if lst[i] is not None:
            left_child = TreeNode(lst[i])
            current_node.left = left_child
            queue.append(left_child)
        i += 1

        # Check if there's a right child
        if i < len(lst) and lst[i] is not None:
            right_child = TreeNode(lst[i])
            current_node.right = right_child
            queue.append(right_child)
        i += 1

    return root


class Solution:
    @staticmethod
    def maxLevelSum(root: Optional[TreeNode]) -> int:
        """
        Binary tree, Breadth first search (BFS), Queue, Level order traversal
        Find the level of the binary tree with the maximum sum of node values.
        """
        # Initialize variables to track the maximum sum and the level with the maximum sum
        maximum_sum = -float('inf')  # Start with negative infinity to handle any possible sum
        min_level = 0  # Variable to store the level with the maximum sum

        # If the tree is empty, return -1 (or another value indicating an empty tree)
        if not root:
            return -1

        # Initialize a queue to perform level order traversal
        queue = deque([root])
        level = 0  # To track the current level in the tree

        # Loop until the queue is empty
        while queue:
            # Reset the sum for the current level
            level_sum = 0
            level += 1  # Move to the next level
            # Number of nodes at the current level
            level_length = len(queue)

            # Iterate over all nodes at the current level
            for _ in range(level_length):
                # Dequeue a node from the front of the queue
                node = queue.popleft()

                # Add the node's value to the current level sum
                level_sum += node.val

                # Enqueue the left child if it exists
                if node.left:
                    queue.append(node.left)

                # Enqueue the right child if it exists
                if node.right:
                    queue.append(node.right)

            # After processing the current level, check if its sum is the highest
            if level_sum > maximum_sum:
                min_level = level  # Update the level with the maximum sum
                maximum_sum = level_sum  # Update the maximum sum
            elif level_sum == maximum_sum:
                # If the level sum is equal to the current maximum, choose the smallest level number
                min_level = min(min_level, level)

        return min_level  # Return the level with the maximum sum


print(Solution.maxLevelSum(root=listToBinaryTree([1, 7, 0, 7, -8, None, None])))
