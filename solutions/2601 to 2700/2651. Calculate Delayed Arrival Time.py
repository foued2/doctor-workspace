class Solution:
    @staticmethod
    def findDelayedArrivalTime(arrivalTime: int, delayedTime: int) -> int:
        # Check if the sum of arrival time and delayed time is less than 24 hours
        if arrivalTime + delayedTime < 24:
            # If so, set the result to the sum of arrival time and delayed time
            ans = arrivalTime + delayedTime
        # Check if the sum of arrival time and delayed time is a multiple of 24
        elif (arrivalTime + delayedTime) % 24 == 0:
            # If so, set the result to 0 (as it's the start of a new day)
            ans = 0
        else:
            # Otherwise, calculate the result as the remainder when the sum is divided by 24
            ans = (arrivalTime + delayedTime) % 24

        # Return the calculated result
        return ans


print(Solution.findDelayedArrivalTime(arrivalTime=13, delayedTime=110))
