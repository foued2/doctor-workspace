# class Solution(object):
#     @staticmethod
#     def merge(nums1, m, nums2, n):
#         i = 0
#         j = 0
#         k = 0
#         expected_nums = [0] * (m + n)
#
#         while k < m + n:
#             if i < m and (j >= n or nums1[i] < nums2[j]):
#                 expected_nums[k] = nums1[i]
#                 i += 1
#             elif j < n and (i >= m or nums1[i] >= nums2[j]):
#                 expected_nums[k] = nums2[j]
#                 j += 1
#             k += 1
#         median = expected_nums[(m + n) // 2]
#         return expected_nums, median
#
#
# # Call the merge() method with two lists [1, 2, 3, 8, 10, 20] and [2, 5, 6], and their lengths 6 and 3 respectively.
# print(Solution.merge([1, 2, 3, 8, 10, 20], 6, [2, 5, 6], 3))
# print((6 + 3) // 2)
#
# from itertools import combinations
#
# numbers = [-1, 0, 1, 2, -1, -4]
# result = list(combinations(numbers, 2))
#
# print(len(result))
#
#
# def quicksort(nums):
#     if len(nums) <= 1:
#         return nums
#     else:
#         pivot = nums[0]
#         lesser = [x for x in nums[1:] if x <= pivot]
#         greater = [x for x in nums[1:] if x > pivot]
#         return quicksort(lesser) + [pivot] + quicksort(greater)
#
#
# original_list = [-1, 0, 1, 2, -1, -4]
#
# sorted_list = quicksort(original_list)
# print(sorted_list)
# s = [1, 0, -1, 0, -2, 2] + [2]
# print(s)
# print([1, 2, 1][2:3])
#
#
# def find_next_bigger(nums):
#     result = [next((num for num in nums[i + 1:] if num > nums[i]), None) for i in range(len(nums))]
#     return result
#
#
# # Example usage:
# my_array = [3, 7, 1, 5, 2, 8, 4]
# result_array = find_next_bigger(my_array)
# print(result_array)
#
#
# def count_d(input):
#     return input.count("D") + input.count("d")
#
#
# print(count_d("Debris was scattered all over the yard."))
#
# matrix = [
#     [1, 2, 3],
#     [4, 5, 6],
#     [7, 8, 9]
# ]
#
# # column_index = 1  # Replace with the desired column index
#
# # Access the entire column
# for index in range(len(matrix)):
#     table = matrix[index]
#     for row in matrix:
#         # table = matrix[index]
#         if row[index] not in table:
#             table += [row[index]]
#         # else:
#         #     pass
#     print(table)
#
#     # print(f"Column {column_index}: {column}")
#
# # Global 4x4 matrix
# global_matrix = [
#     [1, 2, 3, 4],
#     [5, 6, 7, 8],
#     [9, 10, 11, 12],
#     [13, 14, 15, 16]
# ]
#
# # Define the size of the sub-matrix
# sub_matrix_size = 2
#
# # Iterate over sub-matrices
# for i in range(0, len(global_matrix) - sub_matrix_size + 1, sub_matrix_size):
#     for j in range(0, len(global_matrix[0]) - sub_matrix_size + 1, sub_matrix_size):
#         # Extract the sub-matrix
#         sub_matrix = [row[j:j + sub_matrix_size] for row in global_matrix[i:i + sub_matrix_size]]
#
#         # Print the sub-matrix
#         print(f"Sub-matrix starting at ({i}, {j}):")
#         for row in sub_matrix:
#             print(row)
#         print()import math
import math
from functools import reduce
from typing import List


