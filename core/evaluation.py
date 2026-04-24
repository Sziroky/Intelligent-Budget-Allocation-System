"""The evaluation harness for scoring the budget allocation system."""

from typing import Dict, List, Set

from pydantic import BaseModel, Field

from core.models.Campaign import Campaign
from core.models.CampaignAllocation import CampaignAllocation
from core.models.FinalResult import FinalResult


# --- Data Models for Loading Ground Truth ---
class GroundTruthOutput(BaseModel):
    action: str
    target_spend: int
    expected_risk_flags: List[str] = Field(default_factory=list)


class EvalCase(BaseModel):
    eval_case_id: str
    description: str
    total_budget: int
    input_campaigns: List[Campaign]
    ground_truth_output: Dict[str, GroundTruthOutput]


# --- Scoring Logic ---
class EvaluationScores(BaseModel):
    budget_constraint_passed: bool
    allocation_accuracy: float  # Percentage of campaigns within ±10%
    action_agreement: float  # Percentage of correct actions
    risk_flag_recall: float  # Average recall across all campaigns


def score_allocation(
    generated_result: FinalResult, ground_truth: EvalCase
) -> EvaluationScores:
    """
    Scores a generated allocation plan against a ground-truth evaluation case.
    """
    # 1. Budget Constraint Score - If its 85 000
    budget_constraint_passed = (
        generated_result.summary.total_allocated == ground_truth.total_budget
    )

    # Prepare for other scores
    num_campaigns_in_ground_truth = len(ground_truth.ground_truth_output)
    if num_campaigns_in_ground_truth == 0:
        return EvaluationScores(
            budget_constraint_passed=budget_constraint_passed,
            allocation_accuracy=1.0,
            action_agreement=1.0,
            risk_flag_recall=1.0,
        )

    allocation_correct_count = 0
    action_correct_count = 0
    total_recall_score = 0.0

    # Create a map for easy lookup of generated allocations by campaign_id
    generated_allocations_map: Dict[str, CampaignAllocation] = {
        alloc.campaign_id: alloc for alloc in generated_result.allocations
    }

    # 2. Per-Campaign Scores (Accuracy, Agreement, Recall)
    for campaign_id, truth_data in ground_truth.ground_truth_output.items():
        if campaign_id not in generated_allocations_map:
            # If a campaign from ground truth is missing in generated, it's a failure
            # This implicitly reduces allocation accuracy, action agreement, and recall
            continue

        generated_data = generated_allocations_map[campaign_id]

        # Allocation Accuracy (within ±10% tolerance)
        # Note: If target_spend is 0, only 0 is correct.
        if truth_data.target_spend == 0:
            if generated_data.recommended_spend == 0:
                allocation_correct_count += 1
        else:
            spend_lower_bound = truth_data.target_spend * 0.9
            spend_upper_bound = truth_data.target_spend * 1.1
            if (
                spend_lower_bound
                <= generated_data.recommended_spend
                <= spend_upper_bound
            ):
                allocation_correct_count += 1

        # Action Agreement
        if generated_data.action.value == truth_data.action:
            action_correct_count += 1

        # Risk Flag Recall
        generated_flags: Set[str] = set(generated_data.risk_flags)
        truth_flags: Set[str] = set(truth_data.expected_risk_flags)

        true_positives = len(generated_flags.intersection(truth_flags))

        if not truth_flags:
            # If there are no ground truth flags, perfect recall if no flags were generated
            recall = 1.0 if not generated_flags else 0.0
        else:
            recall = true_positives / len(truth_flags)

        total_recall_score += recall

    # 3. Final Score Calculation
    return EvaluationScores(
        budget_constraint_passed=budget_constraint_passed,
        allocation_accuracy=(allocation_correct_count / num_campaigns_in_ground_truth)
        if num_campaigns_in_ground_truth > 0
        else 0.0,
        action_agreement=(action_correct_count / num_campaigns_in_ground_truth)
        if num_campaigns_in_ground_truth > 0
        else 0.0,
        risk_flag_recall=(total_recall_score / num_campaigns_in_ground_truth)
        if num_campaigns_in_ground_truth > 0
        else 0.0,
    )
