from typing import List


class Solution:
    @staticmethod
    def getSneakyNumbers(nums: List[int]) -> List[int]:
        # This list will store the result
        res = []
        # This dictionary will store the frequency of each number
        table = {}

        # Iterate through each number in the input list
        for num in nums:
            # If the number is already in the dictionary, increment its count
            if num in table:
                table[num] += 1
                # If the count becomes 2, add the number to the result list
                if table[num] == 2:
                    res.append(num)

            # If the number is not in the dictionary, add it with count 1
            if num not in table:
                table[num] = 1

        return res


# Example usage to print the first two sneaky numbers
if __name__ == '__main__':
    print(Solution().getSneakyNumbers([7, 1, 5, 4, 3, 4, 6, 0, 9, 5, 8, 2]))