#
# def generate_combinations(elements, current_combination, index):
#     # Print the current combination
#     if len(current_combination) == len(elements):
#         # print(current_combination)
#         return current_combination
#
#     # Explore all possibilities starting from the given index
#     # Choose the current element
#     for i in range(index, len(elements)):
#         current_combination.append(elements[i])
#
#         # Explore further with the chosen element
#         generate_combinations(elements, current_combination, i + 1)
#
#         # Backtrack: Remove the last element to explore other possibilities
#         current_combination.pop()
#
#
# # Example usage:
# elements_to_combine = ["(", ")", "(", ")", "(", ")"]
# generate_combinations(elements_to_combine, [], 0)
#
#
# def generate_combinations_multiple_lists(lists, current_combination, index):
#     if index == len(lists):
#         print(current_combination)
#         return
#
#     for element in lists[index]:
#         current_combination.append(element)
#         generate_combinations_multiple_lists(lists, current_combination, index + 1)
#         current_combination.pop()
#
#
# # Example usage:
# list1 = [1, 2]
# list2 = ['a', 'b']
# list3 = ['x', 'y', 'z']


# generate_combinations_multiple_lists([list1, list2, list3], [], 0)


# def fibonacci(n):
#     # Base cases
#     if n == 0:
#         return 0
#     if n == 1:
#         return 1
#
#     # Initialize a table to store intermediate results
#     dp = [0] * (n + 1)
#
#     # Base values
#     dp[0] = 0
#     dp[1] = 1
#
#     # Fill the table using dynamic programming
#     for i in range(2, n + 1):
#         dp[i] = dp[i - 1] + dp[i - 2]
#
#     # Return the nth Fibonacci number
#     return dp[n]


# Example usage:
# result = fibonacci(5)
# print(result)

# s = 'abcad'
# for i in range(len(s)):
#     mid = len(s[0:i + 1]) // 2
#     print(mid, s[0:i + 1], s[mid])

# a = [1, 2, 3]
# a.insert(2, 5)
# print(a)
#
#
# def backtrack(start, path, elements, k):
#     # Base case
#     if k == 0:
#         # Process or append the combination
#         result.append(path[:])
#         return
#
#     # Explore choices
#     for i in range(start, len(elements)):
#         # Make choice
#         path.append(elements[i])
#         # elements[-i], elements[i] = elements[i], elements[-i]
#
#         # Recur with reduced problem size
#         backtrack(i, path, elements, k - 1)
#
#         # Undo choice
#         path.pop()
#
#
# # Example usage
# result = []
# backtrack(0, [], [1, 2, 3], 3)
# print(result)


#
# print(7 // 2)
# print(2 ** 31)
# print(round(1 / 2))
#
#
# def greedy_coin_change(coins, target_amount):
#     coins.sort(reverse=True)  # Sort coins in descending order
#
#     num_coins = 0
#     change = []
#
#     for coin in coins:
#         while target_amount >= coin:
#             target_amount -= coin
#             num_coins += 1
#             change.append(coin)
#
#     return num_coins, change
#
#
# # Example usage:
# coin_denominations = [25, 10, 5, 1]
# amount_to_make_change = 63
#
# result, change = greedy_coin_change(coin_denominations, amount_to_make_change)
#
# print(f"Minimum number of coins: {result}")
# print(f"Change: {change}")


# def generate_subsets(nums, path, result, index):
#     # Add the current subset to the result
#     result.append(path[:])
#
#     # Explore decisions to include/exclude elements
#     for i in range(index, len(nums)):
#         # Include the current element
#         path.append(nums[i])
#         generate_subsets(nums, path, result, i + 1)
#
#         # Exclude the current element (backtrack)
#         path.pop()
#
#
# # Example usage:
# nums = [1, 2, 3]
# result = []
# generate_subsets(nums, [], result, 0)
# print(result)


# class Solution:
#     @staticmethod
#     def permute(i, path, nums, k):
#         # Base case
#         if k == 0:
#             result.append(path[:])
#             return
#
#         for j in range(i, len(nums)):
#             # Make choice
#             path.append(nums[j])
#
#             # Recur with reduced problem size
#             Solution.permute(0, path, nums[:j] + nums[j + 1:], k - 1)
#
#             # Undo choice
#             path.pop()
#
#
# # Example usage
# solution = Solution()
# result = []
# solution.permute(0, [], [1, 2, 3], len([1, 2, 3]))
# print(result)

