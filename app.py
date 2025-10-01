import streamlit as st
import pandas as pd
import io
from datetime import datetime

st.set_page_config(page_title="Business Evaluation Tool", layout="wide")

# ---------- Configuration ----------
CATEGORY_WEIGHTS = {
    "Business Profile & Model": 0.15,
    "Legal & Compliance": 0.15,
    "Accounting & Finance": 0.20,
    "Payroll & HR Statutory": 0.10,
    "Corporate Governance": 0.10,
    "Intellectual Property": 0.05,
    "Fundraising & Investor Readiness": 0.15,
    "Systems & Automation": 0.05,
    "Risk & Red Flags": 0.05,
}

DEFAULT_OPTION_SCORES = {
    "Yes / Good / Complete": 100,
    "Partially / In progress": 50,
    "No / Missing / Not Compliant": 0,
}

# ---------- Helper functions ----------
def score_option(option_label: str, custom_map=None):
    mapping = custom_map if custom_map else DEFAULT_OPTION_SCORES
    return mapping.get(option_label, 0)

def weighted_total(section_scores: dict, weights: dict):
    total = 0.0
    for k, s in section_scores.items():
        w = weights.get(k, 0)
        total += s * w
    return round(total, 2)

def readiness_label(total_score: float):
    if total_score > 80:
        return "✅ Investor Ready"
    if total_score >= 60:
        return "⚠️ Needs Work"
    return "❌ High Risk"

def format_percent(x):
    return f"{x:.1f}"

def export_to_csv(report: dict):
    df = pd.DataFrame(report["details"])
    meta = pd.DataFrame([["Company", report["company_name"]],
                         ["Evaluated On", report["evaluated_on"]],
                         ["Final Score", report["final_score"]],
                         ["Readiness", report["readiness"]]],
                        columns=["Key", "Value"])
    buf = io.StringIO()
    meta.to_csv(buf, index=False)
    buf.write("\n")
    df.to_csv(buf, index=False)
    return buf.getvalue().encode("utf-8")

# ---------- Questionnaire ----------
QUESTIONNAIRE = {
    "Business Profile & Model": [
        # ... [same as your pasted code] ...
        # Truncated for brevity, use your original section as-is
    ],

    "Legal & Compliance": [
        # ... [same as your pasted code] ...
    ],

    "Accounting & Finance": [
        # ... [same as your pasted code] ...
    ],

    "Payroll & HR Statutory": [
        # ... [same as your pasted code] ...
    ],

    "Corporate Governance": [
        {
            "key": "statutory_records_maintained",
            "label": "Are minutes, registers, board resolutions maintained and filed timely?",
            "type": "radio",
            "options": ["Yes / Good / Complete", "Partially / In progress", "No / Missing / Not Compliant"],
        },
        {
            "key": "board_meetings_regular",
            "label": "Are board meetings held as per statutory frequency?",
            "type": "radio",
            "options": ["Yes / Good / Complete", "No / Missing / Not Compliant"],
        },
        {
            "key": "audit_committee_exists",
            "label": "Does the company have an audit committee or equivalent?",
            "type": "radio",
            "options": ["Yes / Good / Complete", "No / Missing / Not Compliant"],
        }
    ],

    "Intellectual Property": [
        {
            "key": "ip_identified",
            "label": "Have all IP assets (patents, trademarks, copyrights) been identified?",
            "type": "radio",
            "options": ["Yes / Good / Complete", "Partially / In progress", "No / Missing / Not Compliant"],
        },
        {
            "key": "ip_registered",
            "label": "Are key IP assets registered or in registration?",
            "type": "radio",
            "options": ["Yes / Good / Complete", "Partially / In progress", "No / Missing / Not Compliant"],
        }
    ],

    "Fundraising & Investor Readiness": [
        {
            "key": "funding_plan",
            "label": "Is there a fundraising plan with amount, timeline, and use of funds?",
            "type": "radio",
            "options": ["Yes / Good / Complete", "Partially / In progress", "No / Missing / Not Compliant"],
        },
        {
            "key": "data_room_prepared",
            "label": "Is a data room prepared with key documents for investors?",
            "type": "radio",
            "options": ["Yes / Good / Complete", "No / Missing / Not Compliant"],
        },
        {
            "key": "cap_table_current",
            "label": "Is the cap table current and available?",
            "type": "radio",
            "options": ["Yes / Good / Complete", "No / Missing / Not Compliant"],
        }
    ],

    "Systems & Automation": [
        {
            "key": "process_automation",
            "label": "Are key business processes automated (CRM, accounting, payroll, compliance)?",
            "type": "radio",
            "options": ["Yes / Good / Complete", "Partially / In progress", "No / Missing / Not Compliant"],
        }
    ],

    "Risk & Red Flags": [
        {
            "key": "risk_identified",
            "label": "Are major business risks identified and mitigation plans in place?",
            "type": "radio",
            "options": ["Yes / Good / Complete", "Partially / In progress", "No / Missing / Not Compliant"],
        },
        {
            "key": "pending_litigation",
            "label": "Is there any pending litigation or regulatory action?",
            "type": "radio",
            "options": ["No / Missing / Not Compliant", "Yes / Good / Complete"],
        }
    ],
}

