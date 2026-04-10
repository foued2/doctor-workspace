from typing import Optional


class ListNode:
    def __init__(self, val=0, next_node=None):
        """
        Definition for singly-linked list node.

        Args:
        - val: Value of the node.
        - next_node: Reference to the next node in the list.
        """
        self.val = val
        self.next = next_node


class Solution:
    @staticmethod
    def removeNthFromEnd(head: Optional[ListNode], n: int) -> Optional[ListNode]:
        """
        Removes the nth node from the end of a singly-linked list.

        Args:
        - head: The head node of the linked list.
        - n: The position of the node to remove from the end.

        Returns:
        - The head node of the modified linked list.
        """
        # Create a dummy node to handle cases where the head needs to be removed
        dummy = ListNode()
        dummy.next = head

        # Initialize the fast and slow pointers to the dummy node
        fast = dummy
        slow = dummy

        # Move the fast pointer ahead by n nodes
        for _ in range(n + 1):
            fast = fast.next

        # Move both pointers together until the fast pointer reaches the end
        while fast is not None:
            fast = fast.next
            slow = slow.next

        # Remove the nth node from the end by adjusting the next pointer of the slow pointer
        slow.next = slow.next.next

        # Return the head of the modified list (dummy.next will be the actual head)
        return dummy.next


# Create the linked list from the input list [1, 2, 3, 4, 5]
head = ListNode(1)
current = head
for num in [2, 3, 4, 5]:
    current.next = ListNode(num)
    current = current.next

# Create a solution object
solution = Solution()

# Call the removeNthFromEnd method and print the modified linked list
modified_head = solution.removeNthFromEnd(head, 2)
while modified_head:
    print(modified_head.val, end=" -> ")
    modified_head = modified_head.next
