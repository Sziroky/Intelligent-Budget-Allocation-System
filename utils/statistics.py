"""Utilities for statistics calculation."""


def calc_average(data):
    """Calculate the average of a list of numbers."""
    if not data:
        return 0
    return sum(data) / len(data)


def calc_standard_deviation(data):
    """Calculate the standard deviation of a list of numbers."""
    if len(data) < 2:
        return 0
    avg = calc_average(data)
    variance = sum((x - avg) ** 2 for x in data) / len(data)
    return variance**0.5


def calc_zscore(value: float, avg: float, std: float) -> float:
    """Calculate the z-score for a given value."""
    if std == 0:
        return 0.0
    return (value - avg) / std
