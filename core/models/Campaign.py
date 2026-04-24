"""Campaign informations loaded from campaigns.json

This module contains the data model for the campaign.
It will ensure the data are corectly formatted.
Mainly will be used to generate new data.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


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

    model_config = ConfigDict(populate_by_name=True)

    campaign_id: str
    platform: Platform
    campaign_type: Optional[CampaignType] = None
    current_weekly_spend: float
    roas: float
    four_week_roas_trend: RoasTrend = Field(alias="4_week_roas_trend")
    cpa: Optional[float] = None
    conversion_volume: Optional[float] = None
    audience_saturation_signal: float
    platform_level_budget_cap: float
    min_viable_spend: float
