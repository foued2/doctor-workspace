from typing import Optional


class ListNode:
    def __init__(self, val=0, next_node=None):
        self.val = val
        self.next = next_node


class Solution:
    @staticmethod
    def deleteDuplicates(head: Optional[ListNode]) -> Optional[ListNode]:
        # Check if the head is None or if there's only one node in the list
        if not head or not head.next:
            return head

        # Initialize a pointer to traverse the list
        current = head

        # Traverse the list until we reach the end
        while current and current.next:
            # If the current node's value is the same as the next node's value
            if current.val == current.next.val:
                # Bypass the next node by updating the pointers
                current.next = current.next.next
            else:
                # Move to the next distinct node
                current = current.next

        return head


# Example usage:
if __name__ == "__main__":
    # Create a linked list: 1 -> 1 -> 2 -> None
    head = ListNode(1)
    head.next = ListNode(1)
    head.next.next = ListNode(2)

    # Call the removeDuplicates method
    solution = Solution()
    new_head = solution.deleteDuplicates(head)

    # Print the values of the new linked list
    while new_head:
        print(new_head.val, end=" -> ")
        new_head = new_head.next
