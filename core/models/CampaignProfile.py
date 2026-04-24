"""Insights from the campaign data and brief - will be used before the allocation decision is made."""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class StrategyAction(str, Enum):
    """Enum for the recommended action on a campaign."""

    SCALE = "scale"
    HOLD = "hold"
    REDUCE = "reduce"
    PAUSE = "pause"


class BriefMention(BaseModel):
    """Information about how the campaign is mentioned in the strategy brief."""

    is_mentioned: bool
    quote: Optional[str] = None
    semantic_analysis: Optional[str] = None


class CampaignProfile(BaseModel):
    """Extended profile of a campaign with evaluation and strategy decision."""

    campaign_id: str
    # Evaluation metrics
    roas_rank: int  # 1-12, 1 being best
    cpa_rank: int  # 1-12, 1 being best (lowest CPA)
    is_top_3_roas: bool
    is_bottom_3_roas: bool
    # Brief analysis
    brief_mention: BriefMention
    conflicts_in_brief: List[str] = []  # List of conflicting instructions
    # AI decision
    recommended_action: StrategyAction
    rationale: str
