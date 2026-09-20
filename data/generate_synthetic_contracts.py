"""
Generates synthetic vendor contracts plus a labeled ground truth of how
each should be triaged against a legal/procurement "playbook" -- the set
of pre-approved clause ranges a legal team defines once, so most
contracts never need a lawyer's eyes at all.

Run: python generate_synthetic_contracts.py
Outputs: contracts.json, ground_truth.csv
"""
import json
import random
import csv
from pathlib import Path

random.seed(31)

VENDOR_NAMES = [
    "Northbridge Supply Co", "Vantage Logistics", "Clearline Software",
    "Meridian Consulting", "Ashford Materials", "Brightline Services",
    "Kestrel Data Systems", "Union Point Partners", "Cobalt Freight",
    "Silverline Analytics",
]
GOVERNING_LAW_ACCEPTABLE = ["Delaware", "New York", "California"]
GOVERNING_LAW_UNACCEPTABLE = ["Cayman Islands", "Isle of Man"]

# Outcome categories:
#   approve         -> every clause within playbook range: ready to sign
#   flag            -> a clause is present but outside the acceptable
#                      range (negotiable, needs a lawyer's judgment call)
#   missing_clause  -> a REQUIRED clause is absent entirely (higher risk
#                      than a deviation -- the contract is silent on
#                      something that must be addressed before signing)

N_CONTRACTS = 26


def make_contract(contract_id, outcome):
    vendor = random.choice(VENDOR_NAMES)
    contract_value = round(random.uniform(50000, 500000), 2)

    liability_cap_present = True
    liability_cap_amount = contract_value  # cap equal to contract value = compliant baseline
    termination_notice_days = 30
    indemnification_mutual = True
    governing_law = random.choice(GOVERNING_LAW_ACCEPTABLE)
    payment_terms_days = 45
    auto_renewal_present = True

    if outcome == "missing_liability_cap":
        liability_cap_present = False
    elif outcome == "missing_indemnification":
        indemnification_mutual = None  # clause absent entirely
    elif outcome == "flag_low_liability_cap":
        liability_cap_amount = round(contract_value * random.uniform(0.2, 0.5), 2)
    elif outcome == "flag_short_termination_notice":
        termination_notice_days = random.choice([5, 10, 15])
    elif outcome == "flag_one_sided_indemnification":
        indemnification_mutual = False  # present, but one-sided rather than absent
    elif outcome == "flag_unacceptable_governing_law":
        governing_law = random.choice(GOVERNING_LAW_UNACCEPTABLE)
    elif outcome == "flag_long_payment_terms":
        payment_terms_days = random.choice([75, 90, 120])

    return {
        "contract_id": f"CTR{7000 + contract_id}",
        "vendor_name": vendor,
        "contract_value": contract_value,
        "liability_cap_present": liability_cap_present,
        "liability_cap_amount": liability_cap_amount if liability_cap_present else None,
        "termination_notice_days": termination_notice_days,
        "indemnification_mutual": indemnification_mutual,
        "governing_law": governing_law,
        "payment_terms_days": payment_terms_days,
        "auto_renewal_present": auto_renewal_present,
    }


def expected_bucket(outcome_detail: str) -> str:
    if outcome_detail.startswith("missing"):
        return "missing_clause"
    if outcome_detail.startswith("flag"):
        return "flag"
    return "approve"


def main():
    plan = (
        ["missing_liability_cap"] * 3
        + ["missing_indemnification"] * 3
        + ["flag_low_liability_cap"] * 3
        + ["flag_short_termination_notice"] * 3
        + ["flag_one_sided_indemnification"] * 3
        + ["flag_unacceptable_governing_law"] * 2
        + ["flag_long_payment_terms"] * 3
        + ["approve"] * (N_CONTRACTS - 20)
    )
    random.shuffle(plan)

    contracts = []
    ground_truth_rows = []

    for i, outcome_detail in enumerate(plan):
        contract = make_contract(i, outcome_detail)
        contracts.append(contract)
        ground_truth_rows.append({
            "contract_id": contract["contract_id"],
            "expected_outcome": expected_bucket(outcome_detail),
            "detail": outcome_detail,
        })

    out_dir = Path(__file__).parent
    with open(out_dir / "contracts.json", "w") as f:
        json.dump(contracts, f, indent=2)
    with open(out_dir / "ground_truth.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["contract_id", "expected_outcome", "detail"])
        writer.writeheader()
        writer.writerows(ground_truth_rows)

    print(f"Generated {N_CONTRACTS} contracts.")


if __name__ == "__main__":
    main()
