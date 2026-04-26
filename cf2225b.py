def alternating_string(s):
    n = len(s)
    count = 0
    for i, c in enumerate(s):
        if i % 2 == 0:
            if c != 'a':
                count += 1
        else:
            if c != 'b':
                count += 1
    return min(count, n - count)