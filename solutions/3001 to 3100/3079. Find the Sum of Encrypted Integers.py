from typing import List


class Solution:
    @staticmethod
    def encrypt(x: int) -> int:
        # Convert the integer to a string to manipulate digits
        str_x = str(x)

        # Find the maximum digit in the integer
        max_digit = max(str_x)

        # Encrypt the integer by repeating the maximum digit
        encrypted_x = int(max_digit * len(str_x))

        # Return the encrypted integer
        return encrypted_x

    def sumOfEncryptedInt(self, nums: List[int]) -> int:
        # Initialize the total sum
        total_sum = 0

        # Iterate over each integer in the list
        for num in nums:
            # Encrypt the current integer and add it to the total sum
            total_sum += self.encrypt(num)

        # Return the total sum of encrypted integers
        return total_sum


solution = Solution()
arr = [109]
result = solution.sumOfEncryptedInt(arr)
print(result)

