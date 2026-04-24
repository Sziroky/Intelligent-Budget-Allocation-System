"""Insights from the campaign data and brief - will be used before the allocation decision is made."""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class StrategyAction(str, Enum):
    """Enum for the recommended action on a campaign."""

    SCALE = "scale"
    HOLD = "hold"
    REDUCE = "reduce"
    PAUSE = "pause"


class Grades(str, Enum):
    """Buckets for grades (ROAS, CPA, etc.)."""

    LOW = "low"
    RELATIVELY_LOW = "relatively_low"
    MEDIUM = "medium"
    RELATIVELY_HIGH = "relatively_high"
    HIGH = "high"


class SaturationGrade(str, Enum):
    """Grades for audience saturation signal (0-1)."""

    FRESH = "fresh"  # 0.0 - 0.25
    BARELY_KNOWN = "barely_known"  # 0.25 - 0.5
    REGULAR_KNOWN = "regular_known"  # 0.5 - 0.75
    WELL_KNOWN = "well_known"  # 0.75 - 1.0
    FATIGUE = "fatigue"  # > 1.0 (though max should be 1.0)


class BriefMention(BaseModel):
    """Information about how the campaign is mentioned in the strategy brief."""

    is_mentioned: bool
    quote: Optional[str] = None
    semantic_analysis: Optional[str] = None


class CampaignProfile(BaseModel):
    """Extended profile of a campaign with evaluation and strategy decision.

    This model holds only computed insights and LLM decisions,
    not raw campaign data (which exists in Campaign).
    """

    campaign_id: str = Field(description="Reference to the campaign")
    platform: Optional[str] = Field(
        description="Advertising platform - TikTok, Meta, Google"
    )
    # Original Campaign Data needed for allocation
    min_viable_spend: float = Field(
        description="Minimum spend required for the campaign to be viable."
    )
    platform_level_budget_cap: float = Field(
        description="Maximum budget that can be allocated to this campaign's platform."
    )
    current_weekly_spend: float = Field(
        description="Current weekly spend of the campaign."
    )
    # Campaign Statistic and z-scores
    roas_zscore: Optional[float] = Field(description="Z-score for ROAS")
    cpa_zscore: Optional[float] = Field(description="Z-score for CPA")
    roas_trend: Optional[str] = Field(description="Trend of ROAS over 4 weeks")
    saturation_signal_grade: SaturationGrade = Field(
        description="Audience saturation grade"
    )
    # Graded roas and cpa
    roas_grade: Grades = Field(
        description="ROAS bucketed as low/rel. low/medium/rel. high/high"
    )
    cpa_grade: Grades = Field(
        description="CPA bucketed as low/rel. low/medium/rel. high/high (lower is better)"
    )
    # Brief analysis (filled by LLM)
    brief_mention: Optional[BriefMention] = None
    conflicts_in_brief: List[str] = Field(default_factory=list)

    # AI decision (filled by LLM)
    recommended_action: Optional[StrategyAction] = None
    rationale: Optional[str] = None

    @field_validator("cpa_grade")
    @classmethod
    def validate_cpa_bucket(cls, v: Grades) -> Grades:
        """Validate that cpa_bucket is set."""
        if v is None:
            raise ValueError("CPA bucket must be set")
        return v
