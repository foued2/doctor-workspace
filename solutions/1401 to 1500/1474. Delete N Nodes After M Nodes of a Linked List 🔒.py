from typing import Optional

from main import ListNode


class Solution:
    @staticmethod
    def deleteNodes(head: ListNode, m: int, n: int) -> Optional[ListNode]:
        if head is None or m is None or n is None:
            return head

        # Step 1: Create dummy node
        dummy = ListNode()  # Create a dummy node with a placeholder value
        dummy.next = head  # Set the next pointer of the dummy node to the head of the original list

        # Step 2: Traverse the list and delete nodes after every m nodes
        curr = dummy
        while curr:
            # Skip m nodes
            for _ in range(m):
                if curr:
                    curr = curr.next
                else:
                    break  # Break if we reach the end of the list

            # Delete n nodes
            for _ in range(n):
                if curr and curr.next:
                    curr.next = curr.next.next
                else:
                    break  # Break if we reach the end of the list

        # Step 3: Return the modified list
        return dummy.next


if __name__ == "__main__":
    # Test case 1: Deleting 1 node after every 1 node, resulting in an empty list
    # Input: 1 -> 2 -> 3 -> 4 -> 5, m = 1, n = 1
    head1 = ListNode(1)
    head1.next = ListNode(2)
    head1.next.next = ListNode(3)
    head1.next.next.next = ListNode(4)
    head1.next.next.next.next = ListNode(5)
    result1 = Solution.deleteNodes(head1, 1, 1)
    print("Test case 1:", end=" ")
    while result1:
        print(result1.val, end=" ")
        result1 = result1.next
    print()

    # Test case 2: Deleting 1 node after every 2 nodes, resulting in a modified list
    # Input: 1 -> 2 -> 3 -> 4 -> 5, m = 2, n = 1
    head2 = ListNode(1)
    head2.next = ListNode(2)
    head2.next.next = ListNode(3)
    head2.next.next.next = ListNode(4)
    head2.next.next.next.next = ListNode(5)
    result2 = Solution.deleteNodes(head2, 2, 1)
    print("Test case 2:", end=" ")
    while result2:
        print(result2.val, end=" ")
        result2 = result2.next
    print()

    # Test case 3: Deleting 2 nodes after every 2 nodes, resulting in a modified list
    # Input: 1 -> 2 -> 3 -> 4 -> 5 -> 6, m = 2, n = 2
    head3 = ListNode(1)
    head3.next = ListNode(2)
    head3.next.next = ListNode(3)
    head3.next.next.next = ListNode(4)
    head3.next.next.next.next = ListNode(5)
    head3.next.next.next.next.next = ListNode(6)
    result3 = Solution.deleteNodes(head3, 2, 2)
    print("Test case 3:", end=" ")
    while result3:
        print(result3.val, end=" ")
        result3 = result3.next
    print()
