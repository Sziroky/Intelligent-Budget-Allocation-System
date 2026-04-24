"""The entry point of the system. This module is the key orchestrator.

Usage:
    To run the main orchestration:
        python main.py
    To run the orchestrator with evaluation harness:
        python main.py --evaluate
"""

import argparse
import json
import pprint
from pathlib import Path
from typing import List

from core.allocate import allocate_budget
from core.evaluation import EvalCase, score_allocation
from core.llms.GoogleLLM import Gemini
from core.models import CampaignsData
from core.models.FinalResult import FinalResult
from core.profiling import (
    create_campaign_profiles,
    create_campaigns_statistics,
    enrich_profiles_with_llm_insights,
)


def _verify_total_budget(final_result: FinalResult, expected_total_budget: float):
    """
    Verifies that the total allocated budget in the FinalResult exactly matches the expected total budget.
    Raises an AssertionError if they do not match.
    """
    actual_total = final_result.summary.total_allocated
    if actual_total != expected_total_budget:
        raise AssertionError(
            f"Total allocated budget mismatch! Expected {expected_total_budget}, got {actual_total}"
        )
    print(f"✅ Total budget constraint satisfied: {actual_total}")


def orchestrate(data_path: str | Path = "data/campaigns.json") -> FinalResult:
    """Main orchestration function that runs the entire pipeline.

    The flow of this function is as follows:
    1. Load the campagn data and parse it into objects.
    2. Create initial campaign data profiles using statistics (z-scores) and descriptive categories (for LLM).
    3. Send the initial profiles into LLM and ask to analyze the strategy brief based on that fill the LLM-origin fields in the profiles (priorities, rationale, strategy).
    4. Based on the statistical and LLM insights we will allocate the budget but deterministically not stochastically.
    5. We Create a list of Campaings that are not paused.
    6. We sort the list based on pririties assigned by the LLM.
    7. We allocate the minimum spend of each campagn and check if not exceed 85,000 budget.
    8. If we are we drop the last campaign and check the rest (Not ideal and not preffered approach)
    9. We then have a list of campaigns and their budget allocations.
    10. We calculate how much part of the 85 grant we give to each campaign.
        Formula:
        ((Weight ROAS z-score) - (Weight CPA z-score) + (Weight * (1 - Saturation))) * (LLM Priority) * (ROAS Trend Multiplier)
    11. Evaluation of the final result allocation

    Args:
        data_path (str | Path): Path to the input campaign data JSON file.

    Returns:
        FinalResult: The final budget allocation result.
    """
    # 1. Load Data
    campaigns_data = CampaignsData.from_json(data_path)
    print("✅ Loaded campaign data successfully.")

    brief_path = Path("data/strategy_brief.txt")
    brief = brief_path.read_text()
    print("✅ Loaded strategy brief.")

    # 2. Create Profiles
    stats = create_campaigns_statistics(campaigns_data)
    profiles = create_campaign_profiles(campaigns_data, stats)
    print("✅ Generated initial campaign profiles. This may take a while...")

    # 3. Analyze with LLM
    gemini = Gemini()
    analysis_results = gemini.analyze_campaigns(campaigns_data.campaigns, brief)
    print("✅ Received analysis from LLM.")

    # 4. Integrate LLM Insights
    profiles = enrich_profiles_with_llm_insights(profiles, analysis_results)
    print(
        "✅ Integration of LLM insights into campaign profiles. (strategy brief; priorities, rationalle)"
    )

    # 5. Allocate Budget - Deterministic approach
    total_budget = campaigns_data.total_weekly_budget
    final_allocation = allocate_budget(profiles, total_budget)
    print("✅ Budget allocated succesfully")

    # Perform final budget verification
    _verify_total_budget(final_allocation, total_budget)

    if _verify_total_budget:
        print("✅ Final budget verification passed.")
    else:
        print(
            "❌ Final budget verification failed. There could be a call back but the way it is is not possible."
        )

    return final_allocation


def run_harness():
    """Runs the evaluation harness against historical cases."""
    print("--- Starting Evaluation Harness ---")

    eval_cases_path = Path("data/historical_eval_cases.json")
    eval_cases_data = json.loads(eval_cases_path.read_text())
    eval_cases: List[EvalCase] = [EvalCase(**case) for case in eval_cases_data]
    print(f"✅ Loaded {len(eval_cases)} evaluation cases.")

    temp_campaigns_path = Path("data/temp_eval_campaigns.json")
    passed_cases = 0

    for i, case in enumerate(eval_cases):
        print(f"--- Running Eval Case {i + 1}: {case.eval_case_id} ---")

        case_input_data = CampaignsData(
            total_weekly_budget=case.total_budget, campaigns=case.input_campaigns
        )
        temp_campaigns_path.write_text(case_input_data.model_dump_json(indent=2))

        try:
            generated_result = orchestrate(data_path=temp_campaigns_path)
            scores = score_allocation(generated_result, case)

            print("--- 📊 Scores ---")
            pprint.pprint(scores.model_dump())

            if all(
                [
                    scores.budget_constraint_passed,
                    scores.allocation_accuracy == 1.0,
                    scores.action_agreement == 1.0,
                    scores.risk_flag_recall == 1.0,
                ]
            ):
                print("✅ Case Passed")
                passed_cases += 1
            else:
                print("❌ Case Failed")

        except Exception as e:
            print(f"🚨 An error occurred during orchestration for this case: {e}")
            print("❌ Case Failed")

    if temp_campaigns_path.exists():
        temp_campaigns_path.unlink()

    print("--- 🏆 Evaluation Summary ---")
    print(f"Passed {passed_cases} out of {len(eval_cases)} cases.")
    if passed_cases >= 2:
        print("✅ Minimum bar passed (≥ 2 of 3 cases passed).")
    else:
        print("❌ Minimum bar failed (< 2 of 3 cases passed).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the budget allocation system.")
    parser.add_argument(
        "--evaluate",
        action="store_true",
        help="Run the evaluation harness against historical data.",
    )
    args = parser.parse_args()

    if args.evaluate:
        run_harness()
    else:
        final_result = orchestrate()
        print("--- Final Allocation Plan ---")
        pprint.pprint(final_result.model_dump())

        print("--- ✅ Orchestration Complete ---")
