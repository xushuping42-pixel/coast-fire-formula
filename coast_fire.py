"""Coast/Fat FIRE math with a Social-Security offset and separate pre-Medicare health costs.

Stdlib only, zero third-party dependencies. Every function is a pure function of
its arguments, so each number is reproducible and auditable.
"""

import math

__all__ = [
    "target",
    "annuity_factor",
    "health_bridge",
    "capital_today",
    "years_to_target",
]


def target(annual_spend: float, swr: float = 0.04, ss_annual: float = 25008) -> float:
    """FIRE portfolio target after subtracting Social Security.

    The portfolio only has to fund the slice of spending that Social Security
    does not cover, so the withdrawal rate is applied to
    ``annual_spend - ss_annual`` rather than to the full spend.

    Args:
        annual_spend: Desired annual spending in today's dollars.
        swr: Safe withdrawal rate, e.g. ``0.04`` for the 4% rule.
        ss_annual: Annual Social Security benefit in today's dollars
            (SSA June 2026 snapshot: ``25008``).

    Returns:
        The portfolio value needed, in today's dollars.
    """
    return (annual_spend - ss_annual) / swr


def annuity_factor(r: float, n: float) -> float:
    """Present-value factor of an ordinary annuity paying 1 per year for ``n`` years.

    Computes ``sum_{k=1..n} (1 + r) ** -k`` in closed form, i.e.
    ``(1 - (1 + r) ** -n) / r``.

    Args:
        r: Annual discount rate as a decimal, e.g. ``0.05``.
        n: Number of annual payments (fractional values are allowed).

    Returns:
        Present value of one unit per year received for ``n`` years.
        Returns ``n`` when ``r == 0``.
    """
    if r == 0:
        return float(n)
    return (1.0 - (1.0 + r) ** (-n)) / r


def health_bridge(
    monthly_health: float,
    retire_age: float,
    medicare_age: float = 65,
    r: float = 0.05,
) -> float:
    """Discounted cost of health insurance from retirement until Medicare.

    One single discounting segment: the annual premium (``12 * monthly_health``)
    is discounted as an ordinary annuity over ``medicare_age - retire_age``
    years. The result is **not** multiplied by 25 — it is the present value of
    the bridge itself, not a perpetual withdrawal-rate target.

    Args:
        monthly_health: Monthly health-insurance premium before Medicare.
        retire_age: Age at retirement.
        medicare_age: Age Medicare starts (default 65).
        r: Annual discount rate as a decimal (default 5%).

    Returns:
        Present value of the pre-Medicare premiums, in today's dollars.
        Returns ``0.0`` when ``retire_age >= medicare_age`` (no bridge).
    """
    years = medicare_age - retire_age
    if years <= 0:
        return 0.0
    return monthly_health * 12.0 * annuity_factor(r, years)


def capital_today(
    target_amount: float,
    age: float,
    target_age: float = 67,
    real: float = 0.029,
) -> float:
    """Lump sum needed today so it compounds to ``target_amount`` by ``target_age``.

    Discounts the future target at the real (inflation-adjusted) return:
    ``target_amount / (1 + real) ** (target_age - age)``.

    Args:
        target_amount: Portfolio value wanted at ``target_age``, in today's dollars.
        age: Current age.
        target_age: Age at which the target must be reached (default 67).
        real: Real annual return as a decimal (default 2.9%).

    Returns:
        Capital required today, in today's dollars. Returns ``target_amount``
        itself when ``age >= target_age`` (no compounding window left).
    """
    years = target_age - age
    if years <= 0:
        return float(target_amount)
    return target_amount / (1.0 + real) ** years


def years_to_target(
    assets: float,
    monthly_saving: float,
    target_amount: float,
    real: float = 0.05,
) -> float | None:
    """Years to grow ``assets`` plus monthly saving into ``target_amount``.

    Closed form for annual compounding, with the monthly saving annualised
    (``12 * monthly_saving``)::

        ln((target_amount * real + 12 * monthly_saving)
           / (assets * real + 12 * monthly_saving)) / ln(1 + real)

    Args:
        assets: Current invested assets, in today's dollars.
        monthly_saving: Amount saved every month.
        target_amount: Target portfolio value, in today's dollars.
        real: Real annual return as a decimal (default 5%).

    Returns:
        Years as a float, ``0.0`` if already at or above the target, or
        ``None`` when the calculation is undefined — that is, when
        ``ln(1 + real) <= 0`` (``real <= 0``) or when the denominator
        ``assets * real + 12 * monthly_saving`` is ``<= 0``.
    """
    annual_saving = monthly_saving * 12.0
    if assets >= target_amount:
        return 0.0

    if real <= 0:
        return None

    denominator = assets * real + annual_saving
    if denominator <= 0:
        return None

    ratio = (target_amount * real + annual_saving) / denominator
    if ratio <= 0:
        return None

    return math.log(ratio) / math.log1p(real)
