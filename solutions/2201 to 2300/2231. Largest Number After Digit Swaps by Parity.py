import heapq


class Solution:
    @staticmethod
    def largestInteger(num: int) -> int:
        # Initialize max-heaps for odd and even digits
        max_heap_odd = []
        max_heap_even = []

        # Traverse each character in the string representation of the number
        for char in str(num):
            digit = int(char)
            # If the digit is even, push it onto the even max-heap (negated to simulate max-heap using min-heap)
            if digit % 2 == 0:
                heapq.heappush(max_heap_even, -digit)
            # If the digit is odd, push it onto the odd max-heap (negated to simulate max-heap using min-heap)
            else:
                heapq.heappush(max_heap_odd, -digit)

        # Result list to store the digits of the new largest integer
        res = []

        # Traverse again to form the result list based on original parity positions
        for char in str(num):
            digit = int(char)
            # If the digit is even, pop the largest even digit from the heap and append
            if digit % 2 == 0:
                res.append(str(-heapq.heappop(max_heap_even)))
            # If the digit is odd, pop the largest odd digit from the heap and append
            else:
                res.append(str(-heapq.heappop(max_heap_odd)))

        # Join the result list to form the final largest integer and return it
        return int(''.join(res))


if __name__ == '__main__':
    # Test case: print the largest integer by rearranging the digits of 65875
    print(Solution.largestInteger(65875))


class Solution:
    @staticmethod
    def largestInteger(num: int) -> int:
        nums = list(int(i) for i in str(num))

        # Separate and sort even and odd digits in descending order
        evens = sorted([i for i in nums if i % 2 == 0], reverse=True)
        odds = sorted([i for i in nums if i % 2 != 0], reverse=True)

        # Result list to store digits in the correct order
        res = []
        even_index = 0
        odd_index = 0

        for n in nums:
            if n % 2 == 0:
                # Append the next largest even digit
                res.append(evens[even_index])
                even_index += 1
            else:
                # Append the next largest odd digit
                res.append(odds[odd_index])
                odd_index += 1

        # Convert the list of digits back to an integer
        return int(''.join(map(str, res)))


if __name__ == '__main__':
    # Test case: print the largest integer by rearranging the digits of 65875
    print(Solution.largestInteger(65875))