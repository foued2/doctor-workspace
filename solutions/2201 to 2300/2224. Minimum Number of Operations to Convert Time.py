class Solution:
    @staticmethod
    def convertTime(current: str, correct: str) -> int:
        # Initialize the variable to store the answer
        ans = 0

        # Split the current time string by ':' and convert each part to an integer
        current = [int(i) for i in current.split(':')]
        # Convert the current time to total minutes
        current = (current[0] * 60) + current[1]

        # Split the correct time string by ':' and convert each part to an integer
        correct = [int(i) for i in correct.split(':')]
        # Convert the correct time to total minutes
        correct = (correct[0] * 60) + correct[1]

        # Calculate the difference in minutes between the correct time and the current time
        diff = correct - current

        # List of possible changes in minutes: 60 minutes, 15 minutes, 5 minutes, 1 minute
        change = [60, 15, 5, 1]
        # Initialize the index to traverse the change list
        i = 0

        # Loop until the difference becomes zero
        while diff:
            # Calculate how many times the current change can fit into the difference
            quotient, remainder = divmod(diff, change[i])
            # Add the quotient to the answer (number of operations)
            ans += quotient
            # Update the difference to the remainder
            diff = remainder
            # Move to the next change in the list
            i += 1

        # Return the total number of operations needed
        return ans


print(Solution.convertTime(current="02:30", correct="04:35"))
