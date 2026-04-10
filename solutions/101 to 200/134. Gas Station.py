from typing import List


class Solution:
    @staticmethod
    def canCompleteCircuit(gas: List[int], cost: List[int]) -> int:
        total_gas = 0
        total_cost = 0
        tank = 0
        start_station = 0

        for i in range(len(gas)):
            total_gas += gas[i]
            total_cost += cost[i]
            tank += gas[i] - cost[i]

            # If tank becomes negative, reset starting station to next station
            if tank < 0:
                start_station = i + 1
                tank = 0

        # If total gas is less than total cost, it's impossible to complete the circuit
        if total_gas < total_cost:
            return -1
        else:
            return start_station


# Test cases
print(Solution.canCompleteCircuit(gas=[5, 8, 2, 8], cost=[6, 5, 6, 6]))  # Output: 3
print(Solution.canCompleteCircuit(gas=[5, 1, 2, 3, 4], cost=[4, 4, 1, 5, 1]))  # Output: 4
