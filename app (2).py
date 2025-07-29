import streamlit as st
from io import BytesIO
from fpdf import FPDF

# Stubbed scraper (replace with real scraper logic if needed)
def scrape_company_website(url):
    try:
        if not url.startswith("http"):
            url = "https://" + url
        # Fallback simulated values
        return {
            "mission": "Empower teams through intelligent automation.",
            "vision": "To be the leading AI-first platform for scaling B2B operations.",
            "product": "AI-powered CRM and onboarding tools for sales and RevOps teams.",
            "tech_stack": "category"  # Use category labels if site is successfully parsed
        }
    except:
        return None

def generate_onboarding_plan(role, stage, size, seniority, website_data):
    tech_stack = {
        "CRM": "Attio" if website_data["tech_stack"] != "category" else "CRM",
        "Analytics": "Pylon.ai" if website_data["tech_stack"] != "category" else "BI/analytics platform",
        "Support": "Intercom" if website_data["tech_stack"] != "category" else "ticketing system"
    }

    coaching = {
        "junior": "- Ask questions early and often\n- Build trust through reliability\n- Learn before optimizing",
        "mid": "- Balance execution with learning\n- Take initiative on small wins\n- Clarify priorities with manager",
        "senior": "- Lead cross-functional workstreams\n- Identify gaps and propose solutions\n- Mentor newer teammates",
        "executive": "- Build relationships with other execs\n- Shape org structure and KPIs\n- Drive strategic alignment"
    }

    red_flags = "- Lack of curiosity or proactivity\n- Poor communication with manager or team\n- Delays in early milestones"

    return f"""
# Onboarding Plan for {role.title()}

## Company Context
- **Stage**: {stage}
- **Size**: {size}
- **Mission**: {website_data['mission']}
- **Vision**: {website_data['vision']}
- **Product**: {website_data['product']}

---

## Weekly Milestones

### Week 1: Orientation & Setup
- Meet your team and key stakeholders
- Understand mission, vision, values
- Set up core systems: {tech_stack['CRM']}, {tech_stack['Analytics']}, {tech_stack['Support']}

### Week 2: Deep Dives & Workflow Exposure
- Shadow team members and understand workflows
- Document existing processes and questions
- Begin hands-on use of tools

### Week 3: Independent Execution
- Take ownership of a scoped deliverable
- Communicate progress in stand-ups and async updates
- Begin defining what success looks like in role

### Week 4: Feedback & Expansion
- Conduct self-review + request feedback
- Identify growth areas and propose improvements
- Discuss 30-60-90 plan updates with manager

---

## Coaching Guidance ({seniority.title()})
{coaching.get(seniority.lower(), 'No guidance available.')}

---

## Known Constraints & Red Flags
{red_flags}

---

## Tech Stack Assumptions
- **CRM**: {tech_stack['CRM']}
- **Analytics**: {tech_stack['Analytics']}
- **Support Tool**: {tech_stack['Support']}
"""

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

def convert_to_markdown_file(text):
    buffer = BytesIO()
    buffer.write(text.encode())
    buffer.seek(0)
    return buffer

# ------------------- Streamlit UI -------------------

st.set_page_config(page_title="AI Onboarding Plan Generator", layout="centered")
st.title("🧠 AI-Powered Onboarding Plan Generator")

with st.form("inputs"):
    role = st.text_input("🔧 Role", placeholder="e.g. Customer Success Manager", key="role")
    stage = st.selectbox("📈 Company Stage", ["Seed", "Series A", "Series B", "Growth", "Enterprise"], key="stage")
    size = st.selectbox("🏢 Company Size", ["1-10", "11-50", "51-200", "201-1000", "1000+"], key="size")
    seniority = st.selectbox("🧑‍💼 Seniority Level", ["Junior", "Mid", "Senior", "Executive"], key="seniority")
    website_url = st.text_input("🌐 Company Website (optional)", placeholder="https://example.com", key="website")
    submitted = st.form_submit_button("Generate Plan")

if submitted:
    with st.spinner("Generating personalized onboarding plan..."):
        website_data = scrape_company_website(website_url) if website_url else {
            "mission": "Default mission for a B2B SaaS company.",
            "vision": "Default vision focused on intelligent growth.",
            "product": "Default AI-powered customer and revenue operations tools.",
            "tech_stack": "specific"
        }

        plan_text = generate_onboarding_plan(role, stage, size, seniority, website_data)
        st.markdown(plan_text)

        st.success("✅ Plan generated!")
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("📄 Download PDF", convert_to_pdf(plan_text), "onboarding_plan.pdf", "application/pdf")
        with col2:
            st.download_button("📝 Download Markdown", convert_to_markdown_file(plan_text), "onboarding_plan.md", "text/markdown")

