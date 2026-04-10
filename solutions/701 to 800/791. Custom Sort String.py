class Solution:
    @staticmethod
    def customSortString(order: str, s: str) -> str:
        # Helper function to split the string s into two parts:
        # - Characters present in the order string (sorted_part)
        # - Characters not present in the order string (unsorted_part)
        def split_string_based_on_order(s: list, order: str):
            sorted_part = []
            unsorted_part = []
            for char in s:
                if char in order:
                    sorted_part.append(char)
                else:
                    unsorted_part.append(char)
            return sorted_part, unsorted_part

        # Convert the input string s into a list of characters
        s_list = list(s)

        # Get the sorted and unsorted parts of the string
        sorted_part, unsorted_part = split_string_based_on_order(s_list, order)

        # Sort the sorted part according to the order defined in the 'order' string
        sorted_part.sort(key=order.index)

        # Concatenate the sorted part and the unsorted part, then join them into a single string
        result = ''.join(sorted_part + unsorted_part)

        return result


if __name__ == "__main__":
    # Example usage
    print(Solution().customSortString(order="cba", s="abcd"))
