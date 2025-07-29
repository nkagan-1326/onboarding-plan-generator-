
import streamlit as st
import openai
import os
import requests
from bs4 import BeautifulSoup

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="Onboarding Plan Generator", page_icon="📅", layout="centered")

st.title("📅 AI-Powered Onboarding Plan Generator")
st.write("Generate a role-specific, B2B onboarding plan with weekly milestones, red flags, and coaching guidance — all tailored by company stage and tech stack.")

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
        "priorities": "Ramp on product, support processes, and client comms. Begin managing 3–5 accounts by Week 4.",
        "constraints": "Limited documentation, AI tools not yet fully adopted"
    },
    "Mid-level RevOps Manager": {
        "seniority": "Manager",
        "function": "Revenue Operations",
        "priorities": "Optimize GTM data flow, improve forecast accuracy, support sales enablement.",
        "constraints": "Siloed tooling, growing demand for dashboarding"
    },
    "Sales Executive": {
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

# --- Website enrichment ---
def scrape_company_metadata(url):
    try:
        if not url.startswith("http"):
            url = "https://" + url
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string.strip() if soup.title else ""
        meta_desc = ""
        for tag in soup.find_all("meta"):
            if tag.get("name", "").lower() == "description":
                meta_desc = tag.get("content", "").strip()
                break

        h1 = soup.find("h1")
        first_p = soup.find("p")
        extra = ""
        if not meta_desc and h1:
            extra = h1.get_text().strip()
        elif not meta_desc and first_p:
            extra = first_p.get_text().strip()

        content_snippet = meta_desc or extra or "No readable description found."

        return {
            "success": True,
            "title": title,
            "description": content_snippet,
            "product": url.split("//")[-1].split("/")[0],
            "raw": response.text[:300]
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# --- Main Form ---
with st.form("onboarding_form"):
    company_website = st.text_input("🌐 Company Website (optional)", placeholder="https://example.com")
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

        website_metadata = None
        generic_stack = False
        if company_website:
            website_metadata = scrape_company_metadata(company_website)
            if not website_metadata["success"]:
                st.warning(f"We couldn't access or parse that website. Reason: {website_metadata['error']}")
            else:
                generic_stack = True
                st.success(f"Website description: {website_metadata['description'][:200]}")

        try:
            client = openai.OpenAI(api_key=openai_api_key)

            prompt = f"""
You are an experienced onboarding architect designing a high-impact plan for a new hire at a B2B company.

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
{"- Company Website Metadata: " + website_metadata['description'] + " (" + website_metadata['product'] + ")" if website_metadata and website_metadata['success'] else ""}

Instructions:
1. Assume the company is a B2B company.
2. {"Refer to tech stack categories only (e.g., 'CRM', 'ticketing system', 'marketing automation') and avoid naming specific tools or vendors." if generic_stack else "If no website is provided or parsing failed, base platform assumptions on company stage:\n- CRM: Use Attio for Seed–Series B; Salesforce for Growth+.\n- RevOps Tools: Include Pylon.ai for Seed–Series B. Add Clari and Gong for B+.\n- Customer Success: Use Vitally or Gainsight depending on stage.\n- Support: Use Intercom or Zendesk AI depending on stage.\n- All roles should include ramp on these tools as part of onboarding."}

3. Generate a 30/60/90-day onboarding plan broken into 3 phases.
4. Each phase should be structured by weekly themes.
5. For each week, include:
   - 📚 Learning objectives
   - ✅ Milestone checklist
   - 🚩 One red flag (if milestone is not met)
   - 🧭 Coaching notes for the manager

Start with a summary paragraph explaining the onboarding design, considering the company size, stage, and role. Adjust pacing:
- Smaller companies (<100) should ramp quickly and broadly.
- Larger companies (>500) should allow structured immersion.

Use relevant language based on company metadata if available. Format the full plan using markdown.
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
