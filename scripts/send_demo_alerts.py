"""
Runs the synthetic contracts through review and sends real Slack alerts
for every flagged or missing-clause contract. Approved contracts never
page anyone.

Run from repo root: python -m scripts.send_demo_alerts
Requires SLACK_WEBHOOK_URL to be set (falls back to console logging if not).
"""
import json
from pathlib import Path

from src.playbook import review_contract
from src.notifications import send_review_alert

DATA_DIR = Path(__file__).parent.parent / "data"


def main():
    with open(DATA_DIR / "contracts.json") as f:
        contracts = json.load(f)

    sent = 0
    for contract in contracts:
        result = review_contract(contract)
        if result.outcome in ("flag", "missing_clause"):
            ok = send_review_alert(contract, result)
            print(f"{contract['contract_id']} ({result.outcome}): alert {'sent' if ok else 'FAILED'}")
            sent += 1

    print(f"\nDone — {sent} contract(s) alerted.")


if __name__ == "__main__":
    main()
