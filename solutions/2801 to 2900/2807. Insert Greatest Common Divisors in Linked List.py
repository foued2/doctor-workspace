# Definition for singly-linked list.
import math
from typing import Optional


class ListNode:
    def __init__(self, val=0, next_node=None):
        self.val = val
        self.next = next_node


class Solution:
    @staticmethod
    def insertGreatestCommonDivisors(head: Optional[ListNode]) -> Optional[ListNode]:
        current = head
        while current and current.next:
            first = current
            second = current.next
            gcd_value = math.gcd(first.val, second.val)

            # Create a new node with the GCD value
            gcd_node = ListNode(gcd_value)

            # Insert the new node between first and second
            gcd_node.next = second
            first.next = gcd_node

            # Move to the next pair of nodes
            current = second

        return head


# Helper function to print the list
def print_list(head: Optional[ListNode]):
    current = head
    while current:
        print(current.val, end=" -> ")
        current = current.next
    print("None")


# Example usage:
head = ListNode(2, ListNode(3, ListNode(6, ListNode(9))))
solution = Solution()
new_head = solution.insertGreatestCommonDivisors(head)
print_list(new_head)  # Output should show the list with GCD nodes inserted
