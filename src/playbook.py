"""
Deterministic contract review engine, checked against a legal/procurement
"playbook" -- pre-approved clause ranges a legal team defines once so most
vendor contracts never need a lawyer's direct attention.

Same principle as the rest of the series: the playbook thresholds are
explicit and auditable. A contract isn't flagged because a model "felt"
something looked risky -- it's flagged because a specific clause fell
outside a specific, legally-defined range, and the reason states exactly
which one.
"""
from dataclasses import dataclass, field

MIN_LIABILITY_CAP_RATIO = 0.75   # liability cap must be at least 75% of contract value
MIN_TERMINATION_NOTICE_DAYS = 30
MAX_PAYMENT_TERMS_DAYS = 60
ACCEPTABLE_GOVERNING_LAW = ["Delaware", "New York", "California"]


@dataclass
class ReviewResult:
    contract_id: str
    outcome: str  # "approve", "flag", or "missing_clause"
    reasons: list = field(default_factory=list)


def review_contract(contract: dict) -> ReviewResult:
    contract_id = contract["contract_id"]

    # Missing-clause checks come first and are reported on their own --
    # a contract silent on a required protection is a bigger risk than
    # one with an out-of-range value, and legal teams generally want to
    # know about silence before they even look at negotiated numbers.
    missing_reasons = []
    if not contract.get("liability_cap_present", True):
        missing_reasons.append("No liability cap clause present in the contract")
    if contract.get("indemnification_mutual") is None:
        missing_reasons.append("No indemnification clause present in the contract")

    if missing_reasons:
        return ReviewResult(contract_id, "missing_clause", missing_reasons)

    # Flag checks -- clause is present, but outside the playbook's
    # pre-approved range. All applicable reasons are collected, not just
    # the first one found, since a legal reviewer benefits from seeing
    # the full picture in one pass.
    reasons = []

    min_required_cap = contract["contract_value"] * MIN_LIABILITY_CAP_RATIO
    if contract["liability_cap_amount"] < min_required_cap:
        reasons.append(
            f"Liability cap (${contract['liability_cap_amount']:,.2f}) is below "
            f"{MIN_LIABILITY_CAP_RATIO:.0%} of contract value (min required: ${min_required_cap:,.2f})"
        )

    if contract["termination_notice_days"] < MIN_TERMINATION_NOTICE_DAYS:
        reasons.append(
            f"Termination notice period ({contract['termination_notice_days']} days) "
            f"is below the {MIN_TERMINATION_NOTICE_DAYS}-day minimum"
        )

    if contract.get("indemnification_mutual") is False:
        reasons.append("Indemnification clause is present but one-sided, not mutual")

    if contract["governing_law"] not in ACCEPTABLE_GOVERNING_LAW:
        reasons.append(f"Governing law ({contract['governing_law']}) is not on the approved jurisdiction list")

    if contract["payment_terms_days"] > MAX_PAYMENT_TERMS_DAYS:
        reasons.append(
            f"Payment terms ({contract['payment_terms_days']} days) exceed "
            f"the {MAX_PAYMENT_TERMS_DAYS}-day maximum"
        )

    if reasons:
        return ReviewResult(contract_id, "flag", reasons)

    return ReviewResult(contract_id, "approve", [])


def run_batch(contracts: list) -> list:
    return [review_contract(c) for c in contracts]
