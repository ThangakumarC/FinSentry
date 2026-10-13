# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from scenarios import Alert, Transaction, BENCHMARK_SCENARIOS
from agent import workflow

app = FastAPI(
    title="FinSentry - Autonomous AML Investigation & Governance Agent",
    version="1.0.0",
    description="Multi-agent compliance pipeline for automated financial crime investigation and auditable case generation."
)

@app.get("/")
def health_check():
    return {
        "status": "online",
        "service": "FinSentry AML Agent",
        "supported_models": ["openai/gpt-oss-20b via Groq"],
        "governance_mode": "Strict Deterministic Audit Guard"
    }

@app.post("/api/investigate")
def investigate_alert_endpoint(alert: Alert):
    try:
        state_input = {"alert": alert.model_dump()}
        output = workflow.invoke(state_input)
        return {
            "alert_id": alert.alert_id,
            "account_holder": alert.account_holder,
            "dossier": output.get("final_dossier", {}),
            "audit_trail": output.get("audit_feedback", "")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/benchmark-scenarios")
def get_benchmarks():
    return [s.model_dump() for s in BENCHMARK_SCENARIOS]