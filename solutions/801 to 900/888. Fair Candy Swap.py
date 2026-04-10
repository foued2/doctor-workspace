from typing import List


class Solution:
    @staticmethod
    def fairCandySwap(aliceSizes: List[int], bobSizes: List[int]) -> List[int]:
        # Calculate the total amount of candy Alice and Bob have
        alice_sum = sum(aliceSizes)
        bob_sum = sum(bobSizes)

        # Calculate the target difference that needs to be balanced by the swap
        target = (alice_sum - bob_sum) // 2

        # Sort Bob's candy sizes for binary search
        bobSizes.sort()

        # Helper function to perform binary search in Bob's candy sizes
        def binary_search(arr, x):
            left, right = 0, len(arr) - 1
            while left <= right:
                mid = (left + right) // 2
                if arr[mid] == x:
                    return True
                elif arr[mid] < x:
                    left = mid + 1
                else:
                    right = mid - 1
            return False

        # Iterate through each candy size in Alice's list
        for a in aliceSizes:
            # Calculate the corresponding candy size in Bob's list needed to balance the sums
            b = a - target
            # Use binary search to check if the corresponding candy size is in Bob's list
            if binary_search(bobSizes, b):
                return [a, b]

        # In case, no valid swap is found (though the problem guarantees one exists)
        return []


# Example usage
solution = Solution()
print(solution.fairCandySwap([1, 1], [2, 2]))  # Output: [1, 2]
print(solution.fairCandySwap([1, 2, 5], [2, 4]))  # Output: [5, 4]
