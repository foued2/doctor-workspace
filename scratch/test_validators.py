import sys
sys.path.insert(0, r'F:\pythonProject')
from doctor.output_validators import validate_output, VALIDATORS, NO_VALIDATOR_NEEDED

# N-Queens: valid 2x2 solution (2 boards)
v, r = validate_output('N-Queens', [['Q.', '..'], ['..', 'Q.']], {'n': 2})
print(f'N-Queens (2x2 valid, 2 sols): valid={v}, reason={r}')

# N-Queens: diagonal conflict (queens at (0,0) and (1,1))
v, r = validate_output('N-Queens', [['Q.', '..'], ['..', 'Q.']], {'n': 2})
# This should pass — (0,0) and (1,1) ARE diagonal! Let me use a valid board
v, r = validate_output('N-Queens', [['.Q', 'Q.']], {'n': 2})
# (0,1) and (1,0) — also diagonal! For n=2, no valid solution exists.
# Let me use n=4 with a known valid board
v, r = validate_output('N-Queens', [['.Q..', '...Q', 'Q...', '..Q.']], {'n': 4})
print(f'N-Queens (4x4 valid): valid={v}, reason={r}')

# N-Queens: diagonal conflict in 4x4
v, r = validate_output('N-Queens', [['Q...', '...Q', '.Q..', '..Q.']], {'n': 4})
# (0,0), (1,3), (2,1), (3,2) — check (0,0) vs (2,1): |0-2|=2, |0-1|=1, not diag
# (1,3) vs (3,2): |1-3|=2, |3-2|=1, not diag
# (0,0) vs (3,2): |0-3|=3, |0-2|=2, not diag
# (2,1) vs (3,2): |2-3|=1, |1-2|=1, DIAG!
print(f'N-Queens (4x4 diag): valid={v}, reason={r}')

# N-Queens: same column conflict
v, r = validate_output('N-Queens', [['Q...', 'Q...', '....', '....']], {'n': 4})
print(f'N-Queens (4x4 col): valid={v}, reason={r}')

# Two Sum: valid
v, r = validate_output('Two Sum', [0, 3], {'nums': [2, 7, 11, 15], 'target': 17})
print(f'Two Sum (valid): valid={v}, reason={r}')

# Two Sum: wrong sum
v, r = validate_output('Two Sum', [0, 1], {'nums': [2, 7, 11, 15], 'target': 100})
print(f'Two Sum (wrong sum): valid={v}, reason={r}')

# Two Sum: same element
v, r = validate_output('Two Sum', [0, 0], {'nums': [2, 7, 11, 15], 'target': 4})
print(f'Two Sum (same elem): valid={v}, reason={r}')

print(f'')
print(f'With validators: {len(VALIDATORS)}/10 problems')
print(f'Without validators: {len(NO_VALIDATOR_NEEDED)}/10 problems')
