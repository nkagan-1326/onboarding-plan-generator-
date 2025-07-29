
import streamlit as st
import openai
import os
from fpdf import FPDF
import base64

st.set_page_config(page_title="Onboarding Plan Generator", layout="wide")
st.title("📋 AI-Powered Onboarding Plan Generator")

# Role presets and prefill content
role_presets = {
    "Entry-level Customer Success Manager": {
        "role": "Entry-level Customer Success Manager",
        "level": "Individual Contributor",
        "area": "Customer Success",
        "company_size": "1–25",
        "company_stage": "Seed",
        "team_size": 5,
        "customer_facing": True,
        "manager_priorities": "Ramp on product, support processes, and client comms. Begin managing 3–5 accounts by Week 4.",
        "known_constraints": "Limited documentation, AI tools not yet fully adopted"
    },
    "Sales Executive (Series A)": {
        "role": "Sales Executive",
        "level": "Executive",
        "area": "Sales",
        "company_size": "26–50",
        "company_stage": "Series A",
        "team_size": 2,
        "customer_facing": True,
        "manager_priorities": "Close early-stage deals, refine pitch, and build pipeline. Own 1 major client relationship.",
        "known_constraints": "No SDR support, CRM customization incomplete"
    },
    "RevOps Lead (Growth Stage)": {
        "role": "RevOps Lead",
        "level": "Manager",
        "area": "RevOps",
        "company_size": "51–200",
        "company_stage": "Growth",
        "team_size": 3,
        "customer_facing": False,
        "manager_priorities": "Optimize reporting, streamline SFDC workflows, support QBR prep.",
        "known_constraints": "Legacy data issues, unclear ownership of analytics"
    }
}

# Sidebar: API key input
with st.sidebar:
    openai_api_key = st.text_input("🔑 Enter your OpenAI API Key", type="password")
    if not openai_api_key:
        st.warning("Please enter your OpenAI API key to continue.")

# Initialize form state
if "preset_applied" not in st.session_state:
    st.session_state.preset_applied = False

with st.form("onboarding_form"):
    st.markdown("### 🎲 Guided Mode: Choose a Role Preset or Customize")
    selected_preset = st.selectbox("Select a role to prefill context:", [""] + list(role_presets.keys()))

    if selected_preset and not st.session_state.preset_applied:
        preset = role_presets[selected_preset]
        st.session_state.role = preset["role"]
        st.session_state.level = preset["level"]
        st.session_state.area = preset["area"]
        st.session_state.company_size = preset["company_size"]
        st.session_state.company_stage = preset["company_stage"]
        st.session_state.team_size = preset["team_size"]
        st.session_state.customer_facing = preset["customer_facing"]
        st.session_state.manager_priorities = preset["manager_priorities"]
        st.session_state.known_constraints = preset["known_constraints"]
        st.session_state.preset_applied = True
    elif not selected_preset:
        st.session_state.preset_applied = False

    company_website = st.text_input("🌐 Company Website (optional)", placeholder="https://example.com")
    role = st.text_input("🎯 Role", st.session_state.get("role", ""))
    level = st.selectbox("📈 Seniority Level", ["Individual Contributor", "Manager", "Senior Manager", "Director", "Executive"], index=["Individual Contributor", "Manager", "Senior Manager", "Director", "Executive"].index(st.session_state.get("level", "Individual Contributor")))
    area = st.selectbox("🧰 Functional Area", ["Customer Success", "Sales", "RevOps", "Marketing", "Operations"], index=["Customer Success", "Sales", "RevOps", "Marketing", "Operations"].index(st.session_state.get("area", "Customer Success")))
    company_size = st.selectbox("🏢 Company Size", ["1–25", "26–50", "51–200", "201–500", "501–1000", "1000+"], index=["1–25", "26–50", "51–200", "201–500", "501–1000", "1000+"].index(st.session_state.get("company_size", "1–25")))
    company_stage = st.selectbox("🚀 Company Stage", ["Seed", "Series A", "Series B", "Growth", "Enterprise"], index=["Seed", "Series A", "Series B", "Growth", "Enterprise"].index(st.session_state.get("company_stage", "Seed")))
    team_size = st.number_input("👥 Team Size", min_value=0, max_value=50, value=st.session_state.get("team_size", 0))
    customer_facing = st.checkbox("🎧 Is this a customer-facing role?", value=st.session_state.get("customer_facing", False))
    manager_priorities = st.text_area("📌 Manager's Top Priorities", st.session_state.get("manager_priorities", ""))
    known_constraints = st.text_area("⚠️ Known Constraints", st.session_state.get("known_constraints", ""))

    include_milestones = st.checkbox("✅ Include Milestone Checklist", value=True)
    include_feedback = st.checkbox("🧭 Include Coaching Feedback", value=True)
    export_format = st.selectbox("📤 Export Format", ["None", "PDF", "Markdown"])
    submitted = st.form_submit_button("Generate Plan")

    if submitted and openai_api_key:
        st.session_state.preset_applied = False  # reset for next run
        # ... downstream logic continues (already validated separately) ...
