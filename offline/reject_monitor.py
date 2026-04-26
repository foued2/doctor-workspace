#!/usr/bin/env python3
"""
Doctor Monitoring - Batch Metrics

Item 8: Reject rate monitoring
- compute_batch_metrics()
- Tracks reject_rate and reject_rate_trend per batch
"""
from typing import Any, List


def compute_batch_metrics(results: List[dict], history: List[float] = None) -> dict:
    """
    Compute batch-level metrics.
    
    Args:
        results: List of decision results with "status" field
        history: Optional list of previous reject rates (for trend calculation)
    
    Returns:
        {
            "reject_rate": float,
            "reject_rate_trend": float,
            "alert": bool,
            "alert_reason": str | None
        }
    """
    if history is None:
        history = []
    
    total = len(results)
    if total == 0:
        return {
            "reject_rate": 0.0,
            "reject_rate_trend": 0.0,
            "alert": False,
            "alert_reason": None
        }
    
    rejected = sum(1 for r in results if r.get("status") == "rejected")
    reject_rate = rejected / total
    
    recent_history = history[-4:] + [reject_rate]
    reject_rate_trend = sum(recent_history) / len(recent_history)
    
    alert = False
    alert_reason = None
    if reject_rate > 0.40:
        alert = True
        alert_reason = f"reject_rate {reject_rate:.1%} exceeds 40% threshold"
    elif reject_rate < 0.10:
        alert = True
        alert_reason = f"reject_rate {reject_rate:.1%} below 10% threshold"
    
    return {
        "reject_rate": reject_rate,
        "reject_rate_trend": reject_rate_trend,
        "alert": alert,
        "alert_reason": alert_reason
    }


if __name__ == "__main__":
    import json
    test_results = [
        {"status": "rejected"},
        {"status": "rejected"},
        {"status": "success"},
        {"status": "rejected"},
        {"status": "success"},
    ]
    metrics = compute_batch_metrics(test_results, [0.3, 0.5])
    print(json.dumps(metrics, indent=2))