# Define a new class called Solution.
class Solution:
    # Define a static method called findMinimumOperations. A static method can be 
    # called on the class itself, no instance of the class is necessary. "@staticmethod"
    # decorator is used to let Python know that this method is static.
    @staticmethod
    def findMinimumOperations(s1: str, s2: str, s3: str) -> int:
        # First, check if the first characters of the 3 strings are the same.
        # This is necessary because if the first characters are not the same, it means
        # that we cannot make them the same by removing characters from a right.
        if not (s1[0] == s2[0] == s3[0]):
            # If the first characters are not the same, return -1 immediate as there is 
            # no way to achieve our goal.
            return -1
        # Initialize a variable called 'k' to keep track of same characters in the 3 strings 
        # from the beginning
        k = 0
        # Now iterate through every character (c1, c2, and c3 respectively) from s1, s2 and s3, using the zip()
        # function.
        # The zip function combines elements based on their positions, creating tuples where
        # the first element comes from the first iterable, the second element from the second iterable,
        # and so on. It doesn't mix the elements randomly; rather, it pairs them in order.
        for c1, c2, c3 in zip(s1, s2, s3):
            # Check if c1, c2 and c3 are all the same.
            if not (c1 == c2 == c3):
                # If they are not the same, it means we have reached the point of divergence, 
                # and thus we break the loop.
                break
            # If they are the same, we increment k by 1.
            # This helps to track the number of same characters from the start of three strings. 
            k += 1
        # Then we return the sum of lengths of 3 strings minus the number of same characters 
        # from the start of three strings (k * 3)
        # This will be the minimum number of operations to make 3 strings equal.
        return len(s1) + len(s2) + len(s3) - (k * 3)


# Calling the static method of Solution class with 3 string parameters
print(Solution.findMinimumOperations("a", "a", "a"))
