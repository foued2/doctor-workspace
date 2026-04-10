from typing import List


class SubrectangleQueries:
    def __init__(self, rectangle: List[List[int]]):
        # Store the input rectangle as an instance variable
        self.rectangle = rectangle

    def updateSubrectangle(self, row1: int, col1: int, row2: int, col2: int, newValue: int) -> None:
        # Loop through each row in the specified subrectangle
        for i in range(row1, row2 + 1):
            # Loop through each column in the specified subrectangle
            for j in range(col1, col2 + 1):
                # Update the current element to the new value
                self.rectangle[i][j] = newValue

    def getValue(self, row: int, col: int) -> int:
        # Return the value at the specified position in the rectangle
        return self.rectangle[row][col]

# Your SubrectangleQueries object will be instantiated and called as such:
# obj = SubrectangleQueries(rectangle)
# obj.updateSubrectangle(row1,col1,row2,col2,newValue)
# param_2 = obj.getValue(row,col)
