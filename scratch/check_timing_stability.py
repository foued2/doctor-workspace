"""Investigate timing stability across workload sizes."""
from doctor.s_measurement import measure_multi_run

workloads = [1000, 10000, 100000, 1000000]
print("Workload size vs timing stability:")
print(f"{'size':>10} {'median_ms':>12} {'cv':>8} {'status':>10}")
print("-" * 45)

for size in workloads:
    m = measure_multi_run(lambda x: sum(range(x)), (size,), n_runs=20)
    m.input_size = size
    print(f"{size:>10} {m.median_ms:>12.4f} {m.cv:>8.4f} {m.status:>10}")
