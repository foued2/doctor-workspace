class Solution:
    # creating a static class method that takes a string as input and returns an integer
    @staticmethod
    def minimumSteps(s: str) -> int:
        # initializing variables res and swaps to 0
        res, swaps = 0, 0
        # looping through each character in the input string
        for ch in s:
            # if character is '1'
            if ch == '1':
                # increment swaps by 1
                swaps += 1
            else:  # if character is not '1' (i.e., '0')
                # add number of swaps to res
                res += swaps
        # return res, the total number of swaps needed to move all the '1's to the left
        return res


# calling the minimumSteps method on a test string and print the result
print(Solution.minimumSteps("110001111"))
