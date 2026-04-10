import time

# Record the start time
start_time = time.perf_counter()


class Solution:
    @staticmethod
    def isAnagram(s: str, t: str) -> bool:
        # Check if the lengths of the strings are different
        if len(s) != len(t):
            return False

        # Initialize dictionaries to store character frequencies
        s_freq = {}
        t_freq = {}

        # Count frequencies of characters in string s
        for char in s:
            s_freq[char] = s_freq.get(char, 0) + 1

        # Count frequencies of characters in string t
        for char in t:
            t_freq[char] = t_freq.get(char, 0) + 1

        # Compare the frequencies of characters in both strings
        for char in s_freq:
            # If the character in s is not in t or the frequencies are different, return False
            if char not in t_freq or s_freq[char] != t_freq[char]:
                return False

        # If all characters have the same frequencies in both strings, return True
        return True


# Perform the function call
print(Solution.isAnagram(s="rat", t="car"))

# Record the end time
end_time = time.perf_counter()

# Calculate the runtime
runtime = (end_time - start_time) * 1000  # Convert to milliseconds

# Print the runtime
print("Runtime:", runtime, "milliseconds")
