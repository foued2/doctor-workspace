from typing import Optional


class ListNode:
    def __init__(self, val=0, next_node=None):
        self.val = val
        self.next = next_node


class Solution:
    @staticmethod
    def getIntersectionNode(headA: ListNode, headB: ListNode) -> Optional[ListNode]:
        # Check if either of the linked lists is empty
        if not headA or not headB:
            return None

        # Initialize pointers for traversing both linked lists
        pointer_A = headA
        pointer_B = headB

        # Traverse both linked lists until they either intersect or reach the end
        while pointer_A is not pointer_B:
            # If a pointer reaches the end of list A, set it to the head of list B
            pointer_A = pointer_A.next if pointer_A else headB
            # If pointer B reaches the end of list B, set it to the head of list A
            pointer_B = pointer_B.next if pointer_B else headA

        # At this point, either both pointers are pointing to the intersection node or both have reached the end
        # Return the intersection node if found, otherwise return None
        return pointer_A


# Example usage:
if __name__ == "__main__":
    # Example linked lists
    headA = ListNode(2)
    headA.next = ListNode(6)
    headA.next.next = ListNode(4)

    headB = ListNode(1)
    headB.next = ListNode(5)

    # Intersection node
    intersection_node = ListNode(3)
    headA.next.next.next = intersection_node
    headB.next.next = intersection_node

    # Test the function
    intersection = Solution.getIntersectionNode(headA, headB)
    if intersection:
        print("Intersection node value:", intersection.val)  # Output: 3
    else:
        print("No intersection found")

# Example usage:
if __name__ == "__main__":
    # Example linked lists
    # 1 -> 2 -> 3 -> 6 -> 7
    headA = ListNode(1)
    headA.next = ListNode(2)
    headA.next.next = ListNode(3)
    intersection_node = ListNode(6)
    headA.next.next.next = intersection_node
    headA.next.next.next.next = ListNode(7)

    # 4 -> 5 -> 6 -> 7
    headB = ListNode(4)
    headB.next = ListNode(5)
    headB.next.next = intersection_node  # Intersection point
    intersection_node.next = ListNode(7)

    # Test the function
    intersection = Solution.getIntersectionNode(headA, headB)
    if intersection:
        print("Intersection node value:", intersection.val)  # Output: 6
    else:
        print("No intersection found")
