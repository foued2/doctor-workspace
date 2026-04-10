from typing import Optional


class ListNode:
    def __init__(self, val=0, next_node=None):
        self.val = val
        self.next = next_node


class Solution:
    @staticmethod
    def removeElements(head: Optional[ListNode], val: int) -> Optional[ListNode]:
        """
        Remove all elements from a linked list of integers that have a given value.

        Args:
            head (Optional[ListNode]): The head of the linked list.
            val (int): The value to be removed from the linked list.

        Returns:
            Optional[ListNode]: The head of the updated linked list after removal.

        """

        # Create a dummy node and point its next to the head of the provided linked list
        dummy = ListNode()
        dummy.next = head

        # Initialize a pointer to traverse the linked list and a pointer to keep track of the previous node
        prev = dummy

        # Traverse the linked list
        while prev:
            # Check if the value of the current node is equal to the target value
            if prev.next and prev.next.val == val:
                # If it matches, remove the node by skipping it in the linked list
                prev.next = prev.next.next
            else:
                # Move the pointer to the next node
                prev = prev.next

        # Return the head of the updated linked list
        return dummy.next
