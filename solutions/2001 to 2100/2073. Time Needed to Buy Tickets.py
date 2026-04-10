from typing import List


class Solution:
    @staticmethod
    def timeRequiredToBuy(tickets: List[int], target_position: int) -> int:
        current_position = target_position
        result = 0
        queue = list(tickets)

        # Loop until the person at the target position buys all their tickets
        while queue[current_position] > 0:
            # Process the current person
            current_tickets = queue.pop(0)
            if current_position == -1:
                current_position = len(queue)
            if current_tickets > 0:
                # Increment the result as the person buys a ticket
                result += 1
                # If the person has more tickets, enqueue them back to the queue
                queue.append(current_tickets - 1)
            else:
                # If the person has no more tickets, enqueue 0
                queue.append(0)
            # Move to the next person in the queue
            current_position -= 1

        # Return the total time required for the person at the target position to buy all their tickets
        return result


if __name__ == '__main__':
    print(Solution.timeRequiredToBuy([2, 3, 2], 2))
    print(Solution.timeRequiredToBuy([5, 1, 1, 1], 0))
