import streamlit as st
import requests
import os

# Configuration
API_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000/api")

st.set_page_config(
    page_title="ColdChain Assist - Decision Support Prototype",
    page_icon="❄️",
    layout="wide"
)

# --- Helper functions ---
def fetch_metrics():
    try:
        r = requests.get(f"{API_URL}/metrics")
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

def fetch_alerts():
    try:
        r = requests.get(f"{API_URL}/alerts")
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []

def fetch_alert_detail(alert_id):
    try:
        r = requests.get(f"{API_URL}/alerts/{alert_id}")
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

def show_disclaimer():
    st.sidebar.markdown("---")
    st.sidebar.warning(
        "**Prototype / Decision Support**\n\n"
        "This system does not claim regulatory certification and does not guarantee food safety. "
        "It is designed solely to support human decision-making."
    )

# --- Pages ---
def render_dashboard():
    st.title("Executive Dashboard")
    metrics = fetch_metrics()
    
    if not metrics:
        st.error(f"Unable to connect to backend API at {API_URL}. Ensure the FastAPI server is running.")
        return
        
    st.subheader("Current Status Overview")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Alerts", metrics.get("total_alerts", 0))
    col2.metric("High Risk Alerts", metrics.get("high_risk_alerts", 0))
    col3.metric("Medium Risk Alerts", metrics.get("medium_risk_alerts", 0))
    col4.metric("Low Risk Alerts", metrics.get("low_risk_alerts", 0))
    
    st.markdown("---")
    st.subheader("Resolution Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Confirmed Actions", metrics.get("confirmed_recommendations", 0))
    col2.metric("Dispatcher Overrides", metrics.get("overrides", 0))
    col3.metric("Average Time to Corrective Action", metrics.get("average_time_to_corrective_action", "N/A"))


def render_create_alert():
    st.title("Create Alert")
    st.write("Simulate an incoming temperature telemetry event.")
    
    with st.form("create_alert_form"):
        col1, col2 = st.columns(2)
        with col1:
            temperature = st.number_input("Temperature °C", value=-10.0, step=0.1)
            duration = st.number_input("Excursion Duration (minutes)", min_value=0, value=30)
            location = st.selectbox("Location", ["warehouse", "loading_area", "vehicle", "customer_delivery"])
        with col2:
            product_class = st.selectbox("Product Class", ["frozen", "chilled", "unknown"])
            
            all_actions = [
                "continue_monitoring",
                "move_to_controlled_storage",
                "inspect_packaging",
                "quarantine",
                "escalate_to_supervisor",
                "dispatch_replacement"
            ]
            available_actions = st.multiselect(
                "Available Corrective Actions", 
                options=all_actions, 
                default=all_actions
            )
            
        submitted = st.form_submit_button("Submit to Decision Engine")
        
    if submitted:
        payload = {
            "temperature": temperature,
            "duration_minutes": duration,
            "location": location,
            "product_class": product_class,
            "available_actions": available_actions
        }
        
        try:
            r = requests.post(f"{API_URL}/alerts", json=payload)
            if r.status_code == 200:
                alert = r.json()
                st.success("Alert processed successfully.")
                
                # Show results immediately
                rec = alert.get("recommendations", [])[0] if alert.get("recommendations") else None
                if rec:
                    st.markdown("### Automated Evaluation Results")
                    
                    risk_color = "red" if rec['risk_level'] == "HIGH" else "orange" if rec['risk_level'] == "MEDIUM" else "green"
                    
                    st.markdown(f"**RISK LEVEL:** <span style='color:{risk_color}; font-weight:bold;'>{rec['risk_level']}</span>", unsafe_allow_html=True)
                    st.write(f"**RECOMMENDED ACTION:** `{rec['recommended_action']}`")
                    st.write(f"**WHY THIS ACTION?:** {rec['explanation']}")
                    st.write(f"**RULE / EVIDENCE:** {rec['rule_id']}")
                    st.write(f"**HUMAN CONFIRMATION REQUIRED?:** {'YES' if rec['requires_confirmation'] else 'NO'}")
                    
                    st.info(f"**SAFETY NOTES:** {rec.get('safety_notes', 'This is a decision-support prototype. It does not guarantee food safety.')}")
            else:
                st.error(f"Error creating alert: {r.text}")
        except Exception as e:
            st.error(f"Connection error: {e}")


