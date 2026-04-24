"""Main data models for the budget allocation system."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from pydantic import BaseModel

from core.models.Campaign import Campaign


class CampaignsData(BaseModel):
    """Model for the input JSON data from campaigns.json."""

    total_weekly_budget: float
    campaigns: List[Campaign]

    @classmethod
    def from_json(cls, path: str | Path) -> "CampaignsData":
        """Load a CampaignsData instance from a campaigns.json file."""
        path = Path(path)
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.model_validate(data)
