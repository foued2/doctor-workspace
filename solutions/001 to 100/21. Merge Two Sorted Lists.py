from typing import Optional


class ListNode:
    def __init__(self, val=0, next_node=None):
        self.val = val
        self.next = next_node


class Solution:
    @staticmethod
    def mergeTwoLists(list1: Optional[ListNode], list2: Optional[ListNode]) -> Optional[ListNode]:
        # Create a dummy node to serve as the head of the merged list
        dummy = ListNode()
        # Pointer to the current node in the merged list
        temp = dummy

        # Traverse both lists until either one becomes None
        while list1 and list2:
            # Compare the values of the current nodes in list1 and list2
            if list1.val < list2.val:
                # Link the smaller node to the merged list and move list1 pointer forward
                temp.next = list1
                list1 = list1.next
            else:
                # Link the smaller node to the merged list and move list2 pointer forward
                temp.next = list2
                list2 = list2.next
            # Move the temp pointer forward in the merged list
            temp = temp.next

        # Append any remaining nodes from list1 or list2 to the merged list
        if list1:
            temp.next = list1
        elif list2:
            temp.next = list2

        # Return the head of the merged list (dummy.next points to the actual head)
        return dummy.next