def render_alert_details():
    st.title("Alert Management")
    
    alerts = fetch_alerts()
    if not alerts:
        st.info("No alerts found in the database. Go to 'Create Alert' to generate one.")
        return
        
    # Dropdown to select an alert
    alert_options = {f"Alert #{a['id']} - {a['detected_at'][:19]} (Status: {a['status']})": a['id'] for a in alerts}
    selected_name = st.selectbox("Select Alert", list(alert_options.keys()))
    
    if selected_name:
        alert_id = alert_options[selected_name]
        detail = fetch_alert_detail(alert_id)
        
        if detail:
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Event Information")
                st.write(f"**Alert ID:** {detail['id']}")
                st.write(f"**Current Status:** `{detail['status']}`")
                st.write(f"**Temperature:** {detail['temperature']} °C")
                st.write(f"**Duration:** {detail['duration_minutes']} mins")
                st.write(f"**Location:** {detail['location']}")
                st.write(f"**Product Class:** {detail['product_class']}")
            
            with col2:
                st.subheader("Engine Recommendation")
                recs = detail.get("recommendations", [])
                latest_rec = recs[-1] if recs else None
                if latest_rec:
                    st.write(f"**Risk Level:** {latest_rec['risk_level']}")
                    st.write(f"**Recommended Action:** `{latest_rec['recommended_action']}`")
                    st.write(f"**Rule ID:** {latest_rec['rule_id']}")
                    st.write(f"**Explanation:** {latest_rec['explanation']}")
                    st.write(f"**Confirmation State:** {'Required' if latest_rec['requires_confirmation'] else 'Auto-Resolved'}")
                else:
                    st.write("No recommendations generated.")
                    
            st.markdown("---")
            
            # Interactive Actions
            if detail['status'] == 'pending':
                st.subheader("Take Action")
                action_col1, action_col2 = st.columns(2)
                
                with action_col1:
                    if latest_rec and latest_rec['requires_confirmation']:
                        st.write("### Human Confirmation")
                        st.warning("This high-impact action requires manual validation. Do not blindly execute without reviewing.")
                        if st.button("✅ Confirm Recommended Action", use_container_width=True):
                            r = requests.post(f"{API_URL}/alerts/{alert_id}/confirm")
                            if r.status_code == 200:
                                st.success("Action confirmed!")
                                st.rerun()
                            else:
                                st.error(f"Error: {r.text}")
                    else:
                        st.write("No explicit confirmation required.")
                        
                with action_col2:
                    st.write("### Dispatcher Override")
                    with st.form(f"override_form_{alert_id}"):
                        st.write("Force an alternative corrective action.")
                        all_actions = [
                            "continue_monitoring",
                            "move_to_controlled_storage",
                            "inspect_packaging",
                            "quarantine",
                            "escalate_to_supervisor",
                            "dispatch_replacement"
                        ]
                        
                        orig_action = latest_rec['recommended_action'] if latest_rec else "unknown"
                        st.text_input("Original Recommendation", value=orig_action, disabled=True)
                        
                        new_action = st.selectbox("New Corrective Action", all_actions)
                        reason = st.text_area("Mandatory Override Reason", placeholder="Explain why the system recommendation is being bypassed.")
                        dispatcher = st.text_input("Dispatcher Name", placeholder="e.g. Jane Doe")
                        
                        submit_override = st.form_submit_button("Submit Override")
                        if submit_override:
                            if not reason.strip():
                                st.error("Override reason is mandatory.")
                            elif not dispatcher.strip():
                                st.error("Dispatcher name is mandatory.")
                            else:
                                payload = {
                                    "overridden_action": new_action,
                                    "reason": reason,
                                    "dispatcher": dispatcher
                                }
                                r = requests.post(f"{API_URL}/alerts/{alert_id}/override", json=payload)
                                if r.status_code == 200:
                                    st.success("Override applied successfully!")
                                    st.rerun()
                                else:
                                    st.error(f"Error: {r.text}")
            else:
                st.success(f"This alert is fully resolved (Current Status: **{detail['status']}**). No further action required.")

            st.markdown("---")
            st.subheader("Audit History")
            audit_logs = detail.get("audit_logs", [])
            if audit_logs:
                for log in sorted(audit_logs, key=lambda x: x['timestamp']):
                    st.write(f"- **{log['timestamp'][:19]}** | [{log['event_type']}] by {log['actor']}: {log['reason']} (Value: {log['new_value']})")
            else:
                st.write("No audit logs available.")