# ---------- UI Logic ----------
st.title("Business Evaluation Tool")

st.markdown("This tool helps you assess business investor readiness across key categories. Fill the questionnaire below to generate your report.")

company_name = st.text_input("Company Name")
evaluate_btn = st.button("Evaluate Business")

responses = {}
details = []
section_scores = {}

if company_name:
    with st.form("evaluation_form"):
        st.header(f"Business Evaluation: {company_name}")
        for section, questions in QUESTIONNAIRE.items():
            st.subheader(section)
            section_score = 0
            answered = 0
            for question in questions:
                key = f"{section}_{question['key']}"
                if question["type"] == "radio":
                    resp = st.radio(question["label"], question["options"], key=key)
                    responses[key] = resp
                    val = score_option(resp)
                    section_score += val
                    answered += 1
                    details.append({"Section": section, "Question": question["label"], "Response": resp, "Score": val})
                    # Handle branches
                    branch = question.get("branch", {})
                    if resp in branch:
                        for subq in branch[resp]:
                            subkey = f"{section}_{subq['key']}"
                            subresp = st.radio(subq["label"], subq["options"], key=subkey)
                            responses[subkey] = subresp
                            subval = score_option(subresp)
                            section_score += subval
                            answered += 1
                            details.append({"Section": section, "Question": subq["label"], "Response": subresp, "Score": subval})
                elif question["type"] == "select":
                    resp = st.selectbox(question["label"], question["options"], key=key)
                    responses[key] = resp
                    # For select, assign a score (e.g. "None" = 0, others = 100)
                    val = 0 if resp == "None" else 100
                    section_score += val
                    answered += 1
                    details.append({"Section": section, "Question": question["label"], "Response": resp, "Score": val})
            # Average score for the section
            section_scores[section] = round(section_score / answered if answered else 0, 2)
        submitted = st.form_submit_button("Submit")

    if 'submitted' in locals() and submitted:
        final_score = weighted_total(section_scores, CATEGORY_WEIGHTS)
        readiness = readiness_label(final_score)
        st.success(f"Final Score: {final_score} / 100")
        st.info(f"Readiness: {readiness}")
        st.write("**Section-wise Scores:**")
        st.table({section: f"{score:.1f}" for section, score in section_scores.items()})
        st.write("**Detailed Responses:**")
        st.dataframe(pd.DataFrame(details))
        report = {
            "company_name": company_name,
            "evaluated_on": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "final_score": final_score,
            "readiness": readiness,
            "details": details
        }
        csv = export_to_csv(report)
        st.download_button("Download Evaluation as CSV", csv, file_name=f"{company_name}_evaluation.csv", mime="text/csv")