"""The result of the deterministic + LLM insights allocation system."""

from typing import List, Optional

from pydantic import BaseModel, Field

from core.models.CampaignProfile import StrategyAction


class CampaignAllocation(BaseModel):
    """Allocation details for a single campaign."""

    campaign_id: str
    recommended_spend: int
    delta_vs_current: int
    action: StrategyAction
    opportunity_cost_note: str
    risk_flags: List[str] = Field(default_factory=list)
    rationale: str
