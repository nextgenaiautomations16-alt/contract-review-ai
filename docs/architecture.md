# Architecture

```
Vendor contract submitted for review
      |
      v
Playbook engine (src/playbook.py)
  - missing-clause checks run first, in isolation: no liability cap,
    no indemnification clause at all
  - if none missing, flag checks run: liability cap below 75% of
    contract value, termination notice under 30 days, one-sided
    (not mutual) indemnification, governing law off the approved
    list, payment terms over 60 days
  - all applicable flag reasons are collected in one pass, not just
    the first one found
      |
      +--> approve         --> ready to sign, no alert
      |
      +--> flag             --> Slack alert (🖊️), all deviation
      |                         reasons listed together
      |
      +--> missing_clause   --> Slack alert (🚨), visually distinct --
      |                         a required protection is entirely
      |                         absent, not just out of range
      |
      v
Evaluation (eval/run_eval.py)
  - outcome accuracy against a labeled synthetic test set
  - separately tracks missing-clause misclassifications, since an
    absent liability cap or indemnification clause is the highest-risk
    failure mode this system could have -- silently approving a
    contract with no liability protection at all is worse than
    flagging a merely negotiable term
```

## Why missing clauses are checked first, in isolation

A contract with no liability cap at all is a fundamentally different
risk than one with a liability cap set too low. The first is silence on
a required protection; the second is a negotiated number outside a
preferred range. Checking for missing clauses first, before any flag
logic runs, means a genuinely dangerous contract can never get
downgraded into a routine "flag" just because it also happens to pass
some other check.

## Why all flag reasons are collected together, not reported one at a time

Legal reviewers benefit from seeing the whole picture of a contract's
deviations in one pass, rather than fixing one issue and returning to
find another new complaint on the next pass. The engine intentionally
checks every rule and returns every applicable reason together.

## What's stubbed vs. real

- Real: the playbook rules engine, an evaluation harness that separately
  tracks the missing-clause failure mode, a working FastAPI endpoint,
  Slack alerting with visually distinct severity levels.
- Stubbed/roadmap: extracting clause values from an actual contract
  document (this MVP takes already-structured clause data as input; a
  production version would add an LLM/document-extraction layer in
  front, same pattern as LoadAudit AI's `extraction.py`), a real
  e-signature/CLM system integration for "approved" contracts, a
  configurable playbook (currently hardcoded constants a legal team
  would want to own and version themselves), and clause-by-clause
  redline suggestions rather than just flagging.
