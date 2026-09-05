import csv
import os
import sys

# Ensure the backend module is accessible
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.decision_engine import evaluate_excursion

def run_validation():
    csv_path = "data/validation_dataset.csv"
    out_path = "data/test_results.csv"
    
    results = []
    
    total = 0
    correct_action = 0
    false_safe = 0
    false_escalation = 0
    
    edge_cases_total = 0
    edge_cases_passed = 0
    
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            test_id = row['test_id']
            temp = float(row['temperature_c']) if row['temperature_c'] else None
            dur = int(row['duration_minutes']) if row['duration_minutes'] else None
            loc = row['location']
            p_class = row['product_class']
            actions = row['available_actions'].split('|') if row['available_actions'] else []
            
            exp_risk = row['expected_risk']
            exp_action = row['expected_action']
            exp_conf = row['expected_confirmation'] == 'True'
            exp_rule = row['expected_rule_id']
            
            # Execute engine
            actual = evaluate_excursion(temp, dur, loc, p_class, actions)
            
            # Check correctness
            passed = (
                actual['risk_level'] == exp_risk and
                actual['recommended_action'] == exp_action and
                actual['requires_confirmation'] == exp_conf and
                actual['rule_id'] == exp_rule
            )
            
            action_match = (actual['recommended_action'] == exp_action)
            
            total += 1
            if action_match:
                correct_action += 1
                
            # Critical Metrics
            # False-Safe: The system under-reacted to a real excursion
            if exp_risk in ['HIGH', 'MEDIUM'] and actual['risk_level'] == 'LOW':
                false_safe += 1
                
            # False-Escalation: The system over-reacted to a normal situation
            if exp_risk == 'LOW' and actual['risk_level'] in ['HIGH', 'MEDIUM']:
                false_escalation += 1
                
            # Track Edge Cases specifically
            if test_id.startswith('EDGE'):
                edge_cases_total += 1
                if passed:
                    edge_cases_passed += 1
                    
            # Record actuals
            row['actual_risk'] = actual['risk_level']
            row['actual_action'] = actual['recommended_action']
            row['actual_conf'] = str(actual['requires_confirmation'])
            row['actual_rule'] = actual['rule_id']
            row['pass'] = str(passed)
            
            results.append(row)
            
    # Calculate percentages
    accuracy = (correct_action / total) * 100 if total else 0
    edge_rate = (edge_cases_passed / edge_cases_total) * 100 if edge_cases_total else 0
    
    # Save output
    with open(out_path, 'w', newline='') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
            
    print("=== Validation Results ===")
    print(f"Total Tests Run: {total}")
    print(f"Accuracy (Perfect Action Match): {accuracy:.1f}%")
    print(f"Correct Action Rate: {(correct_action/total)*100:.1f}%")
    print(f"False-Safe Decisions (Critical Error): {false_safe}")
    print(f"False-Escalation Decisions (Efficiency Error): {false_escalation}")
    print(f"Edge-Case Pass Rate: {edge_rate:.1f}% ({edge_cases_passed}/{edge_cases_total})")
    print(f"Detailed results saved to: {out_path}")

if __name__ == "__main__":
    run_validation()
