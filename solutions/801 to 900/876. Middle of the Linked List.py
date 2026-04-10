from typing import Optional


class ListNode:
    def __init__(self, val=0, next_node=None):
        self.val = val
        self.next = next_node


class Solution:
    @staticmethod
    def middleNode(head: Optional[ListNode]) -> Optional[ListNode]:
        """
        Linked list
        """
        # Check if the linked list has only one node
        if not head.next:
            return head

        # Initialize the slow and fast pointers
        slow_ptr = head  # Slow pointer starts at the head
        fast_ptr = head  # Fast pointer starts at the head

        # Iterate through the linked list
        while fast_ptr.next:
            # Move the slow pointer one step forward
            slow_ptr = slow_ptr.next
            # Move the fast pointer two steps forward
            fast_ptr = fast_ptr.next.next

        return slow_ptr
