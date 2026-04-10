from typing import List


class Solution:
    @staticmethod
    def nextGreaterElement(nums1: List[int], nums2: List[int]) -> List[int]:
        """
        Stack
        """
        # Create a dictionary to store the mapping of elements in nums2 to their next greater element
        stack = {}

        # Create an empty stack to store elements from nums2
        s = []

        # Iterate through nums2 to find the next greater element for each element
        for num in nums2:
            # While the stack is not empty, and the current element is greater than the top element of the stack
            while s and num > s[-1]:
                # Pop the top element from the stack and map it to the current element (next greater element)
                stack[s.pop()] = num
            # Push the current element onto the stack
            s.append(num)

        # For elements remaining in the stack, there is no next greater element
        for num in s:
            stack[num] = -1

        # Create a list to store the next greater element for each element in nums1
        result = [stack[num] for num in nums1]

        return result


if __name__ == '__main__':
    print(Solution.nextGreaterElement(nums1=[4, 1, 2], nums2=[1, 3, 4, 2]))
