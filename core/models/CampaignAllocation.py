"""The result of the deterministic + LLM insights allocation system."""

from enum import Enum
from typing import List

from pydantic import BaseModel


class Action(str, Enum):
    SCALE = "scale"
    HOLD = "hold"
    REDUCE = "reduce"
    PAUSE = "pause"


class RiskFlag(str, Enum):
    VOLATILITY = "volatility"
    PLATFORM_CONCENTRATION = "platform_concentration"
    BELOW_MIN_SPEND = "below_min_spend"


class CampaignAllocation(BaseModel):
    """Allocation details for a single campaign."""

    campaign_id: str
    recommended_spend: int
    delta_vs_current: int
    action: Action
    opportunity_cost_note: str
    risk_flags: List[RiskFlag]
    rationale: str
