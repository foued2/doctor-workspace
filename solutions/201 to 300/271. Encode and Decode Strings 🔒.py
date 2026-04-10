from typing import List


class Solution:
    @staticmethod
    def encode(strs: List[str]) -> str:
        # Use a generator expression to format each string
        # f'{len(s)}:{s}' creates a string where len(s) is the length of s
        encoded_strs = ''.join(f'{len(s)}:{s}' for s in strs)
        return encoded_strs

    @staticmethod
    def decode(s: str) -> List[str]:
        decoded_strs = []
        i = 0
        while i < len(s):
            # Find the next colon in the string, which follows the length prefix
            j = s.find(':', i)
            # Extract the length of the next substring
            length = int(s[i:j])
            # Append the substring to the output list
            # j+1 is the start of the actual string after the colon
            # j+1+length is the end of the string
            decoded_strs.append(s[j + 1:j + 1 + length])
            # Move the index to the end of the current substring
            i = j + 1 + length
        return decoded_strs


if __name__ == '__main__':
    s = Solution()
    print(s.encode(["Hello", "World"]))
    print(s.decode("10:h1e1l1l1o"))
