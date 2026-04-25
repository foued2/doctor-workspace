import json

with open('phase3_batch3_results.json') as f:
    results = json.load(f)

with open('phase3_batch3.json') as f:
    cases = {c['user_id']: c for c in json.load(f)}

for r in results:
    uid = r['user_id']
    case = cases.get(uid, {})
    r['expected_match'] = case.get('expected_match')
    r['expected_type'] = case.get('expected_type')
    r['note'] = case.get('note', '')

with open('phase3_batch3_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("Updated expected values. Final tally:")

def is_correct(expected, got):
    if expected is None:
        return got is None or got == "no match"
    return expected == got

pass_count = sum(1 for r in results if is_correct(r['expected_match'], r['matched']))
fail_count = len(results) - pass_count

for r in results:
    expected = r['expected_match']
    got = r['matched']
    status = "PASS" if is_correct(expected, got) else "FAIL"
    print(f"  {status} {r['user_id']}: expected={expected}, got={got}")

print(f"\nTotal: {pass_count}/{len(results)} pass, {fail_count}/{len(results)} fail")