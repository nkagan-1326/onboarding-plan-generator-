
import streamlit as st
from openai import OpenAI
from fpdf import FPDF
import requests
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
st.set_page_config(page_title="Onboarding Plan Generator", layout="wide")
st.title("📋 AI-Powered Onboarding Plan Generator")

# --- SIDEBAR: API Key ---
with st.sidebar:
    openai_api_key = st.text_input("🔐 Enter your OpenAI API Key", type="password")
    if not openai_api_key:
        st.warning("Please enter your OpenAI API key to continue.")

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

# --- TECH STACK LOGIC ---
ai_tech_stack = {
    "Seed": {"CRM": "Attio", "CS Platform": "Pylon.ai", "Enablement": "Notion", "Ticketing": "Zendesk"},
    "Series A": {"CRM": "HubSpot", "CS Platform": "Gainsight Essentials", "Enablement": "Gong", "Ticketing": "Freshdesk"},
    "Series B": {"CRM": "Salesforce", "CS Platform": "Catalyst", "Enablement": "Gong", "Ticketing": "Zendesk"}
}

# --- Helper: Enrichment ---
def extract_website_info(url):
    try:
        resp = requests.get(url, timeout=5)
        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.title.string if soup.title else ""
        metas = soup.find_all("meta")
        description = " ".join([m.get("content", "") for m in metas if m.get("name") in ["description", "og:description"]])
        return f"{title}. {description}".strip()
    except Exception:
        return ""

# --- Helper: Prompt Builder ---
def build_prompt(context):
    tools = ai_tech_stack.get(context["company_stage"], {})
    tools_text = (
        "Use generic labels (e.g. CRM, CS Platform) instead of tool names."
        if context["enriched"]
        else "Assume tools like: " + ", ".join([f"{k}: {v}" for k, v in tools.items()])
    )
    return f"""
You are an expert in onboarding design for B2B companies. Create a structured 90-day onboarding plan.

Role: {context["role"]}
Seniority: {context["seniority_level"]}
Function: {context["functional_area"]}
Stage: {context["company_stage"]}, Size: {context["company_size"]}, Team Size: {context["team_size"]}
Customer-Facing: {"Yes" if context["is_customer_facing"] else "No"}
Manager Priorities: {context["manager_priorities"]}
Constraints: {context["known_constraints"]}
{f"Company Website Info: {context['website_info']}" if context["enriched"] else ""}
{tools_text}

Format:
- Days 1–30: Learning Objectives, Milestones, Coaching Guidance, Tools
- Days 31–60: same
- Days 61–90: same
- Red Flags & Remediation
Use markdown headers and bullet points.
"""

# --- PDF Export ---
def export_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in text.split("\n"):
        pdf.multi_cell(0, 10, line)
    path = "/mnt/data/onboarding_plan.pdf"
    pdf.output(path)
    return path

# --- FORM UI ---
preset_choice = st.selectbox("🎯 Choose Role Preset (or Customize)", [""] + list(role_presets.keys()))
preset = role_presets.get(preset_choice, {})

with st.form("form"):
    col1, col2 = st.columns(2)
    with col1:
        role = st.text_input("Role", value=preset.get("role", ""))
        seniority = st.selectbox("Seniority", ["Individual Contributor", "Manager", "Executive"], index=["Individual Contributor", "Manager", "Executive"].index(preset.get("seniority_level", "Individual Contributor")))
        function = st.selectbox("Function", ["Sales", "Marketing", "Customer Success", "RevOps", "Engineering"], index=["Sales", "Marketing", "Customer Success", "RevOps", "Engineering"].index(preset.get("functional_area", "Customer Success")))
        company_stage = st.selectbox("Stage", ["Seed", "Series A", "Series B"], index=["Seed", "Series A", "Series B"].index(preset.get("company_stage", "Seed")))
    with col2:
        company_size = st.selectbox("Size", ["1–25", "26–100", "101–500", "500+"], index=["1–25", "26–100", "101–500", "500+"].index(preset.get("company_size", "1–25")))
        team_size = st.number_input("Team Size", min_value=1, value=preset.get("team_size", 5))
        is_customer_facing = st.checkbox("Customer-Facing", value=preset.get("is_customer_facing", False))
        website = st.text_input("Company Website (optional)", "")

    manager_priorities = st.text_area("📌 Manager's Top Priorities", value=preset.get("manager_priorities", "Ramp on product, close deals, build pipeline."))
    known_constraints = st.text_area("⚠️ Known Constraints", value=preset.get("known_constraints", "Limited documentation, AI not adopted."))

    submitted = st.form_submit_button("Generate Plan")

# --- ON SUBMIT ---
if submitted and openai_api_key:
    client = OpenAI(api_key=openai_api_key)

    website_info = extract_website_info(website) if website else ""
    enriched = bool(website_info)

    prompt = build_prompt({
        "role": role,
        "seniority_level": seniority,
        "functional_area": function,
        "company_stage": company_stage,
        "company_size": company_size,
        "team_size": team_size,
        "is_customer_facing": is_customer_facing,
        "manager_priorities": manager_priorities,
        "known_constraints": known_constraints,
        "website_info": website_info,
        "enriched": enriched
    })

    try:
        with st.spinner("Generating onboarding plan..."):
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
            plan = response.choices[0].message.content
            st.markdown(plan)
            st.download_button("⬇️ Download Markdown", plan, file_name="onboarding_plan.md")
            pdf_path = export_pdf(plan)
            with open(pdf_path, "rb") as f:
                st.download_button("📄 Download PDF", f, file_name="onboarding_plan.pdf")
    except Exception as e:
        st.error(f"❌ OpenAI Error: {e}")
