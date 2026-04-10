class Solution:
    @staticmethod
    def numJewelsInStones(jewels: str, stones: str) -> int:
        ans = 0  # Initialize a counter for the number of jewels

        # Iterate through each stone in the collection
        for stone in stones:
            # Check if the current stone is a jewel
            if stone in jewels:
                ans += 1  # Increment the counter if the stone is a jewel

        # Return the total count of jewels in the stones
        return ans


if __name__ == '__main__':
    print(Solution.numJewelsInStones(jewels="aA", stones="aAAbbbb"))
