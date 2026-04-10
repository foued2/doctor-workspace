from typing import Optional


class ListNode:
    def __init__(self, val=0, next_node=None):
        self.val = val
        self.next = next_node


class Solution:
    @staticmethod
    def pairSum(head: Optional[ListNode]) -> int:
        # Edge case: If the list is empty or has only one node, return 0 as there are no pairs
        if not head or not head.next:
            return 0

        # Step 1: Find the middle of the linked list using slow and fast pointers
        slow = head
        fast = head

        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next

        # Now 'slow' is at the middle node

        # Step 2: Reverse the second half of the linked list
        prev = None
        current = slow

        while current:
            temp = current.next
            current.next = prev
            prev = current
            current = temp

        # 'prev' now points to the head of the reversed second half

        # Step 3: Calculate the maximum twin sum
        max_sum = 0
        first_half = head
        second_half = prev

        while second_half:
            curr_sum = first_half.val + second_half.val
            max_sum = max(curr_sum, max_sum)
            first_half = first_half.next
            second_half = second_half.next

        return max_sum


head = ListNode(4, ListNode(2, ListNode(2, ListNode(3))))
print(Solution.pairSum(head))
