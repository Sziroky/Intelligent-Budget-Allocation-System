"""Deterministic budget allocation logic."""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from core.models.AllocationSummary import AllocationSummary
from core.models.CampaignAllocation import CampaignAllocation
from core.models.Campaign import RoasTrend
from core.models.CampaignProfile import CampaignProfile, SaturationGrade, StrategyAction
from core.models.FinalResult import FinalResult
from utils.indexes import calculate_hhi


# --- Core Allocation Logic ---

def _calculate_performance_score(profile: CampaignProfile) -> float:
    """
    Calculates a single, unified performance score for a campaign.
    This score combines raw performance, strategic priority, and trend momentum.
    """
    llm_priority = 1
    if profile.brief_mention and hasattr(profile.brief_mention, 'priority'):
        llm_priority = profile.brief_mention.priority

    # 1. Base Performance Score (Weights can be tuned)
    w_roas = 0.5
    w_cpa = 0.3
    w_saturation = 0.2
    
    # Use the raw audience_saturation_signal (float) from the profile
    saturation_value = profile.audience_saturation_signal

    base_performance = (
        (w_roas * (profile.roas_zscore or 0.0))
        - (w_cpa * (profile.cpa_zscore or 0.0))
        + (w_saturation * (1 - saturation_value))
    )

    # 2. LLM Priority Score (Strategic Multiplier)
    priority_multiplier = llm_priority

    # 3. Trend Multiplier (Risk/Momentum)
    trend_multiplier = 1.0
    if profile.roas_trend == RoasTrend.DECLINING:
        trend_multiplier = 0.8
    elif profile.roas_trend == RoasTrend.RISING:
        trend_multiplier = 1.2
    # else: flat trend is 1.0

    score = base_performance * priority_multiplier * trend_multiplier
    print(f"DEBUG: Score for {profile.campaign_id}: {score:.2f}") # DEBUG
    return score


