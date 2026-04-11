# Define a ListNode class that represents elements of a linked list.
class ListNode:
    """"
    It's not always named "ListNode," and you can
    choose any name you prefer. In this code, "ListNode" is used as a common convention for naming such a class,
    but you could name it something else if you find it more meaningful or appropriate for your specific use case.

    The essential parts of the ListNode class are:

    val: This attribute stores the value of the node, which is typically an integer, but can be adapted for other data
    types as needed.

    next: This attribute is a reference to the next node in the linked list. It's used to construct the linked list
    by connecting nodes.

    In a linked list, each node typically has a next attribute that references the next node in
    the list. When you create a new ListNode without explicitly specifying a next node, it means that by default,
    the next attribute of that node will be set to None.

    For example, if you create a ListNode like this:

    Node1 = ListNode(2)

    In this case, node1 represents a node with a value of 2. However, since you didn't
    specify a next node, its next attribute will be None, indicating that it's the last node in the list (or the only
    node in the case of a single-node list).
    """

    def __init__(self, val=0, next_node=None):
        self.val = val  # Initialize the value of the node.
        self.next = next_node  # Initialize the reference to the next node.


# Create a class named Solution to encapsulate the solution functions.
class Solution:
    # Define a method within the Solution class to add two linked lists representing numbers.
    @staticmethod
    def addTwoNumbers(l1, l2):
        l1_linked = list_to_linked_list(l1)
        l2_linked = list_to_linked_list(l2)
        # Create a dummy head node to simplify the code.
        dummy_head = ListNode()
        current = dummy_head  # Initialize a current pointer to traverse the result list.
        carry = 0  # Initialize a carry variable to keep track of any carry during addition.

        # Traverse both linked lists while they have nodes.
        while l1_linked or l2_linked:
            val1 = l1_linked.val if l1_linked else 0  # Get the value of the current node in the first list, or 0 if
            # it's None.
            val2 = l2_linked.val if l2_linked else 0  # Get the value of the current node in the second list,
            # or 0 if it's None.

            # Calculate the sum of values along with the carry from the previous step.
            total_sum = val1 + val2 + carry
            carry = total_sum // 10  # Calculate the carry for the next iteration.

            # Create a new node with the value of the sum (modulo 10) and append it to the result list.
            current.next = ListNode(total_sum % 10)
            current = current.next  # Move the current pointer to the newly created node.

            # Move to the next nodes in both input linked lists, if available.
            if l1_linked:
                l1_linked = l1_linked.next
            if l2_linked:
                l2_linked = l2_linked.next

        # If there's still a carry after the loop, create an additional node with its value.
        if carry > 0:
            current.next = ListNode(carry)

        # Create an empty list to store the elements of the result.
        result_list = []

        # Set the 'current' pointer to the first node after the dummy head in the linked list.
        current = dummy_head.next

        # Start a loop to traverse the linked list nodes.
        while current:
            # Append the value of the current node to the 'result_list'.
            result_list.append(current.val)

            # Move the 'current' pointer to the next node in the linked list.
            current = current.next

        # End of the loop. When the loop exits, it means we have processed all nodes in the linked list.

        # Return the 'result_list', which now contains the values of the linked list as a regular list.
        return result_list


def list_to_linked_list(lst):
    # Create a dummy head node
    dummy_head = ListNode()
    current = dummy_head

    # Iterate through the list and create linked list nodes
    for val in lst:
        current.next = ListNode(val)
        current = current.next

    return dummy_head.next  # Skip the dummy head and return the actual head node

#
# # Example linked lists (you can customize these).
# list1 = [9, 9, 9, 9, 9, 9, 9]
# list2 = [9, 9, 9, 9]
#
# solution = Solution()  # Create an instance of the Solution class.
# result = solution.addTwoNumbers(list1, list2)  # Use the addTwoNumbers method to add the linked lists.
#
# # Printing the result.
# print(result)
#
#
# class Node:
#     def __init__(self, data=None):
#         self.data = data
#         self.next = None
#
#
# # class SinglyLinkedList:
# #     def __init__(self):
# #         self.head = None
# #
# #     def append(self, data):
# #         new_node = Node(data)
# #         if not self.head:
# #             self.head = new_node
# #         else:
# #             current = self.head
# #             while current.next:
# #                 current = current.next
# #             current.next = new_node
# #
# #
# # words = SinglyLinkedList()
# # words.append('egg')
# # words.append('ham')
# # words.append('spam')
# #
# # current = words.head
# # while current:
# #     print(current.data, '->', end=' ')
# #     current = current.next
# # print("None")
#
#
# class SinglyLinkedList:
#     def __init__(self):
#         self.head = None
#         self.tail = None
#
#     def append(self, data):
#         node = Node(data)
#
#         if self.head:
#             self.head.next = node
#             self.head = node
#         else:
#             self.tail = node
#             self.head = node
#
#     def size(self):
#         count = 0
#
#         current = self.tail
#         while current:
#             count += 1
#             current = current.next
#         return count
#
#
# words = SinglyLinkedList()
# words.append('egg')
# words.append('ham')
# words.append('spam')
#
# current = words.head
# while current:
#     print(current.data, '->', end=' ')
#     current = current.next
# print("None")
# print(words.size())
