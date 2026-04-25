import json

with open('phase3_batch2_rerun_results.json') as f:
    results = json.load(f)

for r in results:
    if r.get('user_id') in ('user_17', 'user_18', 'user_19', 'user_20'):
        if r.get('error') == 'Rate limit exceeded after 5 retries':
            r['failure_tag'] = 'rate_limit'
            r['status'] = 'rate_limited'

with open('phase3_batch2_rerun_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("Updated tags for users 17-20: rate_limit")
for r in results:
    print(f"  {r['user_id']}: {r['failure_tag']}")