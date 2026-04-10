class Solution:
    # Constant for the number of digits to pad
    DIGIT_COUNT = 4

    @staticmethod
    def generate_key(num1: int, num2: int, num3: int) -> int:
        # Pad the given numbers to DIGIT_COUNT length
        padded_numbers = Solution._pad_numbers([num1, num2, num3])
        # Build the key from the padded numbers and return it
        return Solution._build_key_from_digits(padded_numbers)

    @staticmethod
    def _pad_numbers(numbers: list[int]) -> list[str]:
        # Convert each number to string and pad it with leading zeros to DIGIT_COUNT length
        return [str(num).zfill(Solution.DIGIT_COUNT) for num in numbers]

    @staticmethod
    def _build_key_from_digits(padded_numbers: list[str]) -> int:
        # Initialize an empty string to build the key
        key = ''
        # Iterate over each digit position
        for digit_group in zip(*padded_numbers):
            # Find the minimum digit for the current position and append to key
            key += min(digit_group)
        # Convert the constructed key string to an integer and return it
        return int(key)


if __name__ == '__main__':
    # Example usage: prints the generated key for the provided numbers
    print(Solution().generate_key(num1=1, num2=2, num3=3))