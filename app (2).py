import streamlit as st
import openai
import os

st.set_page_config(page_title="Onboarding Plan Generator", layout="wide")

st.title("📋 AI-Powered Onboarding Plan Generator")

with st.sidebar:
    openai_api_key = st.text_input("🔑 Enter your OpenAI API Key", type="password")
    if not openai_api_key:
        st.warning("Please enter your OpenAI API key to continue.")

with st.form("onboarding_form"):
    company_website = st.text_input("🌐 Company Website (optional)", placeholder="https://example.com")
    role = st.selectbox("🎯 Role", ["Customer Success Manager", "Sales Executive", "RevOps Manager"])
    level = st.selectbox("📈 Level", ["Entry", "Mid", "Senior", "Executive"])
    company_stage = st.selectbox("🏢 Company Stage", ["Seed", "Series A", "Series B", "Growth", "Enterprise"])
    company_size = st.selectbox("👥 Company Size", ["1-10", "11-50", "51-200", "201-500", "501-1000", "1000+"])
    team_size = st.selectbox("👤 Team Size (if managing)", ["0", "1-3", "4-10", "11+"])
    known_constraints = st.text_area("⚠️ Known Constraints (optional)", placeholder="e.g., limited access to sales tools, remote-only team, etc.")
    submitted = st.form_submit_button("Generate Plan")

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
        except Exception as e:
            st.warning("⚠️ We couldn't access the website. We'll use standard assumptions instead.")
            enrichment_text = ""
            used_real_site = False

    with st.spinner("Creating your onboarding plan..."):
        try:
            if used_real_site:
                platform_phrase = "use the appropriate CRM, support system, or enablement tools"
            else:
                platform_phrase = "use platforms like Attio (CRM), Pylon.ai (RevOps), and others"

            prompt = f"""
You are an expert operations leader designing a 90-day onboarding plan for a new {role} at a {level} level.
Company stage: {company_stage}
Company size: {company_size}
Team size: {team_size}
Known constraints: {known_constraints or 'None'}

{"Here is information about the company: " + enrichment_text if enrichment_text else "Use best practices for B2B SaaS companies."}

Include key learning goals, milestones, and coaching feedback. Integrate tools the employee may need to {platform_phrase}. Adjust pacing and expectations to match company stage and role seniority.
"""

            onboarding = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert in onboarding design."},
                    {"role": "user", "content": prompt}
                ]
            )

            st.success("✅ Plan generated successfully!")
            st.markdown("### 📅 90-Day Onboarding Plan")
            st.markdown(onboarding["choices"][0]["message"]["content"])

        except Exception as e:
            st.error(f"❌ An error occurred while generating the plan: {e}")
