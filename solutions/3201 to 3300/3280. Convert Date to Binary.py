class Solution:
    @staticmethod
    def convertDateToBinary(date: str) -> str:
        # Split the input date string by '-'
        date_parts = date.split('-')

        # Convert each part of the date to binary and join them back with '-'
        date_binary = '-'.join(bin(int(part))[2:] for part in date_parts)

        # Return the binary representation of the date
        return date_binary


if __name__ == "__main__":
    # Example usage: prints the binary representation of the date "2080-02-29"
    print(Solution.convertDateToBinary(date="2080-02-29"))