# class Solution:
#     def containsDuplicate(self, nums: List[int]) -> bool:
#         visited = {}
#         for num in nums:
#             if num in visited:
#                 return True
#             else:
#                 visited[num] = 1
#         return False

# def prefix_sum(nums):
#     n = len(nums)
#     prefix = [0] * n  # Initialize prefix sum array
#
#     # Compute prefix sum
#     prefix[0] = nums[0]  # The first element remains the same
#     for i in range(1, n):
#         prefix[i] = prefix[i - 1] + nums[i]
#
#     return prefix
#
#
# # Example usage:
# nums = [1, 2, 3, 4, 5]
# prefix = prefix_sum(nums)
# print(prefix)  # Output: [1, 3, 6, 10, 15]

# def farey_sequence(n: int, descending: bool = False) -> None:
#     """Print the nth Farey sequence.
#     Allow for either ascending or descending."""
#     a, b, c, d = 0, 1, 1, n
#     if descending:
#         a, c = 1, n - 1
#     # print(f"{a}/{b}")
#     counter = 1
#     while c <= n and not descending or a > 0 and descending:
#         k = (n + b) // d
#         a, b, c, d = c, d, k * c - a, k * d - b
#         counter += 1
#         # print(f"{a}/{b}")
#     print(n, counter)
#
#
# for i in range(1, 16):
#     farey_sequence(i, descending=True)
# nums1 = [1, 2, 4, 5, 6, 8]
# nums2 = [2, 6, 7]
# i, j = 0, 0
# nums3 = []
# while i < len(nums1) and j < len(nums2):
#     if nums1[i] <= nums2[j]:
#         nums3.append(nums1[i])
#         i += 1
#     else:
#         nums3.append(nums2[j])
#         j += 1
# print(nums3)

# class Node:
#     def __init__(self, data):
#         self.data = data
#         self.next = None
#
#
# node1 = Node(0)
# node1.data = 10
# node1.next = node1
# node2 = Node([0])
# node3 = Node(3)
# print(node1.data, node2.data, node3.next)
#
#
# class LinkedList:
#     def __init__(self):
#         self.head = None
#
#
# list1 = LinkedList()
# list1.head = Node(2)
# list1.head.next = Node(3)
# list1.head.next.next = Node(4)
# print(list1.head.data, list1.head.next.data, list1.head.next.next.data)
# print(list1.head, list1.head.next, list1.head.next.next, list1.head.next.next.next)
# A complete working Python program to find the length of a
# Linked List iteratively

# Node class


# class Node:
#     # Function to initialize the node object
#     def __init__(self, data):
#         self.data = data  # Assign data
#         self.next = None  # Initialize next as null
#
#
# # Linked List class contains a Node object
# class LinkedList:
#
#     # Function to initialize head
#     def __init__(self):
#         self.head = None
#
#     # This function is in LinkedList class.
#     # It inserts a new node at the beginning of Linked List.
#
#     def push(self, new_data):
#         # 1 & 2: Allocate the Node &
#         # Put in the data
#         new_node = Node(new_data)
#
#         # 3. Make next of new Node as head
#         new_node.next = self.head
#
#         # 4. Move the head to point to new Node
#         self.head = new_node
#
#     # This function counts the number of nodes in Linked List
#     # iteratively, given 'node' as starting node.
#
#     def getCount(self):
#         temp = self.head  # Initialize temp
#         count = 0  # Initialize count
#
#         # Loop while the end of a linked list is not reached
#         while temp:
#             count += 1
#             temp = temp.next
#         return count
#
#
# # Driver code
# if __name__ == '__main__':
#     llist = LinkedList()
#     llist.push(1)
#     llist.push(3)
#     llist.push(1)
#     llist.push(2)
#     llist.push(1)
#
#     # Function call
#     print("Count of nodes is :", llist.getCount())


