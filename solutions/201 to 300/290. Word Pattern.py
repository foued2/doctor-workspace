from collections import defaultdict


class Solution:
    @staticmethod
    def wordPattern(pattern, s):
        # Create a defaultdict to store mappings from pattern characters to words
        dic = defaultdict(str)
        print(dic)

        # Split the string s into words
        words = s.split(' ')

        # Check if the lengths of pattern and words are different, or if there are different number of unique
        # elements in both
        if len(pattern) != len(words) or len(set(pattern)) != len(set(words)):
            return False

        # Iterate over the pattern characters along with their indices
        for i, c in enumerate(pattern):
            # Check if the current character c is already mapped to a word
            if c in dic:
                # If it is, check if the mapping matches the current word
                if dic[c] != words[i]:
                    return False
            else:
                # If the character is not in the mapping, add it along with its corresponding word
                dic[c] = words[i]

        # If the loop completes without returning False, the pattern matches the string
        return True

    print(wordPattern(pattern="aaaa", s="dog cat cat dog"))


# Regular dictionary
regular_dict = {}

# Trying to access a missing key in a regular dictionary raises KeyError
# print(regular_dict['key'])  # This would raise KeyError: 'key'

# Defaultdict with int as the default factory
default_dict = defaultdict(int)

# Accessing a missing key in a defaultdict creates the key with the default value for int, which is 0
print(default_dict['key'])  # Outputs: 0
