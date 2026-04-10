from typing import List


class Solution:
    @staticmethod
    def addToArrayForm(num: List[int], k: int) -> List[int]:
        # Helper function to zip two lists of different lengths with a fill value
        def zip_longest_fillvalue(list1, list2, fillvalue=0):
            # Get the maximum length of the two lists
            max_len = max(len(list1), len(list2))

            # Create the result list
            result = []

            # Iterate over the range of the maximum length
            for i in range(max_len):
                # Get the element from list1 or use fillvalue if the index is out of range
                elem1 = list1[i] if i < len(list1) else fillvalue

                # Get the element from list2 or use fillvalue if the index is out of range
                elem2 = list2[i] if i < len(list2) else fillvalue

                # Append the tuple of elements to the result list
                result.append((elem1, elem2))

            return result

        # Convert k to a list of digits in reverse order
        k = [int(i) for i in str(k)][::-1]

        # Reverse num to align with the least significant digits of k
        num = num[::-1]

        # Zip num and k with the helper function to handle different lengths
        res = zip_longest_fillvalue(num, k)

        # Initialize the result list with zeros, with an extra space for carry-over
        ans = [0] * (len(res) + 1)

        # Iterate over the zipped pairs and perform the addition
        carry = 0
        for i, pair in enumerate(res):
            total = sum(pair) + carry  # Sum the pair of digits along with carry
            ans[i] = total % 10  # Store the unit place of the total
            carry = total // 10  # Calculate carry for the next place

        # Handle the final carry
        if carry > 0:
            ans[len(res)] = carry

        # Reverse the result to get the final array form and remove leading zeros
        while ans[-1] == 0 and len(ans) > 1:
            ans.pop()

        return ans[::-1]


# Example usage
sol = Solution()
num = [9, 9, 9, 9, 9, 9, 9, 9, 9, 9]
k = 1
print(sol.addToArrayForm(num, k))  # Output: [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


class Solution:
    @staticmethod
    def addToArrayForm(num: List[int], k: int) -> List[int]:
        """
        Array, Handling carries (sum overflow)
        """
        num.reverse()  # Reverse the list to start from the least significant digit

        # Iterate over each digit in num
        for i in range(len(num)):
            num[i] += k  # Add k to the current digit
            # Divide the current digit by 10 to get the quotient (k) and the remainder (num[i])
            # num[i] represents the current digit being processed
            k, num[i] = divmod(num[i], 10)

        # Handle any remaining carry
        while k:
            num.append(k % 10)  # Append the carry to the list
            k //= 10  # Update k for further carry

        num.reverse()  # Reverse the list back to its original order
        return num  # Return the updated list


# Example usage
sol = Solution()
num = [9, 9, 9, 9, 9, 9, 9, 9, 9, 9]
k = 1
print(sol.addToArrayForm(num, k))  # Output: [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
