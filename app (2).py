
import streamlit as st
import openai
import os
from fpdf import FPDF
import base64

st.set_page_config(page_title="Onboarding Plan Generator", layout="wide")

st.title("📋 AI-Powered Onboarding Plan Generator")

# Preset roles with prefilled context
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
    }
}

# Sidebar API input
with st.sidebar:
    openai_api_key = st.text_input("🔑 Enter your OpenAI API Key", type="password")
    if not openai_api_key:
        st.warning("Please enter your OpenAI API key to continue.")

# Form layout
with st.form("onboarding_form"):
    st.markdown("### 🎲 Guided Mode: Choose a Role Preset or Customize")
    selected_preset = st.selectbox("Select a role to prefill context:", [""] + list(role_presets.keys()))

    # Default values
    company_website = st.text_input("🌐 Company Website (optional)", placeholder="https://example.com")
    role = st.text_input("🎯 Role", "")
    level = st.selectbox("📈 Seniority Level", ["Individual Contributor", "Manager", "Senior Manager", "Director", "Executive"])
    area = st.selectbox("🧰 Functional Area", ["Customer Success", "Sales", "RevOps", "Marketing", "Operations"])
    company_size = st.selectbox("🏢 Company Size", ["1–25", "26–50", "51–200", "201–500", "501–1000", "1000+"])
    company_stage = st.selectbox("🚀 Company Stage", ["Seed", "Series A", "Series B", "Growth", "Enterprise"])
    team_size = st.number_input("👥 Team Size", min_value=0, max_value=50, value=0)
    customer_facing = st.checkbox("🎧 Is this a customer-facing role?")
    manager_priorities = st.text_area("📌 Manager's Top Priorities", "")
    known_constraints = st.text_area("⚠️ Known Constraints", "")

    include_milestones = st.checkbox("✅ Include Milestone Checklist")
    include_feedback = st.checkbox("🧭 Include Coaching Feedback")
    export_format = st.selectbox("📤 Export Format", ["None", "PDF", "Markdown"])
    submitted = st.form_submit_button("Generate Plan")

    if selected_preset:
        preset = role_presets[selected_preset]
        role = preset["role"]
        level = preset["level"]
        area = preset["area"]
        company_size = preset["company_size"]
        company_stage = preset["company_stage"]
        team_size = preset["team_size"]
        customer_facing = preset["customer_facing"]
        manager_priorities = preset["manager_priorities"]
        known_constraints = preset["known_constraints"]

# Generation
if submitted and openai_api_key:
    openai.api_key = openai_api_key
    enrichment_text = ""
    used_real_site = False

    if company_website:
        try:
            st.info("🔍 Attempting to enrich plan with company website...")
            browsing_prompt = f"Visit {company_website} and extract the company's mission, product description, target customer, and culture in 100-150 words."
            chat_response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes company websites."},
                    {"role": "user", "content": browsing_prompt}
                ]
            )
            enrichment_text = chat_response["choices"][0]["message"]["content"]
            used_real_site = True
        except Exception:
            st.warning("⚠️ We couldn't access the website. We'll use standard assumptions instead.")

    with st.spinner("Creating your onboarding plan..."):
        try:
            platform_phrase = "appropriate CRM, ticketing, and enablement tools" if used_real_site else "platforms like Attio (CRM), Pylon.ai (RevOps), and others"
            prompt = f"""
You are an expert in onboarding design. Create a 90-day onboarding plan for a {level} {role} in the {area} team at a {company_stage} B2B company with {company_size} employees and team size of {team_size}.

{"This role is customer-facing." if customer_facing else ""}
Manager's Top Priorities: {manager_priorities}
{"Company details: " + enrichment_text if enrichment_text else "Use general best practices for B2B SaaS companies."}

Include:
- Key learning objectives by phase (Days 0–30, 31–60, 61–90)
- Recommended tools and resources ({platform_phrase})
{"- Milestone checklist" if include_milestones else ""}
{"- Coaching guidance tailored to this level and function" if include_feedback else ""}
Known Constraints: {known_constraints or 'None'}
"""

            onboarding = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert in onboarding design."},
                    {"role": "user", "content": prompt}
                ]
            )
            output_text = onboarding["choices"][0]["message"]["content"]
            st.success("✅ Plan generated successfully!")
            st.markdown("### 📅 90-Day Onboarding Plan")
            st.markdown(output_text)

            # Export
            if export_format == "PDF":
                pdf = FPDF()
                pdf.add_page()
                pdf.set_auto_page_break(auto=True, margin=15)
                pdf.set_font("Arial", size=12)
                for line in output_text.split("\n"):
                    pdf.multi_cell(0, 10, line)
                pdf_output_path = "/mnt/data/onboarding_plan.pdf"
                pdf.output(pdf_output_path)
                with open(pdf_output_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                href = f'<a href="data:application/pdf;base64,{b64}" download="onboarding_plan.pdf">📄 Download PDF</a>'
                st.markdown(href, unsafe_allow_html=True)

            elif export_format == "Markdown":
                markdown_output_path = "/mnt/data/onboarding_plan.md"
                with open(markdown_output_path, "w") as f:
                    f.write(output_text)
                with open(markdown_output_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                href = f'<a href="data:text/markdown;base64,{b64}" download="onboarding_plan.md">📝 Download Markdown</a>'
                st.markdown(href, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ Error: {e}")

