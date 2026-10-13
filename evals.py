import json
from scenarios import BENCHMARK_SCENARIOS
from agent import workflow
from tabulate import tabulate

def run_evaluation():
    print("Running Polarisk AML Investigation Agent Evaluation Harness...\n")
    results = []
    
    correct_verdicts = 0
    total_grounded = 0
    
    for alert in BENCHMARK_SCENARIOS:
        state_input = {"alert": alert.model_dump()}
        output = workflow.invoke(state_input)
        
        dossier = output["final_dossier"]
        predicted = dossier.get("verdict")
        ground_truth = alert.ground_truth_label
        is_correct = (predicted == ground_truth)
        if is_correct:
            correct_verdicts += 1
            
        is_grounded = "AUDIT PASSED" in dossier.get("audit_notes", "")
        if is_grounded:
            total_grounded += 1
            
        results.append({
            "Alert ID": alert.alert_id,
            "Account": alert.account_holder,
            "Ground Truth": ground_truth,
            "Agent Verdict": predicted,
            "Correct?": "yes" if is_correct else "no",
            "Audit Passed": "yes" if is_grounded else "no",
            "Risk": dossier.get("risk_level")
        })
        
    print(tabulate(results, headers="keys", tablefmt="fancy_grid"))
    
    acc = (correct_verdicts / len(BENCHMARK_SCENARIOS)) * 100
    grounding_rate = (total_grounded / len(BENCHMARK_SCENARIOS)) * 100
    print(f"\nAccuracy on Risk Classification: {acc:.1f}%")
    print(f"Evidence Grounding Score (No Hallucination): {grounding_rate:.1f}%\n")

if __name__ == "__main__":
    run_evaluation()