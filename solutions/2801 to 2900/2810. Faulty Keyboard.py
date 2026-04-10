class Solution:
    @staticmethod
    def finalString(s: str) -> str:
        # Convert the input string into a list of characters
        text = list(s)
        # Initialize an empty list to store the output characters
        output = []

        # Iterate through each character in the input string
        for i in text:
            # If the current character is 'i'
            if i == 'i':
                # Reverse the order of characters accumulated so far
                output.reverse()
            else:
                # Append the current character to the output list
                output.append(i)

        # Join the characters in the output list to form the final string
        return "".join(output)


print(Solution.finalString(s="poiinter"))
