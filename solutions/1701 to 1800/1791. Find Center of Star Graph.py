from typing import List


class Solution:
    @staticmethod
    def findCenter(edges: List[List[int]]) -> int:
        # Check if the first vertex of the first edge is the same as either
        # the first or the second vertex of the second edge.
        if edges[0][0] == edges[1][0] or edges[0][0] == edges[1][1]:
            return edges[0][0]  # Return the common vertex if found

        # If the above condition is not met, return the second vertex of the first edge
        return edges[0][1]  # This vertex is assumed to be the center vertex


print(Solution.findCenter(edges=[[1, 2], [5, 1], [1, 3], [1, 4]]))

from typing import List


class Solution:
    @staticmethod
    def findCenter(edges: List[List[int]]) -> int:
        """
        Graph, Adjacent list, Center
        """
        # If edges list is empty, return -1 (assuming -1 represents no center found)
        if not edges:
            return -1

        # Dictionary to store the degree of each vertex
        degree = {}

        # Iterate through each edge in the edges list
        for edge in edges:
            u, v = edge[0], edge[1]

            # Increment the degree of vertex u
            if u in degree:
                degree[u] += 1
            else:
                degree[u] = 1

            # Increment the degree of vertex v
            if v in degree:
                degree[v] += 1
            else:
                degree[v] = 1

        # Total number of vertices in the graph
        n = len(degree)

        # Iterate through the degree dictionary to find the vertex with degree n-1
        for node, count in degree.items():
            if count == n - 1:
                return node  # Return the vertex which has degree n-1 (center vertex)

        return -1  # Return -1 if no center vertex is found (edge case)


# Example usage:
edges = [[1, 2], [2, 3], [4, 2], [3, 4]]
sol = Solution()
print(sol.findCenter(edges))  # Output: 2
