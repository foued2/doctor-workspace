from typing import List


class Solution:
    @staticmethod
    def calPoints(ops: List[str]) -> int:
        stack = []
        for op in ops:
            if op.isdigit() or (op.startswith('-') and op[1:].isdigit()):  # Check if op is a digit or a negative number
                stack.append(int(op))
            elif op == '+':
                stack.append(stack[-1] + stack[-2])  # Calculate a sum of the last two scores
            elif op == 'D':
                stack.append(stack[-1] * 2)  # Double the last score
            elif op == 'C':
                stack.pop()  # Remove the last valid score
        return sum(stack)


if __name__ == "__main__":
    print(Solution.calPoints(["5", "2", "C", "D", "+"]))  # Output: 30
    print(Solution.calPoints(ops=["5", "-2", "4", "C", "D", "9", "+", "+"]))  # Output: 27
