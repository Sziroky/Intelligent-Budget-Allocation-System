"""Model for campaign statististics and profiles."""

from pydantic import BaseModel, Field


class CampaignsStatistics(BaseModel):
    """Statistics for a set of campaigns."""

    total_campaigns: int = Field(description="Total number of campaigns")
    average_roas: float = Field(description="Average ROAS across campaigns")
    average_cpa: float = Field(description="Average CPA across campaigns")
    std_roas: float = Field(description="Standard deviation of ROAS")
    std_cpa: float = Field(description="Standard deviation of CPA")
