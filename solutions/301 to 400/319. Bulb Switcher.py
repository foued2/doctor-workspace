class Solution:
    @staticmethod
    def bulbSwitch(n: int) -> int:
        # The bulb switch problem explanation:
        # Each bulb starts in the 'off' state (represented as 0).
        # We have n rounds. In the i-th round, we toggle every i-th bulb.
        # This means:
        # In the 1st round, every bulb is toggled.
        # In the 2nd round, every 2nd bulb is toggled.
        # In the 3rd round, every 3rd bulb is toggled, and so on...

        # A bulb ends up being 'on' if it is toggled an odd number of times.
        # This happens only for bulbs at positions which are perfect squares.
        # Example:
        # Bulb 1: toggled in round 1 (1 time) -> ON
        # Bulb 2: toggled in rounds 1 and 2 (2 times) -> OFF
        # Bulb 3: toggled in rounds 1 and 3 (2 times) -> OFF
        # Bulb 4: toggled in rounds 1, 2, and 4 (3 times) -> ON (4 is a perfect square)
        # More generally, a bulb at position k is toggled in round d if and only if d is a divisor of k.
        # Thus, counting the perfect square numbers will give the count of bulbs that are 'on'.

        # We can find the number of bulbs that are 'on' by counting the number of perfect squares <= n.
        # The integer part of sqrt(n) gives the count of these perfect squares.
        return int(n ** 0.5)


if __name__ == '__main__':
    # Example usage:
    # For n = 3, we have bulbs at positions 1, 2, 3.
    # Bulb 1 (perfect square) ends up being 'on'.
    # Bulb 2 and 3 are 'off'.
    # Hence, the result is 1.
    print(Solution.bulbSwitch(3))
