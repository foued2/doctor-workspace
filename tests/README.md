# Tests Directory

Contains test suites for algorithm solutions.

## Running Tests

### All tests
\`\`\`bash
python -m pytest tests/ -v
\`\`\`

### Specific range
\`\`\`bash
python -m pytest tests/test_001_100.py -v
\`\`\`

### With coverage
\`\`\`bash
python -m pytest tests/ --cov=. --cov-report=html
\`\`\`

If the project virtual environment is not activated, run the same commands with
`.\venv\Scripts\python.exe -m pytest ...` instead.

## Writing Tests

Use descriptive test names and multiple assertions. See conftest.py for fixtures.

Example:
\`\`\`python
def test_problem_<number>_<title>():
    """Test <Title> (LeetCode #<number>)"""
    from YOUR_SOLUTION_PATH import SolutionClass
    solution = SolutionClass()
    assert solution.method(input1) == expected_output
\`\`\`
