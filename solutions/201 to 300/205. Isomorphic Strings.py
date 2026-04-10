class Solution:
    @staticmethod
    def isIsomorphic(s: str, t: str) -> bool:
        if len(s) != len(t):
            return False

        # Initialize hash tables to store mappings from s to t and t to s
        s_to_t_mapping = {}
        t_to_s_mapping = {}

        for char_s, char_t in zip(s, t):
            # Check mapping from s to t
            if char_s in s_to_t_mapping:
                if s_to_t_mapping[char_s] != char_t:
                    return False
            else:
                s_to_t_mapping[char_s] = char_t

            # Check mapping from t to s
            if char_t in t_to_s_mapping:
                if t_to_s_mapping[char_t] != char_s:
                    return False
            else:
                t_to_s_mapping[char_t] = char_s

        return True


# Test the implementation
print(Solution.isIsomorphic(s="foo", t="bar"))  # Output: False
