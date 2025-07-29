
import streamlit as st
import openai
import os

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="Onboarding Plan Generator", page_icon="📅", layout="centered")

# --- Title ---
st.title("📅 AI-Powered Onboarding Plan Generator")
st.write("Generate a role-specific, pace-adjusted 30/60/90-day onboarding plan with weekly themes, milestones, red flags, and coaching guidance.")

# --- OpenAI API Key Setup ---
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    with st.sidebar:
        st.header("🔑 API Key Setup")
        openai_api_key = st.text_input("Enter your OpenAI API key", type="password")

# --- Role Presets ---
st.subheader("🎛️ Guided Mode: Choose a Role Preset or Customize")

role_presets = {
    "Entry-level Customer Success Manager": {
        "seniority": "Individual Contributor",
        "function": "Customer Success",
        "priorities": "Ramp on product and support processes, begin managing 3–5 accounts, build strong client relationships",
        "constraints": "Lean documentation, evolving customer playbooks"
    },
    "Mid-level RevOps Manager": {
        "seniority": "Manager",
        "function": "Revenue Operations",
        "priorities": "Identify process gaps, improve forecast accuracy, support sales onboarding",
        "constraints": "Limited analytics tooling, unclear historical pipeline hygiene"
    },
    "Senior Support Lead": {
        "seniority": "Manager",
        "function": "Support",
        "priorities": "Improve ticket triage, mentor junior team, introduce SLA tracking",
        "constraints": "Legacy systems, informal escalation protocols"
    },
    "Executive Sales Leader": {
        "seniority": "Executive",
        "function": "Sales",
        "priorities": "Revamp pipeline strategy, coach managers, increase close rates",
        "constraints": "Dispersed team, inconsistent pipeline reviews"
    },
    "Custom (enter manually)": {
        "seniority": "",
        "function": "",
        "priorities": "",
        "constraints": ""
    }
}

preset_choice = st.selectbox("Select a role to prefill context:", list(role_presets.keys()))
preset = role_presets[preset_choice]

# --- Main Form ---
with st.form("onboarding_form"):
    role = st.text_input("🎯 Role", value=preset_choice if preset_choice != "Custom (enter manually)" else "")
    seniority = st.selectbox("📈 Seniority Level", ["Individual Contributor", "Manager", "Executive"], index=["Individual Contributor", "Manager", "Executive"].index(preset["seniority"]) if preset["seniority"] else 0)
    function = st.selectbox("🛠️ Functional Area", ["Customer Success", "Revenue Operations", "Support", "Sales", "Other"], index=["Customer Success", "Revenue Operations", "Support", "Sales", "Other"].index(preset["function"]) if preset["function"] else 0)
    company_size = st.selectbox("🏢 Company Size", ["1–25", "26–100", "101–500", "501–1000", "1000+"])
    company_stage = st.selectbox("🚀 Company Stage", ["Seed", "Series A", "Series B", "Growth", "Enterprise"])
    team_size = st.number_input("👥 Team Size", min_value=1, value=5)
    is_customer_facing = st.checkbox("🎧 Is this a customer-facing role?", value=True)
    manager_priorities = st.text_area("📌 Manager's Top Priorities", value=preset["priorities"])
    known_constraints = st.text_area("⚠️ Known Constraints", value=preset["constraints"])

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
- Company Size: {company_size}
- Company Stage: {company_stage}
- Team Size: {team_size}
- Customer-Facing: {"Yes" if is_customer_facing else "No"}
- Manager's Top Priorities: {manager_priorities}
- Known Constraints: {known_constraints}

Instructions:
1. Generate a 30/60/90-day onboarding plan broken into 3 phases.
2. Each phase should be structured by weekly themes.
3. For each week, include:
   - 📚 Learning objectives
   - ✅ Milestone checklist
   - 🚩 One red flag (if milestone is not met)
   - 🧭 Coaching notes for the manager

Start the output with a brief summary paragraph contextualizing the onboarding design based on the company size and stage.

Adjust the plan pacing and expectations accordingly:
- Smaller companies (<100 employees) should ramp faster, introduce broader exposure early, and expect early ownership.
- Larger companies (>500) may stretch onboarding timelines, introduce structured immersion, and defer ownership.
- Consider resource availability, documentation maturity, and typical enablement practices for each size/stage.

Generate the full 90-day plan across all 12 weeks, even if early independence is achieved. Later weeks can focus on deepening expertise, mentoring others, or contributing strategically.

Avoid generic filler. Tailor the outputs to the context. Format in markdown.
"""

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a strategic onboarding expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2500
            )

            output = response.choices[0].message.content
            st.markdown("### 🧾 Your 30/60/90-Day Onboarding Plan")
            st.markdown(output)

        except Exception as e:
            st.error(f"Something went wrong: {e}")
