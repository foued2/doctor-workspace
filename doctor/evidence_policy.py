def classify_evidence(pass_ratio, has_error):
    """
    Rule-based classification of execution evidence state.

    No scoring. No weighting. No probabilistic interpretation.
    """

    if has_error:
        if pass_ratio == 0:
            return "catastrophic_failure"
        else:
            return "partial_with_errors"

    if pass_ratio == 1.0:
        return "fully_verified"

    if pass_ratio >= 0.5:
        return "partially_verified"

    return "weakly_verified"
