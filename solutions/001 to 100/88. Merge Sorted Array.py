# EASY // MERGE TWO ARRAYS // TWO POINTERS (Last Valid / Last Valid ) // SORTING (Last Item)

# Define a class called Solution.
class Solution(object):
    # Declare a static method merge() inside the Solution class.
    @staticmethod
    # merge() receives two sorted lists, nums1 and nums2, along with their valid sizes, m and n respectively.
    def merge(nums1, m, nums2, n):
        # three pointers: i, j, and k are initialized. Pointers i and j point to the last valid elements in nums1 and
        # nums2 respectively. The pointer k points to the last element of the nums1 list.
        i = m - 1
        j = n - 1
        k = m + n - 1

        # Start a loop which ends when j becomes negative, i.e., when all elements in nums2 have been compared.
        while j >= 0:
            # Checks whether pointer i is within the list bounds and nums1[i] is greater than nums2[j].
            # If the condition is True, place the larger element pointed to by i at the position pointed to by k.
            if i >= 0 and nums1[i] > nums2[j]:
                nums1[k] = nums1[i]
                i -= 1  # Decrement pointer i.
            else:
                # If nums1[i] is not greater than nums2[j], then place the element pointed to by j in nums1 at the
                # position pointed to by k.
                nums1[k] = nums2[j]
                j -= 1  # Decrement pointer j.
            k -= 1  # After each comparison, decrement pointer k.
        return nums1
    # Call the merge() method with two lists [1, 2, 3, 0, 0, 0] and [2, 5, 6], and their lengths 3 and 3 respectively.
    # The result of the merge operation will be printed.
    print(merge([1, 2, 3, 8, 10, 20], 3, [2, 5, 6], 3))
