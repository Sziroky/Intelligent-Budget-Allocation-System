"""Utilities for statistics calculation."""


def calc_average(data):
    if not data:
        return 0
    return sum(data) / len(data)


def calc_standard_deviation(data):
    if len(data) < 2:
        return 0
    avg = calc_average(data)
    variance = sum((x - avg) ** 2 for x in data) / len(data)
    return variance**0.5
