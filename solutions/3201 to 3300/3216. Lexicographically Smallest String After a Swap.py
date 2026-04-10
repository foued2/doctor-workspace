class Solution:
    @staticmethod
    def getSmallestString(s: str) -> str:
        # Convert the string 's' to a list of integers
        s = list(map(int, s))
        # Get the length of the list
        n = len(s)
        # Iterate through the list up to the second last element
        for i in range(n - 1):
            # Check if the current element is greater than the next element
            # and both elements have the same parity (either both are even or both are odd)
            if s[i] > s[i + 1] and s[i] % 2 == s[i + 1] % 2:
                # Swap the current element with the next element
                s[i], s[i + 1] = s[i + 1], s[i]
                # Break after the first swap
                break
        # Convert the list back into a string of integers and return it
        return "".join(str(i) for i in s)


if __name__ == "__main__":
    # Test the method with the input string "001" and print the result
    print(Solution().getSmallestString(s="001"))