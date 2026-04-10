# Definition for singly-linked list.
from typing import Optional


class ListNode:
    def __init__(self, val=0, next_node=None):
        self.val = val
        self.next = next_node


class Solution:
    @staticmethod
    def gameResult(head: Optional[ListNode]) -> str:
        # Initialize counters for the odd and even indexed players' points.
        odd_points = 0
        even_points = 0

        # Traverse the linked list two nodes at a time.
        while head and head.next:
            # Retrieve the values of the two adjacent nodes.
            odd_value = head.val
            even_value = head.next.val

            # Increment odd_points if the odd indexed player wins the round.
            odd_points += odd_value < even_value
            # Increment even_points if the even indexed player wins the round.
            even_points += odd_value > even_value

            # Move to the next pair of nodes.
            head = head.next.next

        # Determine the result based on the players' points.
        if odd_points > even_points:
            return "Odd"
        elif odd_points < even_points:
            return "Even"
        else:
            return "Tie"
