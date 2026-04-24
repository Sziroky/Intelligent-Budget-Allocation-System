"""Campaign informations loaded from campaigns.json

This module contains the data model for the campaign.
It will ensure the data are corectly formatted.
Mainly will be used to generate new data.
"""

from enum import Enum
from typing import List

from pydantic import BaseModel


class CampaignType(str, Enum):
    """Enum for the type of campaign."""

    BRAND = "brand"
    PROSPECTING = "prospecting"
    RETARGETING = "retargeting"


class Platform(str, Enum):
    """Advertisments Platform"""

    GOOGLE = "Google"
    META = "Meta"
    TIKTOK = "TikTok"


class RoasTrend(str, Enum):
    """Enum for the trend of ROAS."""

    RISING = "rising"
    DECLINING = "declining"
    FLAT = "flat"


class Campaign(BaseModel):
    """The Single Campaign Model."""

    campaign_id: str
    platform: Platform
    campaign_type: CampaignType
    current_weekly_spend: float
    roas: float
    four_weeks_roas_trend: RoasTrend
    cpa: float
    conversion_volume: float
    audience_saturation_signal: float
    platform_level_budget_cap: float
    min_viable_spend: float


class Campaigns(BaseModel):
    """The Campaigns Model"""

    total_weekly_budget: float
    campaigns: List[Campaign]
