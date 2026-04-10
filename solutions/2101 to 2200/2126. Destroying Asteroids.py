from typing import List


class Solution:
    @staticmethod
    def asteroidsDestroyed(mass: int, asteroids: List[int]) -> bool:
        # Sort the asteroids in ascending order of their masses
        asteroids = sorted(asteroids)

        # Iterate through each asteroid in the sorted list
        for asteroid in asteroids:
            # Check if the mass of the current asteroid is greater than the given mass
            if asteroid > mass:
                # If the current asteroid's mass is greater than the given mass,
                # the mass is insufficient to destroy it, so return False
                return False
            else:
                # If the current asteroid's mass is not greater than the given mass,
                # add its mass to the current mass, as it can be destroyed
                mass += asteroid

        # If all asteroids can be destroyed with the given mass,
        # return True after iterating through all asteroids
        return True

    print(asteroidsDestroyed(mass=5, asteroids=[4, 9, 23, 4]))
