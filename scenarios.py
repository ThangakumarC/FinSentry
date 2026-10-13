# scenarios.py
from typing import List, Dict
from pydantic import BaseModel

class Transaction(BaseModel):
    txn_id: str
    timestamp: str
    sender_id: str
    receiver_id: str
    amount_usd: float
    channel: str # WIRE, CASH, CRYPTO_RAMP, ACH
    description: str

class Alert(BaseModel):
    alert_id: str
    account_id: str
    account_holder: str
    declared_monthly_income: float
    risk_trigger: str
    transactions: List[Transaction]
    ground_truth_label: str  # "FALSE_POSITIVE" or "ESCALATE_SUSPICIOUS"

# Benchmark dataset for our Eval Harness
BENCHMARK_SCENARIOS: List[Alert] = [
    Alert(
        alert_id="ALT-101",
        account_id="ACC-8821",
        account_holder="Arun Kumar",
        declared_monthly_income=2500.0,
        risk_trigger="Multiple deposits just below $10,000 threshold within 48h",
        ground_truth_label="ESCALATE_SUSPICIOUS",
        transactions=[
            Transaction(txn_id="TXN-01", timestamp="2026-10-10 10:15", sender_id="ACC-9901", receiver_id="ACC-8821", amount_usd=9850.0, channel="CASH", description="Counter deposit"),
            Transaction(txn_id="TXN-02", timestamp="2026-10-11 14:20", sender_id="ACC-9902", receiver_id="ACC-8821", amount_usd=9600.0, channel="CASH", description="Branch cash deposit"),
            Transaction(txn_id="TXN-03", timestamp="2026-10-12 09:00", sender_id="ACC-9903", receiver_id="ACC-8821", amount_usd=9900.0, channel="CASH", description="ATM deposit"),
        ]
    ),
    Alert(
        alert_id="ALT-102",
        account_id="ACC-3312",
        account_holder="Sarah Jenkins",
        declared_monthly_income=6000.0,
        risk_trigger="Large single incoming wire > $50,000",
        ground_truth_label="FALSE_POSITIVE",
        transactions=[
            Transaction(txn_id="TXN-04", timestamp="2026-10-09 11:30", sender_id="ACC-ESCROW-4", receiver_id="ACC-3312", amount_usd=65000.0, channel="WIRE", description="Residential Property Escrow Release - Title Verified"),
        ]
    ),
    Alert(
        alert_id="ALT-103",
        account_id="ACC-7744",
        account_holder="Vikram Patel",
        declared_monthly_income=1200.0,
        risk_trigger="Rapid fund pass-through (Money Mule activity)",
        ground_truth_label="ESCALATE_SUSPICIOUS",
        transactions=[
            Transaction(txn_id="TXN-05", timestamp="2026-10-12 16:00", sender_id="ACC-SHELL-01", receiver_id="ACC-7744", amount_usd=15000.0, channel="WIRE", description="Consulting invoice"),
            Transaction(txn_id="TXN-06", timestamp="2026-10-12 16:18", sender_id="ACC-7744", receiver_id="ACC-CRYPTO-X", amount_usd=14850.0, channel="CRYPTO_RAMP", description="Immediate exchange purchase"),
        ]
    )
]