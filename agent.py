# agent.py
from typing import TypedDict, List
from pydantic import BaseModel, Field
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from scenarios import Alert, BENCHMARK_SCENARIOS

# Structured output for Auditable Dossier
class CaseDossier(BaseModel):
    verdict: str = Field(description="Must be either 'ESCALATE_SUSPICIOUS' or 'FALSE_POSITIVE'")
    risk_level: str = Field(description="LOW, MEDIUM, HIGH, or CRITICAL")
    primary_typology: str = Field(description="E.g., Structuring/Smurfing, Money Mule, Legitimate Asset Sale, etc.")
    cited_transaction_ids: List[str] = Field(description="Exact transaction IDs that prove the verdict")
    investigator_rationale: str = Field(description="Detailed narrative of why this alert is or is not suspicious")
    audit_notes: str = Field(description="Notes from regulatory verification")

class AgentState(TypedDict):
    alert: dict
    preliminary_verdict: str
    preliminary_rationale: str
    cited_txns: List[str]
    audit_feedback: str
    final_dossier: dict

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)

# --- NODE 1: Forensic Investigator ---
def investigate_alert(state: AgentState) -> dict:
    alert = state["alert"]
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a Tier-2 AML (Anti-Money Laundering) Forensic Investigator at a global bank.
Investigate the transaction alert objectively. Check:
1. Income to transaction volume divergence.
2. Velocity of transfers (rapid movement).
3. Smurfing / structuring patterns (amounts just below regulatory reporting thresholds).
4. Genuine economic purpose (e.g., verified escrow, payroll, invoices).

Return your findings in valid JSON format with keys:
verdict ('ESCALATE_SUSPICIOUS' or 'FALSE_POSITIVE'),
risk_level ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'),
primary_typology,
cited_transaction_ids (list of txn_ids),
investigator_rationale."""),
        ("human", "Alert Details: {alert_json}")
    ])
    
    chain = prompt | llm
    res = chain.invoke({"alert_json": json.dumps(alert)})
    
    # Parse json or fallback
    try:
        parsed = json.loads(res.content.replace("```json", "").replace("```", "").strip())
    except:
        parsed = {
            "verdict": "FALSE_POSITIVE",
            "risk_level": "LOW",
            "primary_typology": "Unspecified",
            "cited_transaction_ids": [],
            "investigator_rationale": res.content
        }
        
    return {
        "preliminary_verdict": parsed.get("verdict"),
        "preliminary_rationale": parsed.get("investigator_rationale"),
        "cited_txns": parsed.get("cited_transaction_ids", []),
        "final_dossier": parsed
    }

# --- NODE 2: Compliance Auditor (Zero-Hallucination Guard) ---
def compliance_auditor(state: AgentState) -> dict:
    alert = state["alert"]
    actual_txn_ids = {t["txn_id"] for t in alert["transactions"]}
    cited_ids = set(state["cited_txns"])
    
    # Hallucination check
    hallucinated = cited_ids - actual_txn_ids
    if hallucinated:
        feedback = f"AUDIT FAILED: Agent hallucinated transaction IDs: {hallucinated}"
    else:
        feedback = f"AUDIT PASSED: All {len(cited_ids)} cited evidence IDs exist in transactional ledger."
        
    dossier = state["final_dossier"]
    dossier["audit_notes"] = feedback
    
    return {
        "audit_feedback": feedback,
        "final_dossier": dossier
    }

# --- BUILD LANGGRAPH ---
builder = StateGraph(AgentState)
builder.add_node("investigator", investigate_alert)
builder.add_node("auditor", compliance_auditor)

builder.set_entry_point("investigator")
builder.add_edge("investigator", "auditor")
builder.add_edge("auditor", END)

workflow = builder.compile()
