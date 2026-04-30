#!/usr/bin/env python3
"""
Benchmark schema classifier against ground truth labels.
Compares predicted domain, paradigm, dp_type with manual labels.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from doctor.schema_classifier import classify_schema

def benchmark():
    # Load ground truth
    f1 = open(r"F:\pythonProject1\scratch\all_labels.json", "r")
    data = json.load(f1)
    f1.close()
    ground_truth = data["labels"]
    
    # Load problem statements
    f2 = open(r"F:\pythonProject1\doctor\registry\problem_registry.json", "r")
    registry = json.load(f2)
    f2.close()
    
    field_scores = {}
    for field in ["domain", "paradigm", "dp_type"]:
        field_scores[field] = {"correct": 0, "total": 0}
    
    results = []
    
    print("Benchmarking %d problems..." % len(ground_truth))
    
    for pid, label_data in ground_truth.items():
        if pid not in registry:
            continue
        
        statement = registry[pid].get("spec", {}).get("description", "")
        if not statement:
            continue
        
        # Get prediction
        pred = classify_schema(statement)
        
        # Get ground truth
        gt = label_data["schema"]
        
        # Compare each field
        for field in ["domain", "paradigm", "dp_type"]:
            pred_val = pred.get(field, "")
            gt_val = gt.get(field, "")
            
            # Skip empty ground truth
            if not gt_val:
                continue
            
            field_scores[field]["total"] += 1
            if pred_val == gt_val:
                field_scores[field]["correct"] += 1
            
            results.append({
                "problem_id": pid,
                "field": field,
                "predicted": pred_val,
                "ground_truth": gt_val,
                "correct": pred_val == gt_val
            })
    
    # Calculate scores
    print("\nResults:")
    for field, scores in field_scores.items():
        if scores["total"] == 0:
            print("  %s: N/A (no ground truth)" % field)
        else:
            accuracy = 100 * scores["correct"] / scores["total"]
            print("  %s: %d/%d (%.1f%%)" % (field, scores["correct"], scores["total"], accuracy))
    
    total_correct = sum(s["correct"] for s in field_scores.values())
    total_fields = sum(s["total"] for s in field_scores.values())
    if total_fields > 0:
        overall = 100 * total_correct / total_fields
        print("\nOverall: %d/%d (%.1f%%)" % (total_correct, total_fields, overall))
    
    # Save results
    output = {
        "field_scores": field_scores,
        "overall_correct": total_correct,
        "overall_total": total_fields,
        "overall_accuracy": total_correct / total_fields if total_fields > 0 else 0,
        "results": results
    }
    
    output_path = Path("scratch/schema_benchmark_results.json")
    f3 = open(output_path, "w")
    json.dump(output, f3, indent=2, ensure_ascii=False)
    f3.close()
    
    print("\nResults saved to: %s" % output_path)
    return output


if __name__ == "__main__":
    benchmark()