# # Define the printLinkedList function
# def printLinkedList(head):
#     # Check if the linked list is empty
#     if head is None:
#         print("Linked list is empty")
#         return
#
#     # Traverse the linked list starting from the head node
#     current = head
#     while current:
#         # Print the data of the current node
#         print(current.data)
#
#         # Move to the next node
#         current = current.next
#
#     # Print a new line at the end
#     print()
#
#
# class SinglyLinkedListNode:
#     def __init__(self, data):
#         self.data = data
#         self.next = None
#
#
# def insertNodeAtTail(head, data):
#     # Create a new node with the given data
#     new_node = SinglyLinkedListNode(data)
#
#     # Check if the linked list is empty
#     if head is None:
#         # If the linked list is empty, the new node becomes the head
#         head = new_node
#     else:
#         # Traverse the linked list to find the last node
#         current = head
#         while current.next:
#             current = current.next
#
#         # Assign the new node to the next of the last node
#         current.next = new_node
#
#     # Return the head of the modified linked list
#     return head
# n = 10
# j = 2
# while j <= n:
#     ring = [j for j in range(j, 2 * j)]
#     j = ring[-1] + 1
#     print(ring)
#     # print(i, bin(i)[2:], bin(i).count('1'))
#
#
# # Hint 1
# # You should make use of what you have produced already.
# # Hint 2
# # Divide the numbers in ranges like [2-3], [4-7], [8-15] and so on.
# # And try to generate new range from previous.
# # Hint 3
# # Or does the odd/even status of the number help you in calculating the number of 1s?
#
# def array_diff(a, b):
#     # Find elements in a that are not in b
#     diff_a = [x for x in a if x not in b]
#     # Find elements in b that are not in a
#     diff_b = [x for x in b if x not in a]
#     # Concatenate the results
#     result = diff_a + diff_b
#     return result
#
#
# # Test cases
# print(array_diff([1, 2], [1]))  # Output: [2]
# print(array_diff([1, 2, 2, 2, 3], [2]))  # Output: [1, 3]
#
# print(array_diff([1, 2, 2, 2, 5], [1, 2, 3, 4, 6]))
#
#
# def number(bus_stops):
#     # Good Luck!
#     res = [0] * len(bus_stops)
#     res[0] = bus_stops[0][0]
#     for i in range(1, len(bus_stops)):
#         res[i] = res[i - 1] + (bus_stops[i][0] - bus_stops[i][1])
#     return res
#
#
# print(number([[3, 0], [9, 1], [4, 8], [12, 2], [6, 1], [7, 8]]))
#
#
# def validBraces(s):
#     while '{}' in s or '()' in s or '[]' in s:
#         s = s.replace('{}', '')
#         s = s.replace('[]', '')
#         s = s.replace('()', '')
#     return s == ''
#
#
# print(validBraces("(({{[[]]}}))"))

# Reverse linked list in place
# while head is not None:
#     head.next, head = head, head.next
#     return head

# Example for Prefix Sum in Python

