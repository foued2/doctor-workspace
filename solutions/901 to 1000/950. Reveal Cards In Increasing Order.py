from typing import List


class Solution:
    @staticmethod
    def deckRevealedIncreasing(deck: List[int]) -> List[int]:
        n = len(deck)
        if n <= 2:
            return sorted(deck)

        # Sort the deck in ascending order
        deck.sort()

        # Initialize an empty list to represent the final result
        result = [0] * n

        # Initialize a queue to store indices of cards
        queue = list(range(n))

        # Iterate through the sorted deck
        for card in deck:
            # Add the current card to the result at the next available index
            result[queue.pop(0)] = card

            # Move the next available index to the end of the result list
            if queue:
                queue.append(queue.pop(0))

        return result


if __name__ == '__main__':
    print(Solution.deckRevealedIncreasing(deck=[17, 13, 11, 2, 3, 5, 7]))
