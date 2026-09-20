# Demo Script (3-4 minutes)

**0:00-0:30 — The problem**
"Legal and procurement teams review every vendor contract against the
same handful of criteria — liability caps, termination notice, governing
law, payment terms. Most contracts are actually fine, but someone still
has to check. This is Contract Review AI — it applies a legal team's own
playbook automatically, so a lawyer only sees the contracts that actually
need one."

**0:30-1:15 — Show the eval**
Run `python -m eval.run_eval`. Point out the separate missing-clause-miss
count, and explain why an absent liability cap is treated as a different,
higher-risk category than an out-of-range one.

**1:15-2:15 — Show a multi-flag contract**
Hit the API with a contract that has five simultaneous issues (low
liability cap, short notice, one-sided indemnification, bad governing
law, long payment terms). Show all five reasons returned together in one
Slack alert, not five separate pings.

**2:15-3:00 — Show a missing-clause contract**
Hit the API with a contract that has no liability cap at all. Show the
🚨 emoji and distinct framing versus the 🖊️ flag alerts — point out this
is a deliberate visual/severity distinction, not decoration.

**3:00-3:45 — Close**
"Seventh project in the series, same architecture, first time applied to
a legal/procurement domain — shows the pattern isn't tied to any one
industry, it's a general approach to 'where can rules replace routine
human review, and where does a human still need to be in the loop.'"
