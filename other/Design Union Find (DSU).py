class UnionFind:
    def __init__(self, n):
        # Initialize the Union-Find data structure with 'n' elements
        self.parent = list(range(n))  # Initially, each element is its own parent

    def find(self, x):
        # Find the root parent of element 'x' with path compression
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # Path compression
        return self.parent[x]

    def union(self, x, y):
        # Union operation: merge the sets containing elements 'x' and 'y'
        root_x = self.find(x)
        root_y = self.find(y)
        if root_x != root_y:
            self.parent[root_x] = root_y


# Example usage:
n = 5
uf = UnionFind(n)

uf.union(1, 2)  # Merge sets containing elements 1 and 2
uf.union(3, 4)  # Merge sets containing elements 3 and 4

print(uf.find(1))  # Output: 2 (the root parent of element 1)
print(uf.find(3))  # Output: 4 (the root parent of element 3)
