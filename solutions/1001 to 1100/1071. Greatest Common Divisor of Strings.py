class Solution:
    from math import gcd

    def gcdOfStrings(self, str1: str, str2: str) -> str:
        """
        Find the greatest common divisor of two strings.

        :param str1: The first string.
        :param str2: The second string.
        :return: The greatest common divisor string.
        """
        # Check if concatenating both strings in different orders results in equal strings.
        if str1 + str2 != str2 + str1:
            return ""

        # If the strings are equal, then either string itself is the GCD, so we return one of the strings.
        # Otherwise, we return the common prefix of length equal to the gcd of the lengths of the strings.
        return str1[:self.gcd(len(str1), len(str2))]

    # We use the built-in gcd function from the math module to find the greatest common divisor.
    # This function is imported at the beginning of the class.
    # It takes two integers and returns their greatest common divisor.

