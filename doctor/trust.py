"""
Risk computation — verification-grounded belief assessment.

Risk = uncalibrated belief × lack of verification.
High risk does not mean wrong — it means unverified.
"""


def compute_risk(ai_confidence: float, evidence_strength: float) -> dict:
    """
    Risk = uncalibrated belief × lack of verification.
    High risk does not mean wrong — it means unverified.
    """
    risk = round(ai_confidence * (1 - evidence_strength), 3)
    flagged = ai_confidence >= 0.9 and evidence_strength < 0.4
    return {
        "risk": risk,
        "flagged": flagged,
    }
