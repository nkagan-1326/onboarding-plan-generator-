
import streamlit as st
import openai
import os

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="Onboarding Plan Generator", page_icon="📅", layout="centered")

# --- Title ---
st.title("📅 AI-Powered Onboarding Plan Generator")
st.write("Generate a tailored 30/60/90-day onboarding plan based on your team and role context.")

# --- OpenAI API Key Setup ---
openai_api_key = os.getenv("OPENAI_API_KEY")  # Allow loading from environment variable
if not openai_api_key:
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
        st.error("Please enter your OpenAI API key in the sidebar or set it as an environment variable.")
    elif not role or not manager_priorities:
        st.error("Please fill in at least the role and manager priorities.")
    else:
        st.info("Generating your onboarding plan...")

        try:
            client = openai.OpenAI(api_key=openai_api_key)

            prompt = f"""
You are a seasoned operations leader and onboarding designer creating a practical, high-impact onboarding plan.

Here’s the new hire context:
- Role: {role}
- Team Size: {team_size}
- Company Stage: {company_stage}
- Manager's Top Priorities: {manager_priorities}
- Known Constraints: {known_constraints}

Generate a customized 30/60/90-day plan that:
- Focuses on clear, measurable goals
- Includes concrete tasks with examples
- Reflects the company’s stage and team size
- Avoids generic advice
- Uses markdown with headers and bullet points

Group activities by each 30-day phase, and tailor it to the realities of a lean team with limited resources.
"""

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
