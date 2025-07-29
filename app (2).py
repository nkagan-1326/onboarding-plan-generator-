
import streamlit as st
import openai
from fpdf import FPDF
import os
import markdown
import requests
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
st.set_page_config(page_title="AI-Powered Onboarding Plan Generator", layout="wide")

# --- SIDEBAR: API Key ---
with st.sidebar:
    openai_api_key = st.text_input("🔐 Enter your OpenAI API Key", type="password")

# --- ROLE PRESETS ---
role_presets = {
    "Entry-level Customer Success Manager": {
        "role": "Entry-level Customer Success Manager",
        "seniority_level": "Individual Contributor",
        "functional_area": "Customer Success",
        "company_size": "1–25",
        "company_stage": "Seed",
        "team_size": 5,
        "is_customer_facing": True,
        "manager_priorities": "Ramp on product, support processes, and client comms. Begin managing 3–5 accounts by Week 4.",
        "known_constraints": "Limited documentation, AI tools not yet fully adopted"
    },
    "Senior Sales Executive": {
        "role": "Senior Sales Executive",
        "seniority_level": "Executive",
        "functional_area": "Sales",
        "company_size": "26–100",
        "company_stage": "Series B",
        "team_size": 3,
        "is_customer_facing": True,
        "manager_priorities": "Drive pipeline, close initial strategic accounts, build repeatable sales process.",
        "known_constraints": "Early stage ICP, basic CRM setup, SDR support still scaling"
    },
    "RevOps Lead": {
        "role": "Revenue Operations Lead",
        "seniority_level": "Manager",
        "functional_area": "RevOps",
        "company_size": "26–100",
        "company_stage": "Series A",
        "team_size": 2,
        "is_customer_facing": False,
        "manager_priorities": "Build scalable systems for reporting, forecasting, and pipeline management.",
        "known_constraints": "Siloed data, no unified tech stack yet"
    }
}

# --- STAGE-BASED TECH STACK ASSUMPTIONS ---
stage_tech_stack = {
    "Seed": {
        "CRM": "Attio",
        "Customer Success Platform": "Pylon.ai",
        "Enablement": "Notion",
        "Support/Ticketing": "Zendesk"
    },
    "Series A": {
        "CRM": "HubSpot",
        "Customer Success Platform": "Gainsight Essentials",
        "Enablement": "Gong",
        "Support/Ticketing": "Freshdesk"
    },
    "Series B": {
        "CRM": "Salesforce",
        "Customer Success Platform": "Catalyst",
        "Enablement": "Gong",
        "Support/Ticketing": "Zendesk"
    }
}

# --- HELPER: Website Enrichment ---
def extract_website_info(url):
    try:
        resp = requests.get(url, timeout=5)
        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.title.string if soup.title else ""
        metas = soup.find_all("meta")
        meta_text = " ".join([m.get("content", "") for m in metas if m.get("name") in ["description", "og:description"]])
        return f"{title}. {meta_text}".strip()
    except Exception:
        return ""

# --- HELPER: Generate Plan ---
def generate_onboarding_plan(**kwargs):
    if not openai_api_key:
        st.error("Please enter your OpenAI API Key in the sidebar.")
        return None

    openai_client = openai.OpenAI(api_key=openai_api_key)

    # Build system prompt
    website_info = extract_website_info(kwargs["company_website"]) if kwargs["company_website"] else None
    tech_stack = stage_tech_stack.get(kwargs["company_stage"], {})
    tech_section = (
        "Use category labels like 'CRM', 'Support System', 'Enablement Platform' for tools mentioned." 
        if website_info else
        f"Use these tools in your recommendations: {', '.join([f'{k}: {v}' for k,v in tech_stack.items()])}."
    )

    prompt = f"""
You're an expert onboarding designer for B2B startups. Create a structured 90-day onboarding plan for the following role:
- Role: {kwargs["role"]}
- Seniority: {kwargs["seniority_level"]}
- Department: {kwargs["functional_area"]}
- Company size: {kwargs["company_size"]}
- Stage: {kwargs["company_stage"]}
- Team size: {kwargs["team_size"]}
- Customer-facing: {kwargs["is_customer_facing"]}
- Manager's Top Priorities: {kwargs["manager_priorities"]}
- Known Constraints: {kwargs["known_constraints"]}
{f"- Company context: {website_info}" if website_info else ""}
{tech_section}

Structure the output in 3 phases:
1. Phase 1 (Days 1–30): Learning & Integration
2. Phase 2 (Days 31–60): Application & Collaboration
3. Phase 3 (Days 61–90): Mastery & Independence

Each phase should include:
- Key Learning Objectives
- Milestone Checklist (3–5)
- Recommended Tools and Resources
- Coaching Guidance tailored to the role's seniority

End with a Red Flags & Remediation section.
Output should be structured with headers and bullet points.
    """

    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}],
        temperature=0.5
    )

    return response.choices[0].message.content.strip()

