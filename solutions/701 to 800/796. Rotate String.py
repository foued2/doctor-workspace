class Solution:
    @staticmethod
    def rotateString(s: str, goal: str) -> bool:
        # Convert the string 's' to a list of characters for easy manipulation
        s = list(s)

        # Initialize a count variable to track the number of rotations
        count = 0

        # Iterate until all possible rotations are exhausted
        for _ in range(len(s)):
            # Check if the current configuration matches the target string 'goal'
            if ''.join(s) != goal:
                # If not, rotate the string by moving the first character to the end
                s.append(s.pop(0))
                # Increment the count of rotations
                count += 1
            else:
                # If the strings match, return True
                return True

        # If all possible rotations have been performed and the strings still don't match, return False
        return False


print(Solution.rotateString(s="abcde", goal="cdeab"))
