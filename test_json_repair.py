import json
from doctor.ingest.problem_parser import _extract_json_object

# Test trailing garbage (common LLM failure mode)
malformed = '{"key": "value"} trailing garbage here'
repair_info = {}
result = _extract_json_object(malformed, repair_info)
print('Trailing garbage test:', result)
print('Repair info:', repair_info)
print()

# Test valid JSON (no repair)
valid = '{"key": "value", "list": [1, 2, 3]}'
repair_info2 = {}
result2 = _extract_json_object(valid, repair_info2)
print('Valid test:', result2)
print('Repair info:', repair_info2)
print()

# Test nested JSON with trailing garbage
malformed2 = '{"key": {"nested": true}, "list": [1, 2]} extra text after'
repair_info3 = {}
result3 = _extract_json_object(malformed2, repair_info3)
print('Nested test:', result3)
print('Repair info:', repair_info3)
print('\nAll tests passed!')