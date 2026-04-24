"""The metadata of the created allocation"""

from __future__ import annotations
from typing import List, Optional

from pydantic import BaseModel

from core.models.CampaignAllocation import CampaignAllocation


class AllocationSummary(BaseModel):
    """Summary of the allocation plan."""

    concentration_score: float  # HHI
    concentration_warning: bool
    alternative_diversified_allocation: Optional[List[CampaignAllocation]] = (
        None  # If warned, alternative allocations
    )
    total_allocated: int
    unresolved_conflicts: List[str]
