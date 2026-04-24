import os
from pathlib import Path
from typing import List

import yaml
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field

from core.models.Campaign import Campaign
from core.models.CampaignProfile import StrategyAction
from core.models.CampaignsProfile import CampaignsStatistics

load_dotenv()


class CampaignAnalysisSchema(BaseModel):
    campaign_id: str = Field(
        description="The unique identifier of the campaign being analyzed."
    )
    is_mentioned: bool = Field(
        description="True if the campaign is mentioned in the brief (explicitly by name or implicitly by platform/type)."
    )
    quote: str | None = Field(
        description="The specific sentence or phrase from the brief that applies to this campaign."
    )
    semantic_analysis: str | None = Field(
        description="A brief explanation of how the campaign's attributes match the brief's intent."
    )
    conflicts_in_brief: List[str] = Field(
        default_factory=list,
        description="List of specific rules from the brief that this campaign violates (e.g., 'CPA > $50').",
    )
    recommended_action: StrategyAction = Field(
        description="The strategic action to take: scale, hold, reduce, or pause."
    )
    rationale: str = Field(
        description="A detailed explanation of why the action was chosen, citing both statistics and specific instructions from the brief."
    )


class AnalysisResponseSchema(BaseModel):
    analyses: List[CampaignAnalysisSchema] = Field(
        description="A collection of structured analyses for the provided campaigns."
    )


class Gemini:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-2.0-flash"

        # Load prompts from YAML
        prompt_path = Path(__file__).parent / "prompts.yaml"
        with open(prompt_path, "r") as f:
            self.prompts = yaml.safe_load(f)

    def analyze_campaigns(
        self, campaigns: List[Campaign], brief: str
    ) -> AnalysisResponseSchema:
        """
        Analyzes each campaign against the strategy brief.
        """
        campaign_data = [c.model_dump() for c in campaigns]
        prompt = self.prompts["analyze_campaigns"].format(
            brief=brief, campaigns=campaign_data
        )

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": AnalysisResponseSchema,
            },
        )

        return response.parsed

    def generate_strategy(self, stats: CampaignsStatistics, brief: str) -> str:
        """
        Generates a high-level strategy overview based on aggregate statistics and the brief.
        """
        prompt = self.prompts["generate_strategy"].format(
            brief=brief, stats=stats.model_dump()
        )

        response = self.client.models.generate_content(
            model=self.model_id, contents=prompt
        )
        return response.text

    def simple_ask(self, text: str) -> str:
        """
        A simple helper to ask a text-based question and get a string response.
        """
        response = self.client.models.generate_content(
            model=self.model_id, contents=text
        )
        return response.text
