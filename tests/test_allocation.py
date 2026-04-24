import pprint
from typing import List

from core.allocate import allocate_budget
from core.models.Campaign import RoasTrend  # Corrected import path
from core.models.CampaignProfile import (
    BriefMention,
    CampaignProfile,
    Grades,  # Import Grades enum
    SaturationGrade,
    StrategyAction,
)
from core.models.FinalResult import FinalResult


def test_budget_allocation_logic_with_dummy_data():
    print("Starting budget allocation logic test with dummy data...")
    total_budget = 85000.0

    # 1. Prepare dummy CampaignProfile data (simulating LLM output and initial profiling)
    # Ensure all fields required by allocate_budget and _calculate_performance_score are present
    dummy_profiles: List[CampaignProfile] = [
        # Campaign 1: High priority, rising ROAS, low CPA, high min spend (TikTok Prospecting)
        CampaignProfile(
            campaign_id="tiktok_prospecting_alpha",
            platform="TikTok",
            min_viable_spend=10000.0,
            platform_level_budget_cap=30000.0,
            current_weekly_spend=5000.0,
            roas_zscore=1.5,
            cpa_zscore=-0.8,
            roas_trend=RoasTrend.RISING,
            saturation_signal_grade=SaturationGrade.FRESH,
            roas_grade=Grades.HIGH,  # Added valid grade
            cpa_grade=Grades.RELATIVELY_HIGH,  # Added valid grade
            brief_mention=BriefMention(
                is_mentioned=True,
                quote="heavily scale up our TikTok prospecting campaigns",
                semantic_analysis="Strategic priority for Q4 growth.",
                priority=10,
            ),
            conflicts_in_brief=[],
            recommended_action=StrategyAction.SCALE,
            rationale="Strategic priority, rising trend, low saturation.",
        ),
        # Campaign 2: Mid priority, high ROAS, declining trend, high CPA (Meta Prospecting)
        CampaignProfile(
            campaign_id="meta_prospecting_bravo",
            platform="Meta",
            min_viable_spend=8000.0,
            platform_level_budget_cap=50000.0,
            current_weekly_spend=12000.0,
            roas_zscore=1.2,
            cpa_zscore=0.5,
            roas_trend=RoasTrend.DECLINING,
            saturation_signal_grade=SaturationGrade.WELL_KNOWN,
            roas_grade=Grades.HIGH,  # Added valid grade
            cpa_grade=Grades.MEDIUM,  # Added valid grade
            brief_mention=BriefMention(
                is_mentioned=True,
                quote="Focus spend strictly on what's working",
                semantic_analysis="High ROAS, but declining trend. Opportunity cost.",
                priority=7,
            ),
            conflicts_in_brief=["Declining trend for high ROAS campaign"],
            recommended_action=StrategyAction.HOLD,
            rationale="Hold due to declining trend despite high ROAS.",
        ),
        # Campaign 3: Low priority, low ROAS, high CPA, below min spend (Google Display)
        CampaignProfile(
            campaign_id="google_display_charlie",
            platform="Google",
            min_viable_spend=4000.0,
            platform_level_budget_cap=40000.0,
            current_weekly_spend=1000.0,
            roas_zscore=-1.0,
            cpa_zscore=1.8,
            roas_trend=RoasTrend.FLAT,
            saturation_signal_grade=SaturationGrade.REGULAR_KNOWN,
            roas_grade=Grades.LOW,  # Added valid grade
            cpa_grade=Grades.LOW,  # Added valid grade
            brief_mention=BriefMention(is_mentioned=False, priority=2),
            conflicts_in_brief=["CPA over $50", "Below minimum viable spend"],
            recommended_action=StrategyAction.PAUSE,
            rationale="Poor performance, high CPA, and not meeting min viable spend.",
        ),
        # Campaign 4: Medium priority, good ROAS, flat trend, moderate CPA (Meta Retargeting)
        CampaignProfile(
            campaign_id="meta_retargeting_delta",
            platform="Meta",
            min_viable_spend=6000.0,
            platform_level_budget_cap=50000.0,
            current_weekly_spend=7000.0,
            roas_zscore=0.8,
            cpa_zscore=-0.2,
            roas_trend=RoasTrend.FLAT,
            saturation_signal_grade=SaturationGrade.BARELY_KNOWN,
            roas_grade=Grades.RELATIVELY_HIGH,  # Added valid grade
            cpa_grade=Grades.RELATIVELY_HIGH,  # Added valid grade
            brief_mention=BriefMention(is_mentioned=False, priority=5),
            conflicts_in_brief=[],
            recommended_action=StrategyAction.HOLD,
            rationale="Stable performance, good efficiency.",
        ),
        # Campaign 5: Low priority, good ROAS, flat trend, moderate CPA, very low min spend (Meta)
        CampaignProfile(
            campaign_id="meta_brand_echo",
            platform="Meta",
            min_viable_spend=1000.0,
            platform_level_budget_cap=50000.0,
            current_weekly_spend=2000.0,
            roas_zscore=0.6,
            cpa_zscore=-0.1,
            roas_trend=RoasTrend.FLAT,
            saturation_signal_grade=SaturationGrade.FRESH,
            roas_grade=Grades.MEDIUM,  # Added valid grade
            cpa_grade=Grades.MEDIUM,  # Added valid grade
            brief_mention=BriefMention(is_mentioned=False, priority=3),
            conflicts_in_brief=[],
            recommended_action=StrategyAction.HOLD,
            rationale="Stable performance, good efficiency.",
        ),
    ]

    # 2. Allocate Budget
    final_allocation_result: FinalResult = allocate_budget(dummy_profiles, total_budget)
    print("✅ Budget allocated successfully.")

    # 3. Verification & Output
    print("\n--- Final Allocation Result (Dummy Data) ---")
    pprint.pprint(final_allocation_result.model_dump())
    print(f"\nTotal Allocated: {final_allocation_result.summary.total_allocated}")
    assert final_allocation_result.summary.total_allocated == total_budget
    print("✅ Total budget constraint satisfied.")


if __name__ == "__main__":
    test_budget_allocation_logic_with_dummy_data()
