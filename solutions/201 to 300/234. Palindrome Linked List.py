from typing import Optional

from main import ListNode


class Solution:
    @staticmethod
    def isPalindrome(head: Optional[ListNode]) -> bool:
        # Edge case: If the list is empty or has only one node, it's a palindrome
        if not head or not head.next:
            return True

        # Step 1: Find the middle of the linked list
        slow = head
        fast = head

        # Use two pointers to find the middle of the linked list
        while fast.next and fast.next.next:
            slow = slow.next
            fast = fast.next.next

        # Now 'slow' is at the middle node

        # Step 2: Reverse the second half of the linked list
        prev = None
        current = slow.next

        while current:
            temp = current.next
            current.next = prev
            prev = current
            current = temp

        # 'prev' now points to the head of the reversed second half

        # Step 3: Compare the first half with the reversed second half,
        # Traverse the first half and the reversed second half simultaneously
        # If any corresponding nodes don't match, it's not a palindrome
        while prev:  # 'prev' is now the head of the reversed second half
            if head.val != prev.val:
                return False
            head = head.next
            prev = prev.next

        # If we reach here, the linked list is a palindrome
        return True
