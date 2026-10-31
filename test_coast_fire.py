"""Pytest suite for the five documented coast_fire numbers.

Every assertion uses ``abs(x - y) < 1`` so the suite stays tolerant of
floating-point noise without hiding a real modelling error.
"""

from coast_fire import capital_today, health_bridge, target, years_to_target


def test_target_at_120k_spend():
    assert abs(target(120000) - 2374800) < 1


def test_target_at_100k_spend():
    assert abs(target(100000) - 1874800) < 1


def test_health_bridge_750_month_from_40():
    assert abs(health_bridge(750, 40) - 126846) < 1


def test_capital_today_3571200_at_40():
    assert abs(capital_today(3571200, 40) - 1650437) < 1


def test_years_to_target_100k_plus_3k_month():
    assert abs(years_to_target(100000, 3000, 2374800) - 27.2) < 1
