"""Creating profiles for each campaign based on statistics and LLM insights.

The key concept here is to translate raw campaign data into profiles describing the campaign.
"""

from typing import List

from core.llms.GoogleLLM import AnalysisResponseSchema
from core.models.CampaignProfile import (
    BriefMention,
    CampaignProfile,
    Grades,
    SaturationGrade,
)
from core.models.Campaigns import CampaignsData
from core.models.CampaignsProfile import CampaignsStatistics
from utils.statistics import calc_average, calc_standard_deviation, calc_zscore


def map_zscore(z_score: float, inverse: bool = False) -> Grades:
    """
    Maps Z-score value into descriptive value.
    The z score normalize the values because the information of ROAS being high or not is ambigous and relative to other campaigns.

    ARGS:
    - z_score: The Z-score to be mapped.
    - inverse: If True, higher Z-scores will be mapped to lower grades f.e CPA z-score - lower is better
    """
    # Logical inversion if you want high values to be considered worse.
    val = -z_score if inverse else z_score

    if val >= 1.5:
        return Grades.HIGH
    elif val >= 0.5:
        return Grades.RELATIVELY_HIGH
    elif val >= -0.5:
        return Grades.MEDIUM
    elif val >= -1.5:
        return Grades.RELATIVELY_LOW
    else:
        return Grades.LOW


def saturation_to_grade(signal: float) -> SaturationGrade:
    """
    Converts saturation signal (0-1) into a descriptivegrade.
    """
    if signal <= 0.25:
        return SaturationGrade.FRESH
    elif signal <= 0.50:
        return SaturationGrade.BARELY_KNOWN
    elif signal <= 0.75:
        return SaturationGrade.REGULAR_KNOWN
    elif signal <= 1.0:
        return SaturationGrade.WELL_KNOWN
    else:
        # Obsługa przypadku, gdy sygnał przekroczy 1.0
        return SaturationGrade.FATIGUE


def create_campaigns_statistics(campaigns: CampaignsData) -> CampaignsStatistics:
    # Create List out of ROAS and CPA stored in CampaignsData
    roas_values = [campaign.roas or 0.0 for campaign in campaigns.campaigns]
    cpa_values = [campaign.cpa or 0.0 for campaign in campaigns.campaigns]

    return CampaignsStatistics(
        total_campaigns=len(campaigns.campaigns),
        average_roas=calc_average(roas_values),
        average_cpa=calc_average(cpa_values),
        std_roas=calc_standard_deviation(roas_values),
        std_cpa=calc_standard_deviation(cpa_values),
    )


def create_campaign_profiles(
    campaigns: CampaignsData, statistics: CampaignsStatistics
) -> List[CampaignProfile]:
    profiles = []
    for campaign in campaigns.campaigns:
        roas_z = calc_zscore(
            campaign.roas or 0.0, statistics.average_roas, statistics.std_roas
        )
        cpa_z = calc_zscore(
            campaign.cpa or 0.0, statistics.average_cpa, statistics.std_cpa
        )

        profile = CampaignProfile(
            campaign_id=campaign.campaign_id,
            platform=campaign.platform,
            min_viable_spend=campaign.min_viable_spend,
            platform_level_budget_cap=campaign.platform_level_budget_cap,
            current_weekly_spend=campaign.current_weekly_spend,
            audience_saturation_signal=campaign.audience_saturation_signal,
            roas_zscore=round(roas_z, 2),
            cpa_zscore=round(cpa_z, 2),
            roas_trend=campaign.four_week_roas_trend.value,
            saturation_signal_grade=saturation_to_grade(
                campaign.audience_saturation_signal
            ),
            roas_grade=map_zscore(roas_z, inverse=False),
            cpa_grade=map_zscore(cpa_z, inverse=True),
            # Pola dla LLM zostają puste
            conflicts_in_brief=[],
        )
        profiles.append(profile)

    return profiles


def enrich_profiles_with_llm_insights(
    profiles: List[CampaignProfile], analysis_results: AnalysisResponseSchema
) -> List[CampaignProfile]:
    """
    Integrates the LLM's analysis into the existing campaign profiles.
    """
    profile_map = {profile.campaign_id: profile for profile in profiles}
    for analysis in analysis_results.analyses:
        if analysis.campaign_id in profile_map:
            profile = profile_map[analysis.campaign_id]
            profile.brief_mention = BriefMention(
                is_mentioned=analysis.is_mentioned,
                quote=analysis.quote,
                semantic_analysis=analysis.semantic_analysis,
                priority=analysis.priority,
            )
            profile.conflicts_in_brief = analysis.conflicts_in_brief
            profile.recommended_action = analysis.recommended_action
            profile.rationale = analysis.rationale
    return list(profile_map.values())


if __name__ == "__main__":
    pass
