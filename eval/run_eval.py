"""
Scores the playbook engine's outcome predictions against ground_truth.csv.

Run from repo root: python -m eval.run_eval
"""
import csv
import json
from pathlib import Path

from src.playbook import run_batch

DATA_DIR = Path(__file__).parent.parent / "data"


def load_json(name):
    with open(DATA_DIR / name) as f:
        return json.load(f)


def load_ground_truth():
    rows = {}
    with open(DATA_DIR / "ground_truth.csv") as f:
        for row in csv.DictReader(f):
            rows[row["contract_id"]] = row
    return rows


def main():
    contracts = load_json("contracts.json")
    ground_truth = load_ground_truth()

    results = run_batch(contracts)

    correct = 0
    mismatches = []
    missing_clause_misses = 0

    for r in results:
        expected = ground_truth[r.contract_id]["expected_outcome"]
        if r.outcome == expected:
            correct += 1
        else:
            mismatches.append((r.contract_id, expected, r.outcome, r.reasons))
            if expected == "missing_clause":
                missing_clause_misses += 1

    total = len(results)
    accuracy = correct / total if total else 0

    print("=== Contract Review AI — Evaluation Report ===")
    print(f"Total contracts evaluated: {total}")
    print(f"Outcome accuracy: {accuracy:.1%}  ({correct}/{total})")
    print(f"Missing-clause contracts misclassified (highest-risk failure mode): {missing_clause_misses}")

    if mismatches:
        print("\n--- Mismatches vs. ground truth ---")
        for contract_id, expected, actual, reasons in mismatches:
            print(f"  {contract_id}: expected {expected}, got {actual} {reasons if reasons else ''}")
    else:
        print("\nNo mismatches — every contract landed in the expected outcome bucket.")


if __name__ == "__main__":
    main()
