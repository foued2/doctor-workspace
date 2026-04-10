from typing import List


class Solution:
    @staticmethod
    def letterCombinations(digits: str) -> List[str]:
        # Check if the input string is empty
        if not digits:
            return []

        # Mapping of digits to letters
        digit_map = {
            '2': 'abc',
            '3': 'def',
            '4': 'ghi',
            '5': 'jkl',
            '6': 'mno',
            '7': 'pqrs',
            '8': 'tuv',
            '9': 'wxyz'
        }

        def generate_combinations(current_combination, index):
            # Base case: if the index is equal to the length of the digits, add the current combination to the result
            if index == len(digits):
                result.append(''.join(current_combination))
                return

            # Iterate over the letters corresponding to the current digit
            for letter in digit_map[digits[index]]:
                current_combination.append(letter)
                # Recursively generate combinations for the next digit
                generate_combinations(current_combination, index + 1)
                # Backtrack: Remove the last letter to explore other possibilities
                current_combination.pop()

        # Initialize an empty result list and start generating combinations
        result = []
        generate_combinations([], 0)
        return result


# Example usage:
solution_instance = Solution()
result_list = solution_instance.letterCombinations("23")
print(result_list)

