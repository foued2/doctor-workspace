class Solution:
    @staticmethod
    def squareIsWhite(coordinates: str) -> bool:
        # Extract the letter (column) from the coordinates
        letter = coordinates[0]
        # Convert the numeric part (row) to an integer
        n = int(coordinates[1])

        # Check if the row number is even
        if n % 2 == 0:
            # If the row is even, the columns 'a', 'c', 'e', 'g' are white
            if letter in "aceg":
                return True  # The square is white
            else:
                return False  # The square is black
        else:
            # If the row is odd, the columns 'b', 'd', 'f', 'h' are white
            if letter in "bdfh":
                return True  # The square is white
            else:
                return False  # The square is black


print(Solution.squareIsWhite(coordinates="c7"))
