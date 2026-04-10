from typing import List


class Solution:
    @staticmethod
    def convertTemperature(celsius: float) -> List[float]:
        # Convert temperature to Kelvin
        kelvin = celsius + 273.15

        # Convert temperature to Fahrenheit
        fahrenheit = celsius * 1.80 + 32.00

        # Store the results in a list
        res = [kelvin, fahrenheit]

        # Return the list containing temperature in Kelvin and Fahrenheit
        return res


if __name__ == '__main__':
    print(Solution.convertTemperature(celsius=122.11))
