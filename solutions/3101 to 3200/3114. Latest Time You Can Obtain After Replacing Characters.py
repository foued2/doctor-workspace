class Solution:
    @staticmethod
    def findLatestTime(s: str) -> str:
        # Split the input string into hour and minute parts based on the colon separator
        s = s.split(':')
        hour, minute = list(s[0]), list(s[1])

        # Determine the maximum possible value for the hour part

        # If the first character of the hour is '?'
        if hour[0] == '?':
            if hour[1] == '?':
                # If both characters are '?', the latest valid hour is "12"
                hour[0] = '1'
            elif hour[1] > '1':
                # If the second character is '2'-'9', the first can only be '0' to form '02'-'09'
                hour[0] = '0'
            else:
                # If the second character is '0' or '1', the first can be '1' to form '10'-'11'
                hour[0] = '1'

        # If the second character of the hour is '?'
        if hour[1] == '?':
            if hour[0] == '0':
                # If the first character is '0', the latest valid second character is '9' (to form '09')
                hour[1] = '9'
            else:
                # Otherwise, set the second character to '1' to make a valid hour '11'
                hour[1] = '1'

        # Determine the maximum possible value for the minute part

        # If the first character of the minute is '?'
        if minute[0] == '?':
            # Set it to '5' to make the minute as large as possible (within 00-59)
            minute[0] = '5'

        # If the second character of the minute is '?'
        if minute[1] == '?':
            # Set it to '9' to maximize the minutes
            minute[1] = '9'

        # Combine the hour and minute parts back into a single string with a colon separator
        res = ':'.join([''.join(hour), ''.join(minute)])

        # Return the resulting time string
        return res


print(Solution.findLatestTime(s="??:1?"))
