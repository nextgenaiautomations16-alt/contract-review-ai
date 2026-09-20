# Contract Review AI

**An AI agent that automates vendor contract review against a legal playbook** — checks liability caps, termination notice, indemnification, governing law, and payment terms against pre-approved ranges, auto-approving compliant contracts and routing deviations to a human with the specific reasons attached.

Seventh project in a series applying the same deterministic-rules-plus-human-in-the-loop architecture to different back-office workflows. See also [LoadAudit AI](https://github.com/nextgenaiautomations16-alt/loadaudit-ai), [Carrier Vet AI](https://github.com/nextgenaiautomations16-alt/carrier-vet-ai), [Claims Intake AI](https://github.com/nextgenaiautomations16-alt/claims-intake-ai), [Support Triage AI](https://github.com/nextgenaiautomations16-alt/support-triage-ai), [Lead Response AI](https://github.com/nextgenaiautomations16-alt/lead-response-ai), and [Mortgage Doc Intake AI](https://github.com/nextgenaiautomations16-alt/mortgage-doc-intake-ai).

## The problem

Every vendor contract needs review against the same handful of criteria before signature — a liability cap that's high enough, adequate termination notice, mutual (not one-sided) indemnification, an acceptable governing law, reasonable payment terms. Most contracts are actually fine as drafted, but a lawyer or procurement lead still has to check every one, which is repetitive and pulls legal attention away from the contracts that actually need judgment.

## What this does

1. **Check for missing clauses first, in isolation** — a contract with no liability cap or no indemnification clause at all is a bigger risk than one with a merely out-of-range value, and is reported as its own distinct outcome
2. **Check remaining clauses against playbook ranges** — liability cap below 75% of contract value, termination notice under 30 days, one-sided indemnification, unapproved governing law, payment terms over 60 days — all applicable issues are collected together, not reported one at a time
3. **Alert a human only when there's something to review** — approved contracts get no alert; flagged and missing-clause contracts post to Slack with visually distinct severity (🖊️ vs 🚨) and the specific reasons
4. **Evaluate the highest-risk failure mode separately** — the eval harness tracks missing-clause misclassifications on their own, since silently approving a contract with no liability protection is the one outcome this system cannot afford

## Quickstart

```bash
git clone <your-repo-url>
cd contract-review-ai
pip install -r requirements.txt

# 1. generate the synthetic dataset (26 contracts across all outcome types)
python data/generate_synthetic_contracts.py

# 2. run the evaluation harness
python -m eval.run_eval

# 3. run the API and try it yourself
uvicorn src.api:app --reload
# then POST to http://127.0.0.1:8000/contracts/review
```

Set `SLACK_WEBHOOK_URL` to actually post flagged/missing-clause contracts to a channel; without it, alerts print to the console.

## Evaluation results (on the included synthetic dataset)

```
Total contracts evaluated: 26
Outcome accuracy: 100.0%  (26/26)
Missing-clause contracts misclassified: 0
```

## Architecture

See [docs/architecture.md](docs/architecture.md) for the full pipeline and the reasoning behind checking missing clauses in isolation.

## Demo

See [docs/demo_script.md](docs/demo_script.md) for a 3-4 minute walkthrough script.

## Tech stack

Python, FastAPI, flat-file/JSON data store.

## Roadmap

- Add an LLM-based clause-extraction layer in front of review (same pattern as LoadAudit AI's `extraction.py`), so the system can work from an actual contract document instead of pre-structured input
- Make the playbook thresholds configurable by a legal team instead of hardcoded constants
- Integrate with a real e-signature/CLM system for approved contracts
- Add clause-by-clause redline suggestions, not just flagging
