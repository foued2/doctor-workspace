from collections import defaultdict


class Solution:
    @staticmethod
    def passwordDerivation(keylog) -> int:
        # Step 1: Construct the graph
        graph = defaultdict(set)  # Create a defaultdict to represent the graph
        in_degree = defaultdict(int)  # Create a defaultdict to track in-degrees of nodes
        for attempt in keylog:
            for i in range(len(attempt)):
                a = attempt[i]
                # Add edges for all digits appearing after a
                for j in range(i + 1, len(attempt)):
                    b = attempt[j]
                    if b not in graph[a]:
                        graph[a].add(b)  # Add edge from a to b
                        in_degree[b] += 1  # Increment in-degree of b

        # Step 2: Perform topological sorting
        result = []  # List to store the sorted digits
        queue = [digit for digit in graph if in_degree[digit] == 0]  # Initialize queue with nodes having in-degree 0
        while queue:
            curr_digit = queue.pop(0)  # Pop the node with in-degree 0 from queue
            result.append(curr_digit)  # Add node to result
            for neighbor in graph[curr_digit]:  # Iterate over neighbors of the current node
                in_degree[neighbor] -= 1  # Decrement in-degree of neighbor
                if in_degree[neighbor] == 0:  # If in-degree becomes 0
                    queue.append(neighbor)  # Add neighbor to queue

        # Step 3: Concatenate the sorted digits to form the passcode
        passcode = ''.join(result)

        return int(passcode)


if __name__ == "__main__":
    # Example keylog
    keylog = [
        "319", "680", "180", "690", "129", "620", "762", "689", "762", "318",
        "368", "710", "720", "710", "629", "168", "160", "689", "716", "731",
        "736", "729", "316", "729", "729", "710", "769", "290", "719", "680",
        "318", "389", "162", "289", "162", "718", "729", "319", "790", "680",
        "890", "362", "319", "760", "316", "729", "380", "319", "728", "716"
    ]
    solution = Solution.passwordDerivation(keylog)
    print(solution)