def render_metrics():
    st.title("Performance & Delivery Metrics")
    st.write("Comparing prototype efficiency against manual dispatcher baselines.")
    
    metrics = fetch_metrics()
    if not metrics:
        st.error("Unable to load metrics.")
        return
        
    avg_str = metrics.get("average_time_to_corrective_action", "0m 0s")
    
    try:
        parts = avg_str.split('m')
        mins = int(parts[0])
        secs = int(parts[1].replace('s','').strip())
        measured_seconds = mins * 60 + secs
    except Exception:
        measured_seconds = 0
        
    baseline_seconds = 15 * 60 # 15 mins historically
    target_seconds = 5 * 60 # 5 mins goal
    
    improvement_pct = 0
    if baseline_seconds > 0 and measured_seconds > 0:
        improvement_pct = round(((baseline_seconds - measured_seconds) / baseline_seconds) * 100, 1)
        
    col1, col2, col3 = st.columns(3)
    col1.metric("Baseline Corrective-Action Time", "15m 0s", help="Historical manual process time.")
    col2.metric("Target Corrective-Action Time", "5m 0s", help="Goal for decision-support prototype.")
    
    # Delta logic: positive means we saved time.
    delta_str = f"{improvement_pct}% Improvement" if measured_seconds > 0 else None
    col3.metric(
        "Measured Prototype Result", 
        avg_str,
        delta=delta_str,
        delta_color="normal" if improvement_pct > 0 else "inverse"
    )
    
    st.markdown("---")
    st.subheader("System Efficacy")
    col4, col5 = st.columns(2)
    
    overrides = metrics.get("overrides", 0)
    high_risk = metrics.get("high_risk_alerts", 0)
    
    col4.metric("Error Count / Manual Overrides", overrides, help="Times a human rejected the system recommendation.")
    col5.metric("Edge-Case Results (High Risk Events)", high_risk, help="Complex alerts requiring human confirmation.")
    
    st.info("Clearly labeled above: baseline, target, and measured prototype results.")


def render_rule_reference():
    st.title("Decision Rule Reference")
    st.write("The assistant operates deterministically using the following rules.")
    
    rules = [
        {"id": "R001", "name": "Normal conditions", "desc": "Temperature is within the configured acceptable range for the product class. Risk = LOW, Action = continue_monitoring."},
        {"id": "R002", "name": "Moderate excursion", "desc": "Temperature is outside the acceptable range for a moderate duration. Risk = MEDIUM, Action = move_to_controlled_storage."},
        {"id": "R003", "name": "Severe or prolonged", "desc": "The excursion is severe or prolonged. Risk = HIGH, Action = quarantine. Requires confirmation."},
        {"id": "R004", "name": "Unknown class", "desc": "If the product class is unknown. Risk = HIGH, Action = quarantine. Requires confirmation."},
        {"id": "R005", "name": "Action Unavailable Fallback", "desc": "If available_actions does not contain the recommended action, select the safest available alternative and explain the fallback."},
        {"id": "R006", "name": "Customer Delivery Impact", "desc": "If the alert occurs at customer_delivery, prioritize customer service and recommend dispatch_replacement."},
        {"id": "R007", "name": "Missing data", "desc": "If data is missing or contradictory. Risk = HIGH, Action = escalate_to_supervisor. Requires confirmation."}
    ]
    
    for r in rules:
        with st.expander(f"Rule {r['id']}: {r['name']}"):
            st.write(r['desc'])