# --- FORM ---
st.title("🧭 AI-Powered Onboarding Plan Generator")

preset_name = st.selectbox("🧩 Guided Mode: Choose a Role Preset or Customize", [""] + list(role_presets.keys()))
preset = role_presets.get(preset_name, {})

with st.form("onboarding_form"):
    col1, col2 = st.columns(2)
    with col1:
        company_website = st.text_input("🌐 Company Website (optional)", value=preset.get("company_website", ""))
        role = st.text_input("🎯 Role", value=preset.get("role", ""))
        seniority_level = st.selectbox("🪪 Seniority Level", ["Individual Contributor", "Manager", "Executive"], index=["Individual Contributor", "Manager", "Executive"].index(preset.get("seniority_level", "Individual Contributor")))
        functional_area = st.selectbox("🧭 Functional Area", ["Sales", "Marketing", "Customer Success", "RevOps", "Engineering"], index=["Sales", "Marketing", "Customer Success", "RevOps", "Engineering"].index(preset.get("functional_area", "Customer Success")))
    with col2:
        company_size = st.selectbox("🏢 Company Size", ["1–25", "26–100", "101–500", "500+"], index=["1–25", "26–100", "101–500", "500+"].index(preset.get("company_size", "1–25")))
        company_stage = st.selectbox("🚀 Company Stage", ["Seed", "Series A", "Series B", "Growth"], index=["Seed", "Series A", "Series B", "Growth"].index(preset.get("company_stage", "Seed")))
        team_size = st.number_input("👥 Team Size", min_value=1, value=preset.get("team_size", 5))
        is_customer_facing = st.checkbox("🎧 Is this a customer-facing role?", value=preset.get("is_customer_facing", True))

    manager_priorities = st.text_area("📌 Manager's Top Priorities", value=preset.get("manager_priorities", "Define short-term goals, such as managing specific accounts or launching a campaign by Week 4."))
    known_constraints = st.text_area("⚠️ Known Constraints", value=preset.get("known_constraints", "Limited documentation, early-stage tooling, AI not fully adopted."))

    submitted = st.form_submit_button("Generate Plan")

# --- OUTPUT ---
if submitted:
    with st.spinner("Generating onboarding plan..."):
        plan = generate_onboarding_plan(
            company_website=company_website,
            role=role,
            seniority_level=seniority_level,
            functional_area=functional_area,
            company_size=company_size,
            company_stage=company_stage,
            team_size=team_size,
            is_customer_facing=is_customer_facing,
            manager_priorities=manager_priorities,
            known_constraints=known_constraints
        )
    if plan:
        st.markdown(plan)

        # Export buttons
        st.download_button("📥 Download as Markdown", plan, file_name="onboarding_plan.md")
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)
        for line in plan.split("\n"):
            pdf.multi_cell(0, 10, line)
        pdf_path = "onboarding_plan.pdf"
        pdf.output(pdf_path)
        with open(pdf_path, "rb") as f:
            st.download_button("📄 Download as PDF", f, file_name="onboarding_plan.pdf")
