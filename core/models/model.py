"""Main data models for the budget allocation system."""

from typing import List

from pydantic import BaseModel

from .Campaign import Campaign


class CampaignData(BaseModel):
    """Model for the input JSON data from campaigns.json."""

    total_weekly_budget: float
    campaigns: List[Campaign]
