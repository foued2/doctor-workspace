from typing import List


class Solution:
    @staticmethod
    def findJudge(n: int, trust: List[List[int]]) -> int:
        # Special case for only one person (self-trusted)
        if n == 1:
            return 1

        # Initialize the trust map with 0 for all persons from 1 to n
        trust_map = {i: 0 for i in range(1, n + 1)}

        # Process the trust pairs
        for a, b in trust:
            # If 'a' trusts someone, mark 'a' as -1 (cannot be the judge)
            trust_map[a] = -1
            # If b is not marked as -1, increment trust count for b
            if trust_map[b] != -1:
                trust_map[b] += 1

        # Check for the person trusted by n-1 people and does not trust anyone
        for person in range(1, n + 1):
            if trust_map[person] == n - 1:
                return person

        # If no judge is found, return -1
        return -1


# Example usage
solution = Solution()
print(solution.findJudge(2, [[1, 2]]))  # Output: 2
print(solution.findJudge(3, [[1, 3], [2, 3]]))  # Output: 3
print(solution.findJudge(3, [[1, 3], [2, 3], [3, 1]]))  # Output: -1
print(solution.findJudge(4, [[1, 3], [2, 3], [4, 3]]))  # Output: 3


class Solution:
    @staticmethod
    def findJudge(n: int, trust: List[List[int]]) -> int:
        """
        Graph theory
        """
        # Initialize arrays to keep track of in-degrees and out-degrees
        in_degree = [0] * (n + 1)
        out_degree = [0] * (n + 1)

        # Populate the in-degree and out-degree arrays based on trust pairs
        for a, b in trust:
            out_degree[a] += 1  # a trusts b, so increase out-degree of a
            in_degree[b] += 1  # b is trusted by a so increase in-degree of b

        # Iterate over each person to find the judge
        for i in range(1, n + 1):
            # The judge should be trusted by n-1 people and should trust no one
            if in_degree[i] == n - 1 and out_degree[i] == 0:
                return i

        # If no judge is found, return -1
        return -1


# Example usage
solution = Solution()
print(solution.findJudge(2, [[1, 2]]))  # Output: 2
print(solution.findJudge(3, [[1, 3], [2, 3]]))  # Output: 3
print(solution.findJudge(3, [[1, 3], [2, 3], [3, 1]]))  # Output: -1
print(solution.findJudge(4, [[1, 3], [2, 3], [4, 3]]))  # Output: 3
