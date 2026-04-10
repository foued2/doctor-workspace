from typing import Optional


# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next_node=None):
        self.val = val
        self.next = next_node


class Solution:
    @staticmethod
    def deleteMiddle(head: Optional[ListNode]) -> Optional[ListNode]:
        # Edge case: If the list is empty or has only one node, return None
        if not head or not head.next:
            return None

        # Step 1: Initialize slow and fast pointers to head, and prev to head
        slow = head
        fast = head
        prev = head

        # Step 2: Use the slow and fast pointer technique to find the middle node
        while fast and fast.next:
            prev = slow  # Move prev to current slow node
            slow = slow.next  # Move slow one step forward
            fast = fast.next.next  # Move fast two steps forward

        # Step 3: Remove the middle node by skipping it
        prev.next = slow.next

        # Step 4: Return the modified list
        return head


# Helper function to create a linked list from a list
def create_linked_list(lst):
    if not lst:
        return None
    head = ListNode(lst[0])
    current = head
    for value in lst[1:]:
        current.next = ListNode(value)
        current = current.next
    return head


# Helper function to print the linked list
def print_linked_list(head):
    current = head
    while current:
        print(current.val, end=" -> ")
        current = current.next
    print("None")


# Example usage
head = create_linked_list([1, 2, 3, 4, 5])
print("Original List:")
print_linked_list(head)

solution = Solution()
new_head = solution.deleteMiddle(head)

print("List after deleting the middle node:")
print_linked_list(new_head)