# def prefix_sum_array(nums):
#     prefix_sum = [0]
#     for num in nums:
#         prefix_sum.append(prefix_sum[-1] + num)
#     return prefix_sum
#
#
# arr = [1, -20, -3, 30, 5, 4]
# print(prefix_sum_array(arr))
#
# # Initialize variables
# Q = int(input())  # Read the number of queries
# heap = []  # Initialize an empty list to represent the min heap
# min_element = float('inf')  # Initialize the minimum element to positive infinity
#
# # Process queries
# for _ in range(Q):
#     query = list(map(int, input().split()))
#     if query[0] == 1:
#         # If the inserted element is smaller than the current minimum, update min_element
#         if query[1] < min_element:
#             min_element = query[1]
#         heap.append(query[1])
#     elif query[0] == 2:
#         element_to_remove = query[1]
#         if element_to_remove == min_element:
#             # If the element to remove is the current minimum, update min_element
#             heap.remove(element_to_remove)
#             if heap:
#                 min_element = min(heap)
#             else:
#                 min_element = float('inf')
#         else:
#             # If the element to remove is not the minimum, just remove it from the heap
#             heap.remove(element_to_remove)
#     else:
#         if heap:
#             print(min_element)
#         else:
#             print("Priority queue is empty")
# Given an array or list
# arr = [1, 2, 3, 4]
#
# # Suppose we want to access an index that may be out of bounds
# index = -2
#
# # To ensure the index is within bounds, we can use modulo
# correct_index = index % len(arr)
#
# # Now, correct_index will always be a valid index within the range of the array
# print("Correct Index:", correct_index)
# print("Value at Correct Index:", arr[correct_index])
#
# # List of integers
# nums = [5, 2, 7, 7, 8]
#
# # Create a dictionary with integers as keys and empty lists as values
# ordered_map = {}
# for index, num in enumerate(nums):
#     ordered_map[num] = ordered_map.get(num, 0) + 1
# print(ordered_map)
#
# print("a" == "A")
#
# c = "ac"
#
# print("ac" * 0)
#
# s = [1, 2, 3]
# print(s, s.pop())
#
# path = 'abs'
# path = path.replace('s', '')
# print(path)
#
# i = '/'
# print(i.isalnum())
#
#
# def calculate_xor(numbers):
#     result = 0
#     for num in numbers:
#         result ^= num
#         print(result)
#     return result
#
#
# # Example usage:
# numbers = [1, 1, 1, 0]
# print("XOR of numbers:", calculate_xor(numbers))
#
# print(bin(3 | 1 | 1 | 32 | 2 | 12))
# lst = [3, 1, 1, 32, 2, 12]
# for i in lst:
#     print(bin(i)[2:])
#
#
# def find_lexicographically_smallest(strings):
#     """
#     This function finds the lexicographically smallest string among a list of strings.
#
#     Args:
#     - strings: A list of strings to compare.
#
#     Returns:
#     - The lexicographically smallest string.
#     """
#
#     # Using the min() function with a custom key to find the lexicographically smallest string
#     smallest_string = min(strings)
#
#     # Return the lexicographically smallest string
#     return smallest_string
#
#
# # Example usage:
# strings = ["banana", "apple", "orange", "grape"]
# result = find_lexicographically_smallest(strings)
# print("Lexicographically smallest string:", result)
#
# a = 'uhgiugi'
# a = a.replace('u', 'k')
# print(a)
#
# list1 = ['a', 'b', 'c']
# list2 = [1, 2, 3]
#
# # Create a dictionary mapping elements from list1 to elements from list2
# hash_map = {key: value for key, value in zip(list1, list2)}
#
# print(hash_map)
#
# s = 'kljlkj'
# s = list(s)
# s.insert(len(s) - 1, s.pop(0))
# print(s)
#
#
# # # Open a file named 'user.out' in write mode
# # f = open('user.out', 'w')
# #
# # # Iterate over each line of input, assuming the input is JSON formatted
# # for i in map(loads, stdin):
# #     # Call the function rowAndMaximumOnes on each input matrix and write the result to the file
# #     f.write(f'[{",".join(map(str, rowAndMaximumOnes(i)))}]\n')
# #
# # # Flush the buffer and exit
# # f.flush()
# # exit(0)
# class TreeNode:
#     def __init__(self, value):
#         self.info = value
#         self.left = None
#         self.right = None
#
#
# def preOrder(root):
#     """
#     Perform pre-order traversal of a binary tree.
#
#     Args:
#     - root: The root node of the binary tree
#
#     Returns:
#     - res: List containing the pre-order traversal of the tree
#
#     """
#     # Initialize an empty list to store the result
#     res = []
#
#     # Base case: If the root is None, return an empty list
#     if root is None:
#         return res
#
#     # Add the current node's value to the result list
#     res.append(root.info)
#
#     # Recursively traverse the left subtree
#     left_result = preOrder(root.left)
#
#     # Recursively traverse the right subtree
#     right_result = preOrder(root.right)
#
#     # Concatenate the results of left and right subtrees with the current node's value
#     res.extend(left_result)
#     res.extend(right_result)
#
#     return res
#
#
# # Create nodes
# root = TreeNode(1)
# root.left = TreeNode(2)
# root.right = TreeNode(3)
# root.left.left = TreeNode(4)
# root.left.right = TreeNode(5)
#
# # Perform pre-order traversal
# result = preOrder(root)
# print("Pre-order traversal result:", *result)
#
#
# def move_to_start(lst, i):
#     if 0 <= i < len(lst):
#         # Remove the element at index i and insert it at the beginning of the list
#         lst.insert(0, lst.pop(i))
#
#
# # Example usage:
# my_list = [4, 2, 7, 1, 9, 5]
# index_to_move = 2
# move_to_start(my_list, index_to_move)
# print(my_list)  # Output: [7, 4, 2, 1, 9, 5]
#
# print(0 ^ 2)
# lst = [4, 2]
# print(reduce(math.gcd, lst))
#
# print(math.floor(5/ 3))
#
# print(ord('a'))
#
# arr2 = [2, 1, 4, 3, 9, 6]
# table = {}
# for num in arr2:
#     table[num] = table.get(num, 0) + 1
# print({element: index for index, element in enumerate(arr2)})
# print(round(7 // 2))
#
# # Two lists to zip
# list1 = [2, 1, 3]
# list2 = ['a', 'b', 'c']
#
# # Using zip() to combine the lists
# zipped = zip(list1, list2)
#
# # Iterating over the zipped object
# for item in sorted(zipped):
#     print(item)
#
#
# def find_lsb_msb(n: int):
#     if n == 0:
#         return 0, 0
#
#     # Finding the LSB (The Least Significant Bit)
#     lsb = n & 1
#
#     # Finding the MSB (Most Significant Bit)
#     msb = 0
#     temp = n
#     while temp > 1:
#         temp >>= 1
#         msb += 1
#
#     # Convert MSB position to its value (2^msb)
#     msb_value = 1 << msb
#
#     return lsb, msb_value
#
#
# # Test the function
# n = 18  # Binary: 10010
# lsb, msb = find_lsb_msb(n)
# print("Number:", n)
# print("LSB:", lsb)
# print("MSB:", msb)  # Output should be 16, since 18 in binary is 10010 and the MSB value is 2^4 =. 16
#
# # Another example
# n = 19  # Binary: 10011
# lsb, msb = find_lsb_msb(n)
# print("Number:", n)
# print("LSB:", lsb)
# print("MSB:", msb)  # Output should be 16, since 19 in binary is 10011 and the MSB value is 2^4 =. 16
#
# # Example: Set operations in Python
# set1 = {1, 2, 3, 4, 5}
# set2 = {4, 5, 6, 7, 8}
#
# # Elements in set1 but not in set2
# difference = set1 - set2
# print(f"set1 - set2: {difference}")  # Output: {1, 2, 3}
#
# # Elements in set2 but not in set1
# difference = set2 - set1
# print(f"set2 - set1: {difference}")  # Output: {8, 6, 7}
#
# # Elements in either set1 or set2 but not in both (symmetric differences)
# symmetric_difference = set1 ^ set2
# print(f"set1 ^ set2: {symmetric_difference}")  # Output: {1, 2, 3, 6, 7, 8}
#
# # Elements in both set1 and set2 (intersection)
# intersection = set1 & set2
# print(f"set1 & set2: {intersection}")  # Output: {4, 5}
#
# # Elements in either set1 or set2 (union)
# union = set1 | set2
# print(f"set1 | set2: {union}")  # Output: {1, 2, 3, 4, 5, 6, 7, 8}
#
# # Initialize the input list
# lst = [-3, 2, -3, 4, 2]
#
# # Initialize the minimum prefix sum with a large positive number
# min_prefix_sum = float('inf')
#
# # Initialize the current prefix sum to zero
# current_prefix_sum = 0
#
# # Iterate through each element in the list
# for num in lst:
#     # Add the current number to the current prefix sum
#     current_prefix_sum += num
#     # Update the minimum prefix sum if the current prefix sum is smaller
#     if current_prefix_sum < min_prefix_sum:
#         min_prefix_sum = current_prefix_sum
#
# # Print the result
# print(min_prefix_sum)
#
#
# def count_ones(n):
#     count = 0
#     while n:
#         count += n & 1
#         n >>= 1
#     return count
#
# # Example usage:
# num = 0  # Example integer
# ones_count = count_ones(num)
# print("Number of 1's in the binary representation of", num, "is:", ones_count)
#

