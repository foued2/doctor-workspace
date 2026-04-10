from typing import List


class Solution:
    @staticmethod
    def findKOr(nums: List[int], k: int) -> int:
        # Convert integers to binary string representation
        binary_nums = Solution.convert_to_binary(nums)

        # Determine the length of the longest binary string
        max_len = max(map(len, binary_nums))

        # Fill all binary strings with leading zeros to match the max length
        filled_binary_nums = Solution.fill_zeros(binary_nums, max_len)

        # Calculate the K-Or result as a binary string
        result = Solution.calculate_k_or(filled_binary_nums, k, max_len)

        # Convert the binary result to an integer and return
        return int(result, 2)

    @staticmethod
    def convert_to_binary(nums: List[int]) -> List[str]:
        """
        Convert each integer in the list to its binary string representation.
        """
        return [bin(num)[2:] for num in nums]

    @staticmethod
    def fill_zeros(binary_nums: List[str], max_len: int) -> List[str]:
        """
        Fill each binary string with leading zeros to match the length of the longest binary string.
        """
        return [num.zfill(max_len) for num in binary_nums]

    @staticmethod
    def calculate_k_or(binary_nums: List[str], k: int, max_len: int) -> str:
        """
        Calculate the K-Or result as a binary string where each bit is set to '1'
        if at least 'k' numbers have that bit set to '1', otherwise '0'.
        """
        result = ''
        for i in range(max_len):
            # Count the number of '1's in the current bit position across all binary numbers
            count = sum(num[i] == '1' for num in binary_nums)

            # Append '1' to the result if at least 'k' numbers have the current bit set to '1'
            if count >= k:
                result += '1'
            else:
                # Append '0' otherwise
                result += '0'

        return result


if __name__ == '__main__':
    print(Solution().findKOr(nums=[7, 12, 9, 8, 9, 15], k=4))


class Solution:
    @staticmethod
    def findKOr(nums: List[int], k: int) -> int:
        ans = 0  # Initialize the answer to 0.

        for i in range(31):  # Iterate over each bit position from 0 to 30.
            rep = 1 << i  # Calculate the bit mask for the 'i-th' bit position.
            cnt = 0  # Initialize a counter to count the number of set bits at the 'i-th' position.

            for ele in nums:  # Iterate through the input list 'nums'.
                if (rep & ele) != 0:  # If the 'i-th' bit in 'ele' is set (i.e., 1), increment the count.
                    cnt += 1

            # If the count of set bits at the 'i-th' position is greater than or equal to 'k',
            # set the corresponding bit in the 'ans' variable.
            if cnt >= k:
                ans = ans + rep  # Update the answer by adding the current bit position value.

        return ans  # Return the final result.


if __name__ == '__main__':
    print(Solution().findKOr(nums=[7, 12, 9, 8, 9, 15], k=4))
