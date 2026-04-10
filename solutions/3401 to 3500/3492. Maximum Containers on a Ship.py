class Solution:
    @staticmethod
    def maxContainers(n: int, w: int, maxWeight: int) -> int:
        # Calculate maximum containers based on space
        space_limit = n * n

        # Calculate maximum containers based on weight
        weight_limit = maxWeight // w

        # Return the stricter limit
        return min(space_limit, weight_limit)

if __name__ == "__main__":
    print(Solution.maxContainers(n = 2, w = 3, maxWeight = 15))
    print(Solution.maxContainers(n = 3, w = 5, maxWeight = 20))
