"""Scoring and bucketing logic for campaigns."""

from typing import List

from core.models.CampaignProfile import CampaignProfile, Grades, SaturationGrade
from core.models.Campaigns import CampaignsData
from core.models.CampaignsProfile import CampaignsStatistics
from utils.statistics import calc_average, calc_standard_deviation, calc_zscore


def map_zscore(z_score: float, inverse: bool = False) -> Grades:
    """
    Maps Z-score value into descriptive value.

    ARGS:
    - z_score: The Z-score to be mapped.
    - inverse: If True, higher Z-scores will be mapped to lower grades f.e CPA z-score - lower is better
    """
    # Logical inversion
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
    roas_values = [campaign.roas for campaign in campaigns.campaigns]
    cpa_values = [campaign.cpa for campaign in campaigns.campaigns]

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
            campaign.roas, statistics.average_roas, statistics.std_roas
        )
        cpa_z = calc_zscore(campaign.cpa, statistics.average_cpa, statistics.std_cpa)

        profile = CampaignProfile(
            campaign_id=campaign.campaign_id,
            platform=campaign.platform,
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


if __name__ == "__main__":
    pass
