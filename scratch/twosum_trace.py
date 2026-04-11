"""Trace L1 analysis for Two_Sum_partial."""
import sys
sys.path.insert(0, r'F:\pythonProject')

from tests.verify_code_only_baseline import SOLUTIONS
from doctor.code_analyzer import CodeAnalyzer

sol = SOLUTIONS['Two Sum::partial']
problem = sol['problem']
code = sol['code']

analyzer = CodeAnalyzer()
result = analyzer.analyze(problem, code, 'two_sum')

print(f"verdict: {result.verdict}")
print(f"confidence: {result.confidence}")
print(f"failures: {result.failures}")
print(f"details: {result.details}")
print(f"fatal_flags: {result.fatal_flags}")
print(f"reasoning: {result.reasoning}")
