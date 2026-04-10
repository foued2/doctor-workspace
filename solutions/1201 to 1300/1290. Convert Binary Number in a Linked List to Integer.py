class ListNode:
    def __init__(self, val=0, next_node=None):
        self.val = val
        self.next = next_node


class Solution:
    @staticmethod
    def getDecimalValue(head: ListNode) -> int:
        if head is None:
            return 0

        # Initialize the decimal value to 0
        decimal_value = 0

        # Traverse the linked list
        while head is not None:
            # Left shift the current decimal value by 1 position to make room for the next bit
            decimal_value <<= 1
            # Perform a bitwise OR with the current node's value to set the least significant bit
            decimal_value |= head.val
            # Move to the next node
            head = head.next

        return decimal_value


if __name__ == '__main__':
    # Create a linked list: 1 -> 0 -> 1
    head = ListNode(1)
    head.next = ListNode()
    head.next.next = ListNode(1)

    # Call the getDecimalValue function and print the result
    print(Solution.getDecimalValue(head))


class Solution:
    @staticmethod
    def getDecimalValue(head: ListNode) -> int:
        # If the head is None, the linked list is empty, return 0
        if not head:
            return 0

        # Initialize the result with the value of the head node
        result = head.val

        # Iterate through the linked list starting from the head node
        while head.next:
            # Multiply the current result by 2 and add the value of the next node
            result = (result * 2) + head.next.val
            # Move to the next node
            head = head.next

        # Return the final result, which represents the decimal value of the binary linked list
        return result
