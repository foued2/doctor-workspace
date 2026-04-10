import itertools


class Solution:
    @staticmethod
    def backspaceCompare(s: str, t: str) -> bool:
        """
        Stack, Build String
        """
        # Helper function to process the given string and return the final string after applying backspace
        def process_string(input_str):
            # Use a list to simulate a stack
            result = list()

            for char in input_str:
                if char != '#':
                    result.append(char)
                # If the stack is not empty, pop the last character (backspace)
                elif result:
                    result.pop()
            return ''.join(result)  # Convert the list back to a string

        # Process both strings and compare the final results
        return process_string(s) == process_string(t)


if __name__ == '__main__':
    print(Solution.backspaceCompare(s="ab#c", t="ad#c"))  # Output: True
    print(Solution.backspaceCompare(s="ab##", t="c#d#"))  # Output: True
    print(Solution.backspaceCompare(s="a##c", t="#a#c"))  # Output: True


class Solution:
    @staticmethod
    def backspaceCompare(S: str, T: str) -> bool:
        # Helper function to process the string considering backspaces
        def F(S):
            skip = 0
            for x in reversed(S):
                if x == '#':
                    skip += 1  # Increment skip counter for backspaces
                elif skip:
                    skip -= 1  # Skip the character if there's a backspace
                else:
                    yield x  # Yield the character if it shouldn't be skipped

        # Compare processed versions of both strings
        return all(x == y for x, y in itertools.zip_longest(F(S), F(T)))


# Example usage
solution = Solution()
print(solution.backspaceCompare("ab#c", "ad#c"))  # Output: True (both become "ac")
print(solution.backspaceCompare("ab##", "c#d#"))  # Output: True (both become "")
print(solution.backspaceCompare("a##c", "#a#c"))  # Output: True (both become "c")
print(solution.backspaceCompare("a#c", "b"))  # Output: False ("c" vs "b")
