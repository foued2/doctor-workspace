class Solution:
    @staticmethod
    def minMoves(target: int, maxDoubles: int) -> int:
        count = 0  # Initialize the move counter

        # Continue the loop until target is reduced to 1 or no more doubles are allowed
        while target > 1 and maxDoubles:
            if target % 2 == 0:
                # If target is even, use one double operation
                target //= 2
                maxDoubles -= 1
            else:
                # If target is odd, subtract 1 to make it even
                target -= 1
            count += 1  # Increment the move counter

        # If maxDoubles are exhausted, we simply subtract 1 from target to make it 1
        # Each subtraction represents a move
        count += target - 1

        return count  # Return the total number of moves


if __name__ == '__main__':
    # Example usage of the function to determine minimum moves
    print(Solution().minMoves(target=5, maxDoubles=0))  # Output the minimum moves to reach 1
