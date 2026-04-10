from typing import Optional, List


class ListNode:
    def __init__(self, val=0, next_node=None):
        self.val = val
        self.next = next_node


class Solution:
    @staticmethod
    def nodesBetweenCriticalPoints(head: Optional[ListNode]) -> List[int]:
        # Initialize pointers to traverse the linked list
        prev = head
        current = head.next
        # List to store the positions of critical points
        critical_points = []
        # Position index, starting at 1 because head is considered position 0
        i = 1

        # Traverse the list to find critical points
        while current and current.next:
            if prev.val > current.val < current.next.val:
                # Local minimum
                critical_points.append(i)
            elif prev.val < current.val > current.next.val:
                # Local maximum
                critical_points.append(i)
            # Move to the next node in the list
            prev = current
            current = current.next
            i += 1

        # If there are fewer than 2 critical points, return [-1, -1]
        if len(critical_points) < 2:
            return [-1, -1]

        # Calculate the minimum and maximum distances between critical points
        min_distance = float('inf')
        for j in range(1, len(critical_points)):
            min_distance = min(min_distance, critical_points[j] - critical_points[j - 1])

        max_distance = critical_points[-1] - critical_points[0]

        return [min_distance, max_distance]


# Example usage:
# Let's create a linked list: 1 -> 3 -> 2 -> 5 -> 4 -> 6 -> 1
head = ListNode(1, ListNode(3, ListNode(2,
                                        ListNode(5, ListNode(4, ListNode(6, ListNode(1)))))))
print(Solution.nodesBetweenCriticalPoints(head))  # Expected output: [1, 6]
