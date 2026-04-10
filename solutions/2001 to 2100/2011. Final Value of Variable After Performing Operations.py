from typing import List


class Solution:
    @staticmethod
    def finalValueAfterOperations(operations: List[str]) -> int:
        ans = 0  # Initialize the variable to store the final value

        # Iterate through each operation in the list
        for op in operations:
            # Check the type of operation and update the final value accordingly
            if op == '++X' or op == 'X++':
                ans += 1
            else:
                ans -= 1

        # Return the final value after performing all the operations
        return ans


if __name__ == '__main__':
    print(Solution.finalValueAfterOperations(operations=["++X", "++X", "X++"]))