def compute_failure(pattern):
    # Get the length of the pattern
    m = len(pattern)

    # Initialize the failure array with zeros, where each index corresponds to a position in the pattern
    failure = [0] * m

    # Initialize variables to track positions in the pattern
    i, j = 1, 0

    # Iterative Calculation
    while i < m:
        # Compare characters at positions i and j
        if pattern[i] == pattern[j]:
            # If they match, increment both i and j, and set the failure value at position i to j + 1
            failure[i] = j + 1
            i += 1
            j += 1
        elif j > 0:
            # If they don't match and j is not at the beginning, update j using the failure value of the previous
            # position
            j = failure[j - 1]
        else:
            # If they don't match and j is at the beginning, set the failure value at position i to 0 and increment i
            failure[i] = 0
            i += 1

    # Return the computed failure array
    return failure


# Example usage
pattern = "ABCDABD"
failure = compute_failure(pattern)
print("Failure function values:", failure)


def binary_search(row: List[int]) -> int:
    # Initialize the left and right pointers for the binary search
    left, right = 0, len(row) - 1

    # Variable to store the index of the last 1 found
    last_one_index = -1

    # Continue searching while the left pointer does not cross the right pointer
    while left <= right:
        # Calculate the middle index in the current search range
        mid = (right + left) // 2

        # If the middle element is 1
        if row[mid] == 1:
            # Update the last-found index of 1
            last_one_index = mid
            # Move the search range to the right half
            left = mid + 1
        else:
            # Move the search range to the left half
            right = mid - 1

    # Return the index of the last 1 found
    return last_one_index


