"""The metadata of the created allocation"""

from typing import List, Optional

from pydantic import BaseModel


class AllocationSummary(BaseModel):
    """Summary of the allocation plan."""

    concentration_score: float  # HHI
    concentration_warning: bool
    alternative_diversified_allocation: Optional[List[dict]] = (
        None  # If warned, alternative allocations
    )
    total_allocated: int
    unresolved_conflicts: List[str]
