"""
Posts contracts needing legal review to Slack, with missing-clause
contracts visually distinguished from negotiable flags -- a missing
required clause is a bigger risk than an out-of-range value, and a legal
team scanning a channel should be able to tell the difference at a
glance, not read every message fully to find out which is which.
"""
import os
import requests

SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

OUTCOME_EMOJI = {"missing_clause": "🚨", "flag": "🖊️"}


def send_review_alert(contract: dict, result) -> bool:
    emoji = OUTCOME_EMOJI.get(result.outcome, "🖊️")
    label = "Missing required clause" if result.outcome == "missing_clause" else "Flagged for review"
    reasons_text = "\n".join(f"• {r}" for r in result.reasons)

    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": f"{emoji} {label} — {contract.get('vendor_name')} ({contract.get('contract_id')})"}
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Contract value:*\n${contract.get('contract_value', 0):,.2f}"},
                {"type": "mrkdwn", "text": f"*Governing law:*\n{contract.get('governing_law', 'N/A')}"},
            ]
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Reason(s):*\n{reasons_text}"}
        },
    ]

    payload = {"text": f"Contract {contract.get('contract_id')}: {label}", "blocks": blocks}

    if not SLACK_WEBHOOK_URL:
        print("[notifications] SLACK_WEBHOOK_URL not set — logging alert instead of sending:")
        print(reasons_text)
        return True

    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=5)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"[notifications] Failed to send Slack alert: {e}")
        return False
