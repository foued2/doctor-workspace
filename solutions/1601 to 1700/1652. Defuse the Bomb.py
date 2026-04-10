from typing import List


class Solution:
    @staticmethod
    def decrypt(code: List[int], k: int) -> List[int]:
        # Get the length of the input list
        n = len(code)

        # If the length of the list is 1 or k is 0, return a list with n elements, all initialized to 0
        if n == 1 or k == 0:
            return [0] * n

        # Initialize a result list with n elements, all initialized to 0
        res = [0] * n

        # Calculate the initial total sum based on the value of k
        if k > 0:
            total = sum(code[1:k + 1])  # Sum of elements from index 1 to k
        else:
            total = sum(code[n + k:])  # Sum of elements from index n+k to the end

        # Iterate over each index in the range of 0 to n-1
        for i in range(n):
            # Assign the current total to the result list at index i
            res[i] = total

            # Update the total by subtracting the value at (i+1) % n and adding the value at (i+k+1) % n
            if k > 0:
                total -= code[(i + 1) % n]
                total += code[(i + k + 1) % n]
            else:
                total -= code[i + k]
                total += code[i]

        # Return the resulting list
        return res


if __name__ == '__main__':
    print(Solution.decrypt(code=[5, 7, 1, 4], k=3))
    print(Solution.decrypt(code=[2, 4, 9, 3], k=-2))
    print(Solution.decrypt(code=[1, 4], k=-1))
