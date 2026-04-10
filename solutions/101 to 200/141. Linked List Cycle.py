from typing import Optional


class ListNode:
    def __init__(self, val=0, next_node=None):
        self.val = val
        self.next = next_node


class Solution:
    @staticmethod
    def hasCycle(head: Optional[ListNode]) -> bool:
        # Check if the linked list is empty or has only one node
        if not head or not head.next:
            return False

        # Initialize the slow and fast pointers
        slow_ptr = head  # Slow pointer starts at the head
        fast_ptr = head.next  # Fast pointer starts at the node after the head

        # Iterate through the linked list
        while fast_ptr and fast_ptr.next:
            # Move the slow pointer one step forward
            slow_ptr = slow_ptr.next
            # Move the fast pointer two steps forward
            fast_ptr = fast_ptr.next.next

            # If the slow pointer meets the fast pointer, there is a cycle
            if slow_ptr == fast_ptr:
                return True

        # If the fast pointer reaches the end of the list (or becomes None), there is no cycle
        return False