def render_audit_history():
    st.title("Global Audit History")
    st.write("Complete ledger of plan changes, confirmations, and overrides.")
    
    alerts = fetch_alerts()
    if not alerts:
        st.info("No activity found.")
        return
        
    all_logs = []
    for a in alerts:
        detail = fetch_alert_detail(a['id'])
        if detail and detail.get('audit_logs'):
            for log in detail['audit_logs']:
                log['alert_id'] = a['id']
                all_logs.append(log)
                
    if not all_logs:
        st.info("No audit logs found.")
        return
        
    all_logs.sort(key=lambda x: x['timestamp'], reverse=True)
    
    for log in all_logs:
        st.markdown(f"**Alert #{log['alert_id']}** - `{log['timestamp'][:19]}`")
        st.write(f"[{log['event_type']}] Actor: **{log['actor']}**")
        if log['previous_value'] or log['new_value']:
            st.write(f"Change: `{log['previous_value']} -> {log['new_value']}`")
        st.write(f"Reason: {log['reason']}")
        st.markdown("---")


def render_safety_fairness_controls():
    st.title("Safety, Fairness & Service Controls")
    st.write("This section demonstrates how the prototype's design principles are operationalized in the decision engine.")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🛡️ Safety: High-Risk Confirmation")
        st.info("High-risk or uncertain cases must not be silently approved. The system inherently escalates these and forces explicit manual confirmation.")
        
        st.subheader("📝 Safety & Audit: Override Reasons")
        st.info("When a human dispatcher overrides an automated recommendation, the system strictly enforces the submission of a mandatory override rationale. This ensures every deviation is logged.")
        
        st.subheader("⚠️ Safety: Escalation for Uncertainty")
        st.info("If contradictory inputs are received or data is missing, the system aborts standard evaluation and immediately recommends escalation to a supervisor.")

    with col2:
        st.subheader("⚖️ Fairness: Consistent Rule Application")
        st.info("The same decision rules are applied consistently for equivalent telemetry conditions. The system does not use customer identity, demographic attributes, income, or other irrelevant personal attributes. *(Note: Fairness is a prototype design objective and validation criterion; we do not claim it is mathematically proven.)*")
        
        st.subheader("📦 Customer Service")
        st.info("At customer delivery, standard quarantine rules are adapted to consider replacement or return actions, prioritizing customer service without compromising product safety.")
        
        st.subheader("🔍 Transparency: Audit History")
        st.info("Every state change, automated evaluation, and human override is immutably logged in the Audit History for full operational transparency.")

def main():
    st.sidebar.title("ColdChain Assist")
    st.sidebar.write("Prototype Dashboard")
    
    page = st.sidebar.radio("Navigation", [
        "Executive Dashboard",
        "Create Alert",
        "Alert Details",
        "Metrics",
        "Rule Reference",
        "Safety, Fairness & Service Controls",
        "Audit History"
    ])
    
    if page == "Executive Dashboard":
        render_dashboard()
    elif page == "Create Alert":
        render_create_alert()
    elif page == "Alert Details":
        render_alert_details()
    elif page == "Metrics":
        render_metrics()
    elif page == "Rule Reference":
        render_rule_reference()
    elif page == "Safety, Fairness & Service Controls":
        render_safety_fairness_controls()
    elif page == "Audit History":
        render_audit_history()
        
    show_disclaimer()

if __name__ == "__main__":
    main()
