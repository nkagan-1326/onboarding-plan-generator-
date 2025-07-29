
import streamlit as st
import openai
import os

# --- Configuration ---
st.set_page_config(page_title="Onboarding Plan Generator", page_icon="📅", layout="centered")

# --- Title ---
st.title("📅 AI-Powered Onboarding Plan Generator")
st.write("Generate a tailored 30/60/90-day onboarding plan based on your team and role context.")

# --- Sidebar: OpenAI API Key ---
with st.sidebar:
    st.header("🔑 API Key Setup")
    openai_api_key = st.text_input("Enter your OpenAI API key", type="password")
    st.markdown("Don't have one? Get it [here](https://platform.openai.com/account/api-keys).")

# --- Main Form ---
with st.form("onboarding_form"):
    role = st.text_input("🎯 Role", placeholder="e.g. Customer Success Manager")
    team_size = st.number_input("👥 Team Size", min_value=1, value=5)
    company_stage = st.selectbox("🏢 Company Stage", ["Seed", "Series A", "Series B", "Growth", "Enterprise"])
    manager_priorities = st.text_area("📌 Manager's Top Priorities", placeholder="e.g. Build client relationships, improve onboarding process")
    known_constraints = st.text_area("⚠️ Known Constraints", placeholder="e.g. Limited documentation, complex product")

    submitted = st.form_submit_button("Generate Plan")

# --- Generate Plan ---
if submitted:
    if not openai_api_key:
        st.error("Please enter your OpenAI API key in the sidebar.")
    elif not role or not manager_priorities:
        st.error("Please fill in at least the role and manager priorities.")
    else:
        st.info("Generating your onboarding plan...")

        openai.api_key = openai_api_key

        prompt = f"""
You are an experienced operations leader designing onboarding plans. Given the context below, generate a detailed 30/60/90-day onboarding plan for a new hire.

Role: {role}
Team Size: {team_size}
Company Stage: {company_stage}
Manager's Top Priorities: {manager_priorities}
Known Constraints: {known_constraints}

Output the plan in markdown format with clear headings for each phase.
"""

        try:
            client = openai.OpenAI(api_key=openai_api_key)

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a strategic onboarding expert."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.7,
    max_tokens=1000
)

output = response.choices[0].message.content
st.markdown("### 🧾 Your 30/60/90-Day Onboarding Plan")
st.markdown(output)

except Exception as e:
    st.error(f"Something went wrong: {e}")

        except Exception as e:
            st.error(f"Something went wrong: {e}")
