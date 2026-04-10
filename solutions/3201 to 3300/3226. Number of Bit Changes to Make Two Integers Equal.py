

class Solution:
    @staticmethod
    def minChanges(n: int, k: int) -> int:
        # If k has bits set to 1 that n cannot cover, it's impossible
        if bin(k & ~n).count('1') > 0:
            return -1

        # XOR `n` and `k` to get the differing bits
        differing_bits = n ^ k

        # Count the number of 1s in differing_bits where n has 1s
        changes_needed = bin(differing_bits & n).count('1')

        return changes_needed


# Example usage
sol = Solution()
print(sol.minChanges(13, 9))  # Output should be 1
print(sol.minChanges(13, 15))  # Output should be -1


class Solution:
    @staticmethod
    def minChanges(n: int, k: int) -> int:
        # If k has bits set to 1 that n cannot cover, it's impossible
        if bin(k & ~n).count('1') > 0:
            return -1

        # XOR `n` and `k` to get the differing bits
        differing_bits = n ^ k

        # Count the number of 1s in differing_bits where n has 1s
        changes_needed = bin(differing_bits & n).count('1')

        return changes_needed


# Example usage
sol = Solution()
print(sol.minChanges(13, 9))  # Output should be 1
print(sol.minChanges(13, 15))  # Output should be -1
