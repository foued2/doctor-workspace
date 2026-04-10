class ParkingSystem:

    def __init__(self, big: int, medium: int, small: int):
        # Initialize the parking spaces for each car type
        self.big = big
        self.medium = medium
        self.small = small

        # Create a dictionary to map car types to available parking spaces
        self.cars = {1: big,  # Type 1 corresponds to 'big' cars
                     2: medium,  # Type 2 corresponds to 'medium' cars
                     3: small}  # Type 3 corresponds to 'small' cars

    def addCar(self, carType: int) -> bool:
        # Check if there is available space for the given car type
        if self.cars[carType] > 0:
            # If space is available, reduce the count of available spaces by 1
            self.cars[carType] -= 1
            return True  # Car successfully parked
        else:
            return False  # No available space for the given car type


# Example usage
# Your ParkingSystem object will be instantiated and called as such:
obj = ParkingSystem(1, 1, 0)

# Attempt to park a big car (carType 1)
param_1 = obj.addCar(1)
print(param_1)  # Output: True

# Attempt to park another big car (carType 1)
param_2 = obj.addCar(1)
print(param_2)  # Output: False (no space left for big cars)

# Attempt to park a medium car (carType 2)
param_3 = obj.addCar(2)
print(param_3)  # Output: True

# Attempt to park a small car (carType 3)
param_4 = obj.addCar(3)
print(param_4)  # Output: False (no space for small cars)
