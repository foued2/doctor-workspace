from typing import Optional


class ListNode:
    def __init__(self, val=0, next_node=None):
        # Initialize a ListNode with a value and a pointer to the next node
        self.val = val
        self.next = next_node


class Solution:
    @staticmethod
    def mergeNodes(head: Optional[ListNode]) -> Optional[ListNode]:
        # Check if the head is None or the next node is None
        if not head or not head.next:
            return None  # Return None for empty or single node linked lists

        # Create a dummy node to simplify the merge process
        dummy = ListNode()

        # Initialize a current pointer to the dummy node
        current = dummy

        # Initialize a sum variable to accumulate values
        sum_val = 0

        # Move head to the first node
        head = head.next

        # Iterate through the linked list
        while head:
            if head.val == 0:
                # When a zero node is encountered, finalize the current segment
                current.next = ListNode(sum_val)

                # Move to the next node in the result-linked list
                current = current.next

                # Reset the sum for the next segment
                sum_val = 0
            else:
                # Accumulate the value if it's not zero
                sum_val += head.val

            # Move to the next node in the input linked list
            head = head.next

        # Return the next of dummy node as the head of the result-linked list
        return dummy.next


# Example usage
def list_to_linked_list(lst):
    # Helper function to convert a list to a linked list
    if not lst:
        return None
    head = ListNode(lst[0])
    current = head
    for value in lst[1:]:
        current.next = ListNode(value)
        current = current.next
    return head


def linked_list_to_list(node):
    # Helper function to convert a linked list to a list
    result = []
    while node:
        result.append(node.val)
        node = node.next
    return result


# Create a linked list from a list
input_list = [0, 3, 1, 0, 4, 5, 2, 0]
linked_list = list_to_linked_list(input_list)

# Merge nodes
solution = Solution()
merged_linked_list = solution.mergeNodes(linked_list)

# Convert the result linked list to a list
result_list = linked_list_to_list(merged_linked_list)
print(result_list)  # Output should be [4, 11]
