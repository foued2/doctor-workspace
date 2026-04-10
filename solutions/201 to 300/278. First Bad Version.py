def isBadVersion(version):
    # Implement the isBadVersion function here
    pass


class Solution:
    @staticmethod
    def firstBadVersion(n: int) -> int:
        left = 1  # Initialize left boundary to the first version
        right = n  # Initialize right boundary to the last version

        # Binary search loop
        while left <= right:
            # Calculate the midpoint
            mid = (left + right) // 2

            # Check if the current version is bad and the previous version is not bad
            if isBadVersion(mid) and not isBadVersion(mid - 1):
                return mid  # Found the first bad version

            # Adjust search boundaries based on the result of isBadVersion(mid)
            if isBadVersion(mid):
                # If the current version is bad, search in the left half (mid - 1)
                right = mid - 1
            else:
                # If the current version is not bad, search in the right half (mid + 1)
                left = mid + 1

        # If no bad version is found, return -1 or handle appropriately
        return -1


if __name__ == '__main__':
    # Replace isBadVersion function with the actual implementation
    # For testing purposes, we'll assume the first bad version is 4
    def isBadVersion(version):
        return version >= 4


    # Test the firstBadVersion method
    print(Solution.firstBadVersion(n=5))  # Output should be 4
