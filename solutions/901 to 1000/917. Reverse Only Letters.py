class Solution:
    @staticmethod
    def reverseOnlyLetters(s: str) -> str:
        """
        Two Pointers
        """
        # Get the length of the input string
        n = len(s)
        # Convert the string to a list to allow mutation
        res = list(s)
        # Initialize two pointers: one at the start and one at the end of the list
        i = 0
        j = n - 1

        # Iterate until the two pointers cross each other
        while i < j:
            # If both characters at pointers i and j are alphabetic, swap them
            if res[i].isalpha() and res[j].isalpha():
                res[i], res[j] = res[j], res[i]
                # Move both pointers inward
                i += 1
                j -= 1
            # If the character at pointer i is not alphabetic, move pointer i to the right
            elif not res[i].isalpha():
                i += 1
            # If the character at pointer j is not alphabetic, move pointer j to the left
            elif not res[j].isalpha():
                j -= 1

        # Join the list back into a string and return it
        return ''.join(res)


print(Solution.reverseOnlyLetters(s="a"))  # "Redo1ct-eeLg=nose-T!"


class Solution:
    @staticmethod
    def reverseOnlyLetters(s: str) -> str:
        """
        Stack
        """
        # Initialize a stack to store alphabetic characters
        stack = [char for char in s if char.isalpha()]

        # Initialize a list to build the result
        res = []

        # Iterate through the original string
        for char in s:
            # If the character is alphabetic, pop from the stack and add to the result
            if char.isalpha():
                res.append(stack.pop())
            # If the character is not alphabetic, add it directly to the result
            else:
                res.append(char)

        # Join the list into a string and return it
        return ''.join(res)


print(Solution.reverseOnlyLetters(s="Redo1ct-eeLg=nose-T!"))  # "Redo1ct-eeLg=nose-T!"
