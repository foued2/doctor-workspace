class Solution:
    @staticmethod
    def angleClock(hour: int, minutes: int) -> float:
        # Each hour is represented by 30 degrees on the clock (360 degrees / 12 hours)
        degrees_per_hour = 30

        # Each minute is represented by 6 degrees on the clock (360 degrees / 60 minutes)
        degrees_per_minute = 6

        # Calculate the angle of the minute hand from 12:00
        minute_angle = minutes * degrees_per_minute

        # Calculate the contribution of the minutes to the hour hand's position
        # Each minute the hour hand moves by 0.5 degrees (30 degrees / 60 minutes)
        minute_contribution_to_hour_angle = minutes * 0.5

        # Calculate the angle of the hour hand from 12:00
        hour_angle = (hour % 12) * degrees_per_hour + minute_contribution_to_hour_angle

        # Calculate the absolute difference between the two angles
        angle = abs(minute_angle - hour_angle)

        # The angle between the two hands could be the smaller of the two possibilities
        # Either the calculated angle or 360 - calculated angle
        angle = min(angle, 360 - angle)

        return angle


# Test case
hour = 8
minutes = 7
solution = Solution()
print(solution.angleClock(hour, minutes))  # Output should be 158.5

