"""Utility functions for calculating financial indexes and metrics."""

from typing import List

def calculate_hhi(values: List[float]) -> float:
    """
    Calculates the Herfindahl-Hirschman Index (HHI) for a list of values.

    The HHI is a common measure of market concentration and is calculated by
    squaring the market share of each firm in the industry and then summing
    them. Here, it will be used for spend concentration across campaigns or platforms.

    Args:
        values: A list of non-negative float values (e.g., campaign spends or shares).
                These values do not need to sum to 1, as the function will normalize them.

    Returns:
        The calculated HHI as a float, typically between 0 and 1 (or 0 and 10,000
        if percentages are used, but we'll use normalized shares).
    """
    if not values:
        return 0.0

    total = sum(values)
    if total == 0:
        return 0.0

    # Calculate shares and then square and sum them
    hhi = sum((v / total) ** 2 for v in values)
    return hhi
