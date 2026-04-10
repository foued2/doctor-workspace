from typing import List


class Solution:
    @staticmethod
    def countStudents(students: List[int], sandwiches: List[int]) -> int:
        # Loop until there are sandwiches left and the current sandwich is in students' preferences
        while sandwiches and sandwiches[0] in students:
            # If the first student's preference matches the current sandwich
            if students[0] == sandwiches[0]:
                # Serve the sandwich to the student by removing both from their lists
                students.pop(0)
                sandwiches.pop(0)
            else:
                # If the current sandwich doesn't match the first student's preference,
                # rotate the first student to the end of the list
                students.append(students.pop(0))

        # Return the number of non served students, which is the length of the remaining students' list
        return len(students)


if __name__ == '__main__':
    print(Solution.countStudents(students=[1, 1, 0, 0], sandwiches=[0, 1, 0, 1]))