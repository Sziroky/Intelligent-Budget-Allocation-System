"""Unit tests for profiling module - pytest tutorials & best practices."""

import pytest

from core.models.Campaign import Campaign, Platform, RoasTrend
from core.models.CampaignProfile import Grades, SaturationGrade
from core.models.Campaigns import CampaignsData
from core.profiling import (
    create_campaigns_statistics,
    map_zscore,
    saturation_to_grade,
)


def test_map_zscore():
    """Test of mapping Z-score to Grades enum"""
    expected = Grades.HIGH
    assert map_zscore(1.6) == expected


def test_saturation_to_grade():
    """Test of mapping saturation signal to SaturationGrade enum"""
    expected = SaturationGrade.FRESH
    assert saturation_to_grade(0.2) == expected


@pytest.fixture
def sample_campaign_1():
    """
    Fixture for a sample campaign.
    """
    return Campaign(
        campaign_id="campaign_001",
        platform=Platform.TIKTOK,
        current_weekly_spend=5000.0,
        roas=2.5,
        **{"4_week_roas_trend": RoasTrend.RISING},
        cpa=15.0,
        audience_saturation_signal=0.2,
        platform_level_budget_cap=30000.0,
        min_viable_spend=10000.0,
    )


@pytest.fixture
def sample_campaign_2():
    """Fixture for a second sample campaign."""
    return Campaign(
        campaign_id="campaign_002",
        platform=Platform.META,
        current_weekly_spend=3000.0,
        roas=1.2,
        **{"4_week_roas_trend": RoasTrend.DECLINING},
        cpa=35.0,
        audience_saturation_signal=0.7,
        platform_level_budget_cap=50000.0,
        min_viable_spend=8000.0,
    )


@pytest.fixture
def sample_campaign_3():
    """Fixture for a third sample campaign."""
    return Campaign(
        campaign_id="campaign_003",
        platform=Platform.GOOGLE,
        current_weekly_spend=1000.0,
        roas=0.8,
        **{"4_week_roas_trend": RoasTrend.FLAT},
        cpa=50.0,
        audience_saturation_signal=0.5,
        platform_level_budget_cap=20000.0,
        min_viable_spend=5000.0,
    )


@pytest.fixture
def sample_campaigns_data(sample_campaign_1, sample_campaign_2, sample_campaign_3):
    """
    Fixture for campaigns data containing 3 sample campaigns (fixtures above).
    """
    return CampaignsData(
        total_weekly_budget=85000.0,
        campaigns=[sample_campaign_1, sample_campaign_2, sample_campaign_3],
    )


class TestCreateCampaignsStatistics:
    """Statistics tests for create_campaigns_statistics function"""

    def test_creates_correct_number_of_campaigns(self, sample_campaigns_data):
        """
        TEST: Count the campaigns in dataset
        ARRANGE: sample_campaigns_data - 3 campaigns
        ACT: create_campaigns_statistics()
        ASSERT: total_campaigns == 3
        """
        stats = create_campaigns_statistics(sample_campaigns_data)
        assert stats.total_campaigns == 3


class TestCreateCampaignProfiles:
    pass


class TestLLMInsights:
    pass
