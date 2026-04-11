def countingValleys(steps, path):
    valleys = 0
    altitude = 0
    prev_altitude = 0

    # Iterate through each step in the path
    for step in path:
        # Update the altitude based on the current step
        if step == 'U':
            altitude += 1
        else:
            altitude -= 1

        # Check if the hiker just came out of a valley
        if prev_altitude < 0 and altitude == 0:
            valleys += 1

        # Update the previous altitude for the next step
        prev_altitude = altitude

    return valleys


print(countingValleys(8, "UDDDUDUU"))

# def countingValleys(steps, path):
#     valleys = 0
#     sea_level = 0
#     altitude = 0
#     valley = False
#
#     for step in path:
#         if step == 'U':
#             altitude += 1
#         elif step == 'D':
#             altitude -= 1
#
#         # Check if the hiker is in a valley
#         if altitude < sea_level:
#             valley = True
#
#         # Check if the hiker returned to sea level after being in a valley
#         if altitude == sea_level and valley:
#             valleys += 1
#             valley = False  # Reset the valley flag
#
#     return valleys
