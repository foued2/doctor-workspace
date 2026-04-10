from typing import Optional


class ListNode:
    def __init__(self, val=0, next_node=None):
        self.val = val
        self.next = next_node


class Solution:
    @staticmethod
    def reverseList(head: Optional[ListNode]) -> Optional[ListNode]:
        """
        Recursive solution
        """
        # Base case: if head is None or head.next is None, return head
        if head is None or head.next is None:
            return head

        # Recursively reverse the rest of the list starting from head.next
        new_head = Solution.reverseList(head.next)

        # Reverse the links: make head.next point to head and head.next to None
        head.next.next = head
        head.next = None

        # Return the new head of the reversed list
        return new_head


# Example usage:
# Create a linked list: 1 -> 2 -> 3 -> 4 -> 5
head = ListNode(1)
head.next = ListNode(2)
head.next.next = ListNode(3)
head.next.next.next = ListNode(4)
head.next.next.next.next = ListNode(5)

# Print the original linked list
print("Original Linked List:")
current = head
while current:
    print(current.val, end=" -> ")
    current = current.next
print("None")

# Reverse the linked list
new_head = Solution.reverseList(head)

# Print the reversed linked list
print("\nReversed Linked List:")
current = new_head
while current:
    print(current.val, end=" -> ")
    current = current.next
print("None")
