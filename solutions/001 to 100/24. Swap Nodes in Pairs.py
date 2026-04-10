from typing import Optional


class ListNode:
    def __init__(self, val=0, next_node=None):
        self.val = val
        self.next = next_node


class Solution:
    def swapPairs(self, head: ListNode) -> Optional[ListNode]:
        # Base Case: If either the current node or the next node is None, or both are None, return the current node.
        if head is None or head.next is None:
            return head

        # Swap the current node with its next node's next node.
        next_node = head.next
        head.next = self.swapPairs(next_node.next)
        next_node.next = head

        # Return the new head of the swapped pair.
        return next_node


class Solution2:
    @staticmethod
    def swapPairs(head: ListNode) -> Optional[ListNode]:
        if head is None:
            return head

        # Step 1: Create dummy node
        dummy = ListNode()  # Create a dummy node with a placeholder value
        dummy.next = head  # Set the next pointer of the dummy node to the head of the original list

        # Step 2: Reverse each pair of adjacent nodes
        prev = dummy  # Initialize a pointer to the dummy node
        while prev.next and prev.next.next:
            first = prev.next  # Pointer to the first node of the current pair
            second = prev.next.next  # Pointer to the second node of the current pair

            # Reverse the pair of nodes
            first.next = second.next  # Update the next pointer of the first node to skip the second node
            second.next = first  # Reverse the order of the pair

            # Update the pointers for the next iteration
            prev.next = second  # Update the next pointer of the previous node to point to the new first node
            prev = first  # Move the prev pointer two steps forward for the next pair

        return dummy.next