def allocate_budget(
    profiles: List[CampaignProfile], total_budget: float
) -> FinalResult:
    """
    Allocates the total budget using a single performance score and a two-phase
    deficit/surplus balancing algorithm.
    """
    # --- Phase 1: Handle Deficit by Pausing Lowest Performers ---

    # Calculate performance score for each profile
    scored_profiles = [ (p, _calculate_performance_score(p)) for p in profiles ]

    # Tentatively allocate min_viable_spend to everyone
    tentative_allocations = {
        p.campaign_id: p.min_viable_spend for p, score in scored_profiles
    }
    
    current_budget_after_min_spend = sum(tentative_allocations.values())

    # Sort campaigns by score, worst to first, to decide who to cut if needed
    sorted_for_cutting = sorted(scored_profiles, key=lambda item: item[1])

    # NOTE: As discussed, this iterative pausing is a greedy algorithm. It's
    # transparent and effective, but might not be globally optimal. For instance,
    # pausing one expensive, low-scoring campaign might be better than pausing
    # two cheaper, even-lower-scoring campaigns. This is a known trade-off.
    for profile, score in sorted_for_cutting:
        if current_budget_after_min_spend <= total_budget:
            break

        # Pause the worst-performing campaigns one by one until the budget is balanced
        reclaimed_budget = tentative_allocations[profile.campaign_id]
        tentative_allocations[profile.campaign_id] = 0
        current_budget_after_min_spend -= reclaimed_budget

    # --- Phase 2: Distribute Surplus ---

    active_allocations = {
        cid: spend
        for cid, spend in tentative_allocations.items()
        if spend > 0
    }
    active_profiles = {
        p.campaign_id: (p, score)
        for p, score in scored_profiles
        if p.campaign_id in active_allocations
    }

    surplus = total_budget - sum(active_allocations.values())

    if surplus > 0:
        # Calculate the total score of only the active, non-capped, POSITIVE-scoring campaigns
        total_performance_score_for_surplus = sum(
            score
            for cid, (p, score) in active_profiles.items()
            if active_allocations[cid] < p.platform_level_budget_cap and score > 0
        )

        if total_performance_score_for_surplus > 0:
            for cid, (profile, score) in active_profiles.items():
                if score <= 0: # Only give surplus to positive-scoring campaigns
                    continue

                current_spend = active_allocations[cid]
                if current_spend >= profile.platform_level_budget_cap:
                    continue

                # Distribute surplus proportionally based on performance score
                share_of_surplus = (
                    score / total_performance_score_for_surplus
                ) * surplus
                potential_spend = current_spend + share_of_surplus

                # Enforce platform-level budget caps
                final_spend = min(potential_spend, profile.platform_level_budget_cap)
                active_allocations[cid] = final_spend

    # Re-sum and normalize to exactly match the total budget to handle any rounding errors
    # or leftover surplus from capped campaigns.
    final_allocations_raw = active_allocations
    total_allocated_raw = sum(final_allocations_raw.values())

    print(f"DEBUG: Total allocated before final normalization: {total_allocated_raw}")

    final_allocations: Dict[str, float] = {}
    if total_allocated_raw != total_budget and total_allocated_raw > 0:
        normalization_factor = total_budget / total_allocated_raw
        for cid in final_allocations_raw:
            final_allocations[cid] = final_allocations_raw[cid] * normalization_factor
    else:
        final_allocations = final_allocations_raw

    total_allocated_final = sum(final_allocations.values())
    print(f"DEBUG: Total allocated after final normalization: {total_allocated_final}")
    print(f"DEBUG: Final Allocations: {final_allocations}") # DEBUG

    # --- Phase 3: Finalization & Flagging ---

    final_campaign_allocations: List[CampaignAllocation] = []
    platform_spends: Dict[str, float] = {}

    # First pass to populate platform_spends and initial allocations
    for profile in profiles:
        recommended_spend = round(final_allocations.get(profile.campaign_id, 0.0))
        platform_spends[profile.platform] = (
            platform_spends.get(profile.platform, 0.0) + recommended_spend
        )

    # Second pass to create CampaignAllocation objects and add flags
    for profile in profiles:
        recommended_spend = round(final_allocations.get(profile.campaign_id, 0.0))
        delta = recommended_spend - int(profile.current_weekly_spend)

        # Determine final action based on delta
        action = StrategyAction.HOLD
        if recommended_spend == 0 and profile.current_weekly_spend > 0:
            action = StrategyAction.PAUSE
        elif delta > 50:  # Use a threshold to avoid minor fluctuations being 'SCALE'
            action = StrategyAction.SCALE
        elif delta < -50:  # Use a threshold to avoid minor fluctuations being 'REDUCE'
            action = StrategyAction.REDUCE

        # Calculate risk flags
        risk_flags = []
        if profile.roas_trend == RoasTrend.DECLINING:
            risk_flags.append("volatility")

        if 0 < recommended_spend < profile.min_viable_spend:
            risk_flags.append("below_min_spend")

        # Platform concentration flag (per campaign if its platform exceeds threshold)
        if (
            profile.platform
            and (platform_spends.get(profile.platform, 0.0) / total_budget) > 0.55
        ):
            risk_flags.append("platform_concentration")

        final_campaign_allocations.append(
            CampaignAllocation(
                campaign_id=profile.campaign_id,
                recommended_spend=recommended_spend,
                delta_vs_current=delta,
                action=action,
                opportunity_cost_note=(
                    f"Based on a performance score of {_calculate_performance_score(profile):.2f}, this campaign was prioritized."
                ),
                risk_flags=list(set(risk_flags)),  # Ensure unique flags
                rationale=profile.rationale or "No rationale provided.",
            )
        )
        print(f"DEBUG: Campaign {profile.campaign_id}: Recommended Spend = {recommended_spend}, Delta = {delta}, Flags = {risk_flags}")

    # Calculate HHI
    hhi_score = calculate_hhi(list(final_allocations.values()))

    # Construct final summary
    summary = AllocationSummary(
        concentration_score=round(hhi_score, 4),
        concentration_warning=hhi_score > 0.25,
        total_allocated=round(total_budget),
        unresolved_conflicts=list(set(
            conflict
            for p in profiles
            if p.conflicts_in_brief
            for conflict in p.conflicts_in_brief
        )),
    )

    return FinalResult(allocations=final_campaign_allocations, summary=summary)
