class Solution:
    @staticmethod
    def maximumTime(time: str) -> str:
        # Convert the input time string into a list of characters for easier manipulation
        time = list(time)

        # Determine the maximum possible value for the first digit of the hour
        if time[0] == '?':
            if time[1] == '?' or time[1] < '4':  # If the second digit is unknown or less than 4
                time[0] = '2'  # The first digit can be 2 (to allow 20, 21, 22, 23)
            else:
                time[0] = '1'  # Otherwise, the first digit should be 1 (to allow 10-19)

        # Determine the maximum possible value for the second digit of the hour
        if time[1] == '?':
            if time[0] == '2':  # If the first digit is 2
                time[1] = '3'  # The second digit can be at most 3 (to allow 23)
            else:
                time[1] = '9'  # Otherwise, it can be 9 (to allow 19, 09, etc.)

        # Determine the maximum possible value for the first digit of the minutes
        if time[3] == '?':
            time[3] = '5'  # The first digit of minutes can be at most 5

        # Determine the maximum possible value for the second digit of the minutes
        if time[4] == '?':
            time[4] = '9'  # The second digit of minutes can be at most 9

        # Join the list back into a string and return the result
        return ''.join(time)


print(Solution.maximumTime(time="1?:22"))
