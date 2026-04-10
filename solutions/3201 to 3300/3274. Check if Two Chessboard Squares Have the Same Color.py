class Solution:
    @staticmethod
    def checkTwoChessboards(coordinate1: str, coordinate2: str) -> bool:
        # Dictionary mapping columns (files) of the chessboard to numbers
        chessboard = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8}

        # Calculate the square value for the first coordinate
        # For example, "h7" would be mapped to chessboard['h'] + 7 => 8 + 7 = 15
        square1 = chessboard[coordinate1[0]] + int(coordinate1[1])

        # Calculate the square value for the second coordinate
        # For example, "c8" would be mapped to chessboard['c'] + 8 => 3 + 8 = 11
        square2 = chessboard[coordinate2[0]] + int(coordinate2[1])

        # Check if both squares have the same parity (both even or both odd)
        # If they do, both squares have the same color on a chessboard
        return square1 % 2 == square2 % 2


if __name__ == "__main__":
    # Example usage of the function to check if two squares are of the same color
    print(Solution().checkTwoChessboards("h7", "c8"))  # Output: True