
import streamlit as st
import openai
from fpdf import FPDF
import requests
from bs4 import BeautifulSoup
import base64

# --- CONFIGURATION ---
st.set_page_config(page_title="Onboarding Plan Generator", layout="wide")
st.title("📋 AI-Powered Onboarding Plan Generator")

# --- API Key Input ---
with st.sidebar:
    openai.api_key = st.text_input("🔐 Enter your OpenAI API Key", type="password")
    if not openai.api_key:
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

# --- Stage-based AI-first Tech Stack ---
ai_tech_stack = {
    "Seed": {
        "CRM": "Attio",
        "Customer Success Platform": "Pylon.ai",
        "Enablement": "Notion",
        "Ticketing": "Zendesk"
    },
    "Series A": {
        "CRM": "HubSpot",
        "Customer Success Platform": "Gainsight Essentials",
        "Enablement": "Gong",
        "Ticketing": "Freshdesk"
    },
    "Series B": {
        "CRM": "Salesforce",
        "Customer Success Platform": "Catalyst",
        "Enablement": "Gong",
        "Ticketing": "Zendesk"
    }
}

# --- Helpers ---
def extract_website_info(url):
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string if soup.title else ""
        metas = soup.find_all("meta")
        description = " ".join([m.get("content", "") for m in metas if m.get("name") in ["description", "og:description"]])
        return f"{title}. {description}".strip()
    except Exception:
        return ""

def generate_prompt(context):
    tech_info = ai_tech_stack.get(context["company_stage"], {})
    tech_line = (
        "Use generic tool categories (e.g. CRM, Ticketing, Enablement Platform) for tech stack references."
        if context["enriched"] else
        "Assume tools like " + ", ".join([f"{k}: {v}" for k, v in tech_info.items()])
    )

    return f"""
You're an expert in onboarding design for B2B startups. Create a 90-day onboarding plan for:

Role: {context["role"]}
Seniority: {context["seniority_level"]}
Function: {context["functional_area"]}
Company Stage: {context["company_stage"]}
Company Size: {context["company_size"]}
Team Size: {context["team_size"]}
Customer-Facing: {"Yes" if context["is_customer_facing"] else "No"}
Manager's Top Priorities: {context["manager_priorities"]}
Known Constraints: {context["known_constraints"]}
{f"Company Context: {context['website_info']}" if context["enriched"] else ""}

Requirements:
- Organize into 3 phases: Days 1–30, 31–60, 61–90
- Each phase should include:
  - Learning Objectives
  - Milestone Checklist
  - Coaching & Feedback Guidance (tailored to seniority)
  - Tools and Resources ({tech_line})
- Finish with a Red Flags & Remediation section
- Use clean markdown formatting with headers and bullet points.
"""

def export_pdf(content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in content.split("\n"):
        pdf.multi_cell(0, 10, line)
    path = "/mnt/data/onboarding_plan.pdf"
    pdf.output(path)
    return path

# --- FORM UI ---
preset_choice = st.selectbox("🎯 Use a Role Preset (or Customize Below)", [""] + list(role_presets.keys()))
preset = role_presets.get(preset_choice, {})

with st.form("form"):
    col1, col2 = st.columns(2)
    with col1:
        role = st.text_input("Role", value=preset.get("role", ""))
        seniority = st.selectbox("Seniority Level", ["Individual Contributor", "Manager", "Executive"], index=["Individual Contributor", "Manager", "Executive"].index(preset.get("seniority_level", "Individual Contributor")))
        function = st.selectbox("Functional Area", ["Sales", "Marketing", "Customer Success", "RevOps", "Engineering"], index=["Sales", "Marketing", "Customer Success", "RevOps", "Engineering"].index(preset.get("functional_area", "Customer Success")))
        company_stage = st.selectbox("Company Stage", ["Seed", "Series A", "Series B", "Growth"], index=["Seed", "Series A", "Series B", "Growth"].index(preset.get("company_stage", "Seed")))
    with col2:
        company_size = st.selectbox("Company Size", ["1–25", "26–100", "101–500", "500+"], index=["1–25", "26–100", "101–500", "500+"].index(preset.get("company_size", "1–25")))
        team_size = st.number_input("Team Size", min_value=1, value=preset.get("team_size", 5))
        customer_facing = st.checkbox("Is Customer-Facing?", value=preset.get("is_customer_facing", False))
        website = st.text_input("Company Website (optional)", "")

    priorities = st.text_area("Manager's Top Priorities", value=preset.get("manager_priorities", "Ramp up, start owning deliverables by Week 4."))
    constraints = st.text_area("Known Constraints", value=preset.get("known_constraints", "Limited documentation, early tooling."))

    submitted = st.form_submit_button("🚀 Generate Plan")

# --- PLAN GENERATION ---
if submitted and openai.api_key:
    with st.spinner("Generating onboarding plan..."):
        website_info = extract_website_info(website) if website else ""
        enriched = bool(website_info)

        prompt = generate_prompt({
            "role": role,
            "seniority_level": seniority,
            "functional_area": function,
            "company_stage": company_stage,
            "company_size": company_size,
            "team_size": team_size,
            "is_customer_facing": customer_facing,
            "manager_priorities": priorities,
            "known_constraints": constraints,
            "website_info": website_info,
            "enriched": enriched
        })

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "system", "content": prompt}]
            )
            output = response.choices[0].message.content
            st.success("✅ Plan generated successfully!")

            # Render markdown
            st.markdown(output)

            # Export options
            st.download_button("⬇️ Download Markdown", output, file_name="onboarding_plan.md")
            pdf_path = export_pdf(output)
            with open(pdf_path, "rb") as f:
                st.download_button("📄 Download PDF", f, file_name="onboarding_plan.pdf")

        except Exception as e:
            st.error(f"OpenAI API error: {e}")
