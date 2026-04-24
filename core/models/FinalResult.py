"""Main JSON object that will be returned."""

from typing import List

from pydantic import BaseModel

from .AllocationSummary import AllocationSummary
from .CampaignAllocation import CampaignAllocation


class FinalResult(BaseModel):
    """The complete output of the budget allocation system."""

    allocations: List[CampaignAllocation]
    summary: AllocationSummary
