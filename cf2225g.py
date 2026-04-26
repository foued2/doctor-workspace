def solve_case(n, ks):
    if 1 in ks:
        return list(range(n))
    
    for k in ks:
        classes = []
        for r in range(k):
            cls = list(range(r, n, k))
            if cls:
                classes.append(cls)
        
        if len(classes) == 1:
            return classes[0]
        
        for flip_first in [False, True]:
            oriented = []
            if flip_first:
                oriented.append(classes[0][::-1])
            else:
                oriented.append(classes[0][:])
            
            valid = True
            for i in range(1, len(classes)):
                prev_last = oriented[-1][-1]
                fwd_first = classes[i][0]
                rev_first = classes[i][-1]
                
                fwd_ok = any(abs(fwd_first - prev_last) % ki == 0 for ki in ks)
                rev_ok = any(abs(rev_first - prev_last) % ki == 0 for ki in ks)
                
                if fwd_ok:
                    oriented.append(classes[i][:])
                elif rev_ok:
                    oriented.append(classes[i][::-1])
                else:
                    valid = False
                    break
            
            if valid:
                result = []
                for cls in oriented:
                    result.extend(cls)
                ok = True
                for i in range(len(result) - 1):
                    diff = abs(result[i+1] - result[i])
                    if not any(diff % ki == 0 for ki in ks):
                        ok = False
                        break
                if ok:
                    return result
    
    return -1

def solve():
    t = int(input())
    for _ in range(t):
        n, m = map(int, input().split())
        ks = list(map(int, input().split()))
        result = solve_case(n, ks)
        if result == -1:
            print(-1)
        else:
            print(*result)

if __name__ == "__main__":
    solve()