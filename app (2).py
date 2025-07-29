
import streamlit as st
from io import BytesIO
from fpdf import FPDF

# --- Website Scraper (Stubbed) ---
def scrape_company_website(url):
    try:
        if not url.startswith("http"):
            url = "https://" + url
        return {
            "mission": "Empower teams through intelligent automation.",
            "vision": "To be the leading AI-first platform for scaling B2B operations.",
            "product": "AI-powered CRM and onboarding tools for sales and RevOps teams.",
            "tech_stack": "category"
        }
    except:
        return None

# --- Plan Generator ---
def generate_onboarding_plan(role, stage, size, seniority, website_data):
    tech_stack = {
        "CRM": "Attio" if website_data["tech_stack"] != "category" else "CRM system",
        "Analytics": "Pylon.ai" if website_data["tech_stack"] != "category" else "analytics platform",
        "Support": "Intercom" if website_data["tech_stack"] != "category" else "support ticketing tool"
    }

    milestones = [
        "Week 1: Orientation, system access, intro to mission, vision, product.",
        "Week 2: Shadowing, training on tools, light project work.",
        "Week 3: Independent execution, stakeholder communication, early feedback loop.",
        "Week 4: Reflect, request feedback, set goals for 30/60/90 ramp."
    ]

    coaching = {
        "junior": "- Build strong habits early
- Ask questions proactively
- Get familiar with tools and process",
        "mid": "- Balance learning and doing
- Begin to own deliverables
- Build internal relationships",
        "senior": "- Drive clarity in ambiguity
- Mentor others
- Build cross-functional partnerships",
        "executive": "- Align org to strategy
- Demonstrate leadership influence
- Evaluate team structure and gaps"
    }

    red_flags = {
        "universal": [
            "- Lack of communication",
            "- Not seeking clarity when blocked",
            "- Poor time management or missed check-ins"
        ]
    }

    output = f"""
# Onboarding Plan: {role}

## Company Details
- **Stage**: {stage}
- **Size**: {size}
- **Mission**: {website_data['mission']}
- **Vision**: {website_data['vision']}
- **Product**: {website_data['product']}

---

## Weekly Milestones
""" + "\n".join([f"- {m}" for m in milestones]) + f"""

---

## Coaching Guidance ({seniority.title()})
{coaching.get(seniority.lower(), 'N/A')}

---

## Known Constraints / Red Flags
""" + "\n".join(red_flags["universal"]) + f"""

---

## Tech Stack
- CRM: {tech_stack['CRM']}
- Analytics: {tech_stack['Analytics']}
- Support: {tech_stack['Support']}
"""
    return output

# --- Export Helpers ---
def convert_to_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in text.split('\n'):
        pdf.multi_cell(0, 10, line)
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

def convert_to_markdown(text):
    buffer = BytesIO()
    buffer.write(text.encode())
    buffer.seek(0)
    return buffer

# --- UI ---
st.set_page_config("AI-Powered Onboarding Plan Generator", layout="centered")
st.title("🧠 AI-Powered Onboarding Plan Generator")

with st.form("input_form"):
    role = st.text_input("Role", placeholder="e.g. Sales Engineer")
    stage = st.selectbox("Company Stage", ["Seed", "Series A", "Series B", "Growth", "Enterprise"])
    size = st.selectbox("Company Size", ["1-10", "11-50", "51-200", "201-1000", "1000+"])
    seniority = st.selectbox("Seniority Level", ["Junior", "Mid", "Senior", "Executive"])
    website = st.text_input("Company Website (optional)")
    submitted = st.form_submit_button("Generate Onboarding Plan")

if submitted:
    site_data = scrape_company_website(website) if website else {
        "mission": "Default B2B SaaS mission.",
        "vision": "Default vision for high-growth tech orgs.",
        "product": "Default AI-first GTM tools.",
        "tech_stack": "specific"
    }
    plan = generate_onboarding_plan(role, stage, size, seniority, site_data)
    st.markdown(plan)

    st.download_button("📄 Export as PDF", convert_to_pdf(plan), file_name="onboarding_plan.pdf", mime="application/pdf")
    st.download_button("📝 Export as Markdown", convert_to_markdown(plan), file_name="onboarding_plan.md", mime="text/markdown")