# Test the function with a list containing only 1's
print(binary_search([1, 1, 1, 1, 1]))  # Output should be 4

print('-'.isalpha())


def Xoring(x: int, n: int) -> int:
    bin_x = str((bin(x)[2:]))[::-1]
    i = 0
    while x < (2 ** n):
        x = (2 ** i) + x
        bin_x = '1' + bin_x
        print(bin_x)
        x = int(bin_x)
        print(x)
        i += 1
    return x


print(Xoring(7, 4))


def get_lsb(n: int) -> int:
    # Perform bitwise AND with 1 to extract the LSB
    return n & 1


# Example usage
number = 10  # Binary representation: 1010
lsb = get_lsb(number)

print(f"The LSB of {number} is: {lsb}")  # Output: The LSB of 10 is: 0

number = 11  # Binary representation: 1011
lsb = get_lsb(number)

print(f"The LSB of {number} is: {lsb}")  # Output: The LSB of 11 is: 1

s = '$easy$'
r = '$'
print(s.strip(r))

b = 1
b ^= 1
print(b)

num = 13
k, num = divmod(num, 3)
print(k, num)

nums = [4, 4, 2, 4, 3]
nums = set(nums)
print(nums)

a = 'capiTalIze'
print(a.swapcase())

mainTank = 58
a, b = divmod(mainTank, 5)
print(a, b)

t = 'leetcode'
print(t.find('e'))

print(bin(8)[2:], bin(12)[2:], bin(12 ^ 8)[2:])
s = "ABFCACDB"
s = s.replace('AB', '')
s = s.replace('CD', '')

print(s)

k = -10
print(len(str(k)))

print(6 ^ 5)

a = set(list("abba"))
b = set(list("baba"))
s = a.difference(b)
if not s:
    print(True)

d = [1]
if not d:
    print(True)

n = [91, 92, 60, 65, 87, 100]
print(sum(n) / len(n))


from datetime import datetime

# Define the start date and the target date
start_date = datetime(2023, 7, 16)
target_date = datetime(2024, 7, 1)

# Calculate the number of days between the two dates
days_difference = (target_date - start_date).days

# Convert the number of days to weeks
weeks_difference = days_difference // 7

# Find the week number in the cycle of 3 weeks (1, 2, 3)
week_number = (weeks_difference % 3) + 1

print("The week number for 1/7/2024 is:", week_number)



