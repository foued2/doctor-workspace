import json

with open('doctor/registry/problem_registry.json') as f:
    registry = json.load(f)

with open('doctor/registry/new_problems.json') as f:
    new_problems = json.load(f)

for pid, problem in new_problems.items():
    registry[pid] = problem
    print(f"Added: {pid}")

registry['registry_version'] = registry.get('registry_version', '1.0')

with open('doctor/registry/problem_registry.json', 'w') as f:
    json.dump(registry, f, indent=2)

print(f"\nTotal problems: {len([k for k in registry.keys() if k not in ('registry_version', 'registry_notes')])}")