
import streamlit as st
from openai import OpenAI
from fpdf import FPDF
import base64

st.set_page_config(page_title="📋 Onboarding Plan Generator", layout="wide")
st.title("📋 AI-Powered Onboarding Plan Generator")

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

with st.sidebar:
    openai_api_key = st.text_input("🔑 Enter your OpenAI API Key", type="password")
    if not openai_api_key:
        st.warning("Please enter your OpenAI API key to continue.")

if "preset_applied" not in st.session_state:
    st.session_state.preset_applied = False

with st.form("onboarding_form"):
    st.markdown("### 🎲 Guided Mode: Choose a Role Preset or Customize")
    selected_preset = st.selectbox("Select a role to prefill context:", [""] + list(role_presets.keys()))

    if selected_preset and not st.session_state.preset_applied:
        preset = role_presets[selected_preset]
        for key, value in preset.items():
            st.session_state[key] = value
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
    manager_priorities = st.text_area("📌 Manager's Top Priorities", value=st.session_state.get("manager_priorities", "e.g. Ramp on product, close deals, build pipeline"))
    known_constraints = st.text_area("⚠️ Known Constraints", value=st.session_state.get("known_constraints", "e.g. Limited documentation, incomplete tooling"))

    include_milestones = st.checkbox("✅ Include Milestone Checklist", value=True)
    include_feedback = st.checkbox("🧭 Include Coaching Feedback", value=True)
    export_format = st.selectbox("📤 Export Format", ["None", "PDF", "Markdown"])
    submitted = st.form_submit_button("Generate Plan")

if submitted and openai_api_key:
    client = OpenAI(api_key=openai_api_key)

    enrichment_text = ""
    used_real_site = False
    if company_website:
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes company websites."},
                    {"role": "user", "content": f"Visit {company_website} and extract the company's mission, product description, target customer, and culture in 100-150 words."}
                ]
            )
            enrichment_text = response.choices[0].message.content
            used_real_site = True
        except Exception:
            st.warning("⚠️ Website access failed — using defaults.")

    with st.spinner("Creating your onboarding plan..."):
        try:
            platform_description = "appropriate CRM, ticketing, and enablement tools" if used_real_site else "platforms like Attio (CRM), Pylon.ai (RevOps), and others"

            prompt = f"""
You are an expert in onboarding design. Create a 90-day onboarding plan for a {level} {role} in the {area} team at a {company_stage} B2B company with {company_size} employees and team size of {team_size}.
{"This role is customer-facing." if customer_facing else ""}
Manager's Top Priorities: {manager_priorities}
{"Company details: " + enrichment_text if enrichment_text else "Use general best practices for B2B SaaS companies."}

Include:
- Key learning objectives by phase (Days 0–30, 31–60, 61–90)
- Recommended tools and resources ({platform_description})
{"- Milestone checklist" if include_milestones else ""}
{"- Coaching guidance tailored to this level and function" if include_feedback else ""}
Known Constraints: {known_constraints or 'None'}
"""

            plan_response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert in onboarding design."},
                    {"role": "user", "content": prompt}
                ]
            )
            output_text = plan_response.choices[0].message.content
            st.success("✅ Plan generated successfully!")
            st.markdown("### 📅 90-Day Onboarding Plan")
            st.markdown(output_text)

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
                st.markdown(f'<a href="data:application/pdf;base64,{b64}" download="onboarding_plan.pdf">📄 Download PDF</a>', unsafe_allow_html=True)

            elif export_format == "Markdown":
                markdown_output_path = "/mnt/data/onboarding_plan.md"
                with open(markdown_output_path, "w") as f:
                    f.write(output_text)
                with open(markdown_output_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                st.markdown(f'<a href="data:text/markdown;base64,{b64}" download="onboarding_plan.md">📝 Download Markdown</a>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ Error: {e}")
