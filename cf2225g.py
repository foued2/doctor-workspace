"""
Codeforces 2225G - Simple Problem
Given 0..n-1, arrange so |adjacent| is divisible by at least one k in given list.
"""
from collections import defaultdict
import sys


def solve_case(n, ks):
    # If any k=1, trivially works 
    if 1 in ks:
        return list(range(n))
    
    # Check: can we connect residue classes?
    # Build connected components via residues
    parent = list(range(n))
    
    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]
    
    def union(x, y):
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py
    
    # Connect all valid difference pairs
    for i in range(n):
        for j in range(i + 1, n):
            diff = j - i
            if any(diff % k == 0 for k in ks):
                union(i, j)
    
    # Check if all in one component
    roots = set(find(i) for i in range(n))
    if len(roots) > 1:
        # Need to try constructing by residue class chains
        pass
    
    # More rigorous: build chains by residue classes and try to merge
    chains = []
    for k in ks:
        for r in range(k):
            chain = [x for x in range(r, n, k)]
            if chain:
                chains.append(chain)
    
    # Sort chains by length for better merging
    chains.sort(key=lambda x: -len(x))
    
    # Try to build valid sequence
    result = []
    used = [False] * n
    
    # Greedy merge: try to attach chains where last->first is valid
    used_chains = []
    while len(chains) > len(used_chains):
        attached = False
        for i, chain in enumerate(chains):
            if i in used_chains:
                continue
            
            # Try to find a valid insertion point
            if not result:
                result = chain
                used_chains.append(i)
                for x in chain:
                    used[x] = True
                attached = True
                break
            
            # Try appending at end
            if not used[chain[0]]:
                # Check if last of result connects to first of chain
                diff = abs(result[-1] - chain[0])
                if any(diff % k == 0 for k in ks):
                    # Valid, append
                    for x in chain:
                        if not used[x]:
                            result.append(x)
                            used[x] = True
                    used_chains.append(i)
                    attached = True
                    break
            
            # Try inserting at start
            if not used[chain[-1]]:
                diff = abs(chain[-1] - result[0])
                if any(diff % k == 0 for k in ks):
                    # Insert at start
                    new_result = []
                    for x in chain:
                        if not used[x]:
                            new_result.append(x)
                    new_result.extend(result)
                    for x in chain:
                        if not used[x]:
                            used[x] = True
                    result = new_result
                    used_chains.append(i)
                    attached = True
                    break
        
        if not attached:
            break
    
    if len(result) == n:
        return result
    
    # Try simpler direct approach: connect consecutive numbers by any k
    result = []
    used = [False] * n
    
    # Sort numbers by residue (this gives local chains)
    by_residue = defaultdict(list)
    for k in ks:
        for r in range(k):
            for x in range(r, n, k):
                by_residue[k, r].append(x)
    
    # Try each k as primary order
    for k in ks:
        result = []
        used = [False] * n
        for r in range(k):
            for x in by_residue[k, r]:
                if not used[x]:
                    result.append(x)
                    used[x] = True
        
        if len(result) == n:
            # Validate
            valid = True
            for i in range(n - 1):
                diff = abs(result[i+1] - result[i])
                if not any(diff % k == 0 for k in ks):
                    valid = False
                    break
            if valid:
                return result
    
    return -1


def solve():
    t = int(input())
    outputs = []
    
    for _ in range(t):
        n, m = map(int, input().split())
        ks = list(map(int, input().split()))
        
        result = solve_case(n, ks)
        if result == -1 or len(result) != n:
            outputs.append([-1])
        else:
            outputs.append(result)
    
    for out in outputs:
        print(' '.join(map(str, out)))


if __name__ == "__main__":
    solve()
