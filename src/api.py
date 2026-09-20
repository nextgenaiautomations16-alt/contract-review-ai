"""
Minimal FastAPI service exposing the contract review pipeline.

Run: uvicorn src.api:app --reload
Then: POST a contract to /contracts/review
"""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

from .playbook import review_contract
from .notifications import send_review_alert

app = FastAPI(title="Contract Review AI")


class Contract(BaseModel):
    contract_id: str
    vendor_name: str
    contract_value: float
    liability_cap_present: bool
    liability_cap_amount: Optional[float] = None
    termination_notice_days: int
    indemnification_mutual: Optional[bool] = None
    governing_law: str
    payment_terms_days: int
    auto_renewal_present: bool = True


@app.post("/contracts/review")
def review(contract: Contract):
    contract_dict = contract.model_dump()
    result = review_contract(contract_dict)

    response = {
        "contract_id": result.contract_id,
        "outcome": result.outcome,
        "reasons": result.reasons,
    }
    if result.outcome in ("flag", "missing_clause"):
        response["slack_alert_sent"] = send_review_alert(contract_dict, result)
    return response


@app.get("/health")
def health():
    return {"status": "ok"}
