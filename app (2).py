import streamlit as st
import openai
import os

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="Onboarding Plan Generator", page_icon="📅", layout="centered")

# --- Title ---
st.title("📅 AI-Powered Onboarding Plan Generator")
st.write("Generate a 30/60/90-day onboarding plan with weekly themes, milestones, red flags, and coaching guidance.")

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
    seniority = st.selectbox("📈 Seniority Level", ["Individual Contributor", "Manager", "Executive"])
    function = st.selectbox("🛠️ Functional Area", ["Customer Success", "Revenue Operations", "Support", "Sales", "Other"])
    team_size = st.number_input("👥 Team Size", min_value=1, value=5)
    is_customer_facing = st.checkbox("🎧 Is this a customer-facing role?", value=True)
    company_stage = st.selectbox("🏢 Company Stage", ["Seed", "Series A", "Series B", "Growth", "Enterprise"])
    manager_priorities = st.text_area("📌 Manager's Top Priorities", placeholder="e.g. Build customer relationships, improve onboarding process")
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
You are an experienced onboarding architect designing a high-impact plan for a new hire.

Context:
- Role: {role}
- Seniority: {seniority}
- Function: {function}
- Team Size: {team_size}
- Customer-Facing: {"Yes" if is_customer_facing else "No"}
- Company Stage: {company_stage}
- Manager's Top Priorities: {manager_priorities}
- Known Constraints: {known_constraints}

Your task is to generate a robust onboarding plan over 90 days using the following format and principles:

1. Structure the plan into 3 phases: 0–30, 31–60, and 61–90 days.
2. For each phase, organize the content by **weekly themes** (e.g., tools, product, internal systems, pitch, reporting, cross-functional collaboration).
3. For each week, include:
   - 📚 Learning objectives
   - ✅ Milestone checklist (what should be completed)
   - 🚩 1 red flag (what's missing if milestones aren't met)
   - 🧭 Coaching notes for the manager

Incorporate best practices such as gradual complexity, varied formats (live, async, peer-led), and increasing ownership. Do not include specific tool names or proprietary details. Format output in markdown.
"""

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a strategic onboarding expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )

            output = response.choices[0].message.content
            st.markdown("### 🧾 Your 30/60/90-Day Onboarding Plan")
            st.markdown(output)

        except Exception as e:
            st.error(f"Something went wrong: {e}")
