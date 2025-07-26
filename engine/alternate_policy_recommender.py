from utils.plan_matcher import (
    match_plans_with_coverage,
    show_top_unique_plans,
    enrich_with_benefits,
)

def recommend_alternatives(
    user_age: int,
    user_state: str,
    plan_df,
    rate_df,
    benefits_df,
    base_coverage: float,
    original_plan_type: str = None,
    tolerance_pct: float = 25,
    top_n: int = 5
):
    """
    Suggests alternative plans with relaxed matching (e.g., wider tolerance)
    """
    print("🔄 Recommending alternate policies...")

    # Try broader plan types if needed
    plan_type_to_try = None if original_plan_type == "Any" else original_plan_type

    # Match again with relaxed tolerance
    matched = match_plans_with_coverage(
        age=user_age,
        state_code=user_state,
        target_coverage=base_coverage,
        plan_df=plan_df,
        rate_df=rate_df,
        plan_type=plan_type_to_try,
        tolerance_pct=tolerance_pct
    )

    if matched.empty:
        return []

    top = show_top_unique_plans(matched, top_n=top_n)
    enriched = enrich_with_benefits(top, benefits_df)

    suggestions = []
    for plan in enriched.itertuples():
        suggestions.append({
            "PlanId": plan.PlanId,
            "Name": plan.PlanMarketingName,
            "Type": plan.PlanType,
            "Rate": plan.IndividualRate,
            "PredictedCoverage": plan.PredictedCoverage,
            "Benefits": plan.CoveredBenefits
        })

    return suggestions
