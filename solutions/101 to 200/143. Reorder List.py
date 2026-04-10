from typing import Optional

from main import ListNode


class Solution:
    @staticmethod
    def reorderList(head: Optional[ListNode]) -> None:
        """
        Do not return anything, modify head in-place instead.
        """
        if not head or not head.next:
            return  # Nothing to reorder for an empty or single-node list

        # Step 1: Find the middle by moving fast & slow iterators
        fast = slow = head
        while fast and fast.next:
            fast = fast.next.next
            slow = slow.next

        # Step 2: Use 'slow' as the beginning of the right half
        right_head = slow.next
        slow.next = None  # Cut off the left part from the right

        # Step 3: Reverse the right half of the linked list
        prev = None
        current = right_head
        while current is not None:
            next_node = current.next  # Store the next node temporarily
            current.next = prev  # Reverse the next pointer
            prev = current  # Update the previous node
            current = next_node  # Move to the next node

        # At the end of this loop, 'prev' will be the new beginning of the reversed right half

        # Step 4: Merge the modified right halfback into the left half
        left = head
        while prev is not None:
            next_left = left.next
            next_right = prev.next

            left.next = prev
            prev.next = next_left

            left = next_left
            prev = next_right

        # Return the head of the modified list
        return head
