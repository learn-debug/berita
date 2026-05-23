def compute_credibility(
    fact_accuracy: float = 0.0,
    narrative_consistency: float = 0.0,
    conflict_resolution: float = 0.0,
    source_quality: float = 0.0,
) -> float:
    score = (
        0.40 * fact_accuracy
        + 0.25 * narrative_consistency
        + 0.20 * conflict_resolution
        + 0.15 * source_quality
    )
    return round(max(0.0, min(1.0, score)), 2)


def routing(score: float) -> str:
    if score >= 0.75:
        return "auto-publish"
    if score >= 0.50:
        return "editor-review"
    return "full-revision"
