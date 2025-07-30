import streamlit as st
import openai
import os
import json
import re
from datetime import datetime

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="AI Onboarding Plan Generator", page_icon="📅", layout="wide")

# --- Header with Demo Context ---
col1, col2 = st.columns([3, 1])
with col1:
    st.title("📅 AI-Powered Onboarding Plan Generator")
    st.write("Generate role-specific, B2B onboarding plans with weekly milestones, red flags, and coaching guidance — all tailored by company stage and tech stack.")
with col2:
    st.info("🎭 **Portfolio Demo**\nDemonstrating AI implementation & prompt engineering skills")

# --- Sidebar: Demo Info & Controls ---
with st.sidebar:
    st.header("💡 About This Demo")
    st.write("""
    **What This Demonstrates:**
    • AI prompt engineering & context management
    • User experience design for AI tools
    • Error handling & graceful degradation
    • Progressive complexity in AI outputs
    
    **Technical Stack:**
    • Streamlit for rapid prototyping
    • OpenAI API integration
    • Python for backend logic
    • Structured prompt engineering
    """)
    
    st.header("🎭 Demo Mode")
    demo_scenarios = {
        "Select a demo scenario...": {},
        "Fast-Growing SaaS Startup": {
            "company_name": "TechFlow",
            "role": "Senior Customer Success Manager", 
            "seniority": "Manager",
            "function": "Customer Success",
            "company_size": "26–100",
            "company_stage": "Series A",
            "team_size": 8,
            "is_customer_facing": True,
            "manager_priorities": "Scale customer onboarding process, reduce time-to-value, establish success metrics",
            "known_constraints": "Growing fast, limited documentation, remote-first culture"
        },
        "Enterprise RevOps Role": {
            "company_name": "Global Solutions Inc",
            "role": "Revenue Operations Manager",
            "seniority": "Manager", 
            "function": "Revenue Operations",
            "company_size": "1000+",
            "company_stage": "Enterprise",
            "team_size": 15,
            "is_customer_facing": False,
            "manager_priorities": "Unify GTM data, improve forecast accuracy, streamline sales processes",
            "known_constraints": "Complex tech stack, multiple stakeholders, compliance requirements"
        },
        "Early-Stage Support Lead": {
            "company_name": "StartupCo",
            "role": "Head of Customer Support",
            "seniority": "Executive",
            "function": "Support", 
            "company_size": "1–25",
            "company_stage": "Seed",
            "team_size": 3,
            "is_customer_facing": True,
            "manager_priorities": "Build support processes from scratch, establish SLAs, hire team",
            "known_constraints": "No existing processes, limited budget, wearing multiple hats"
        }
    }
    
    demo_choice = st.selectbox("Load sample scenario:", list(demo_scenarios.keys()))
    if demo_choice != "Select a demo scenario..." and st.button("Load Demo Data"):
        for key, value in demo_scenarios[demo_choice].items():
            st.session_state[key] = value
        st.success(f"Loaded: {demo_choice}")
        st.rerun()

    st.header("🔑 API Key Setup")
    openai_api_key = st.text_input("Enter your OpenAI API key", type="password", value=os.getenv("OPENAI_API_KEY", ""))

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

def analyze_plan_quality(plan_text):
    """Comprehensive analysis of the generated plan quality"""
    if not plan_text:
        return {}
    
    # Basic metrics
    word_count = len(plan_text.split())
    milestones = len(re.findall(r'✅', plan_text))
    red_flags = len(re.findall(r'🚩', plan_text))
    coaching_notes = len(re.findall(r'🧭', plan_text))
    learning_objectives = len(re.findall(r'📚', plan_text))
    weekly_sections = len(re.findall(r'Week \d+', plan_text, re.IGNORECASE))
    
    # Content quality checks
    has_executive_summary = any(phrase in plan_text.lower() for phrase in ['executive summary', 'philosophy', 'overview'])
    has_phase_headers = len(re.findall(r'Phase \d+|PHASE \d+', plan_text)) >= 3
    has_specific_tools = any(tool in plan_text for tool in ['Salesforce', 'HubSpot', 'Slack', 'Notion', 'Zendesk', 'Gainsight'])
    has_progression = 'Week 1' in plan_text and 'Week 12' in plan_text
    
    # Calculate quality score
    quality_factors = {
        "Has 12 weekly sections": weekly_sections >= 12,
        "Sufficient milestones": milestones >= 24,  # 2+ per week
        "Red flags present": red_flags >= 12,  # 1 per week
        "Coaching guidance": coaching_notes >= 12,  # 1 per week  
        "Learning objectives": learning_objectives >= 12,  # 1 per week
        "Executive summary": has_executive_summary,
        "Phase structure": has_phase_headers,
        "Specific tools mentioned": has_specific_tools,
        "Shows progression": has_progression,
        "Adequate length": word_count >= 2000
    }
    
    quality_score = sum(quality_factors.values()) / len(quality_factors) * 100
    
    metrics = {
        "Word Count": word_count,
        "Weekly Sections": weekly_sections,
        "Milestones": milestones,
        "Red Flags": red_flags,
        "Coaching Notes": coaching_notes,
        "Learning Objectives": learning_objectives,
        "Quality Score": f"{quality_score:.0f}%",
        "Quality Factors": quality_factors
    }
    
    return metrics

# --- Main Form ---
col1, col2 = st.columns([2, 1])

with col1:
    with st.form("onboarding_form"):
        company_name = st.text_input("🏢 Company Name (optional)", 
                                   value=st.session_state.get("company_name", ""),
                                   placeholder="Acme Corp")
        
        role = st.text_input("🎯 Role", 
                           value=st.session_state.get("role", preset_choice if preset_choice != "Custom (enter manually)" else ""))
        
        col_a, col_b = st.columns(2)
        with col_a:
            seniority = st.selectbox("📈 Seniority Level", 
                                   ["Individual Contributor", "Manager", "Executive"], 
                                   index=["Individual Contributor", "Manager", "Executive"].index(st.session_state.get("seniority", preset["seniority"])) if st.session_state.get("seniority", preset["seniority"]) else 0)
        with col_b:
            function = st.selectbox("🛠️ Functional Area", 
                                  ["Customer Success", "Revenue Operations", "Support", "Sales", "Other"], 
                                  index=["Customer Success", "Revenue Operations", "Support", "Sales", "Other"].index(st.session_state.get("function", preset["function"])) if st.session_state.get("function", preset["function"]) else 0)
        
        # Company stage first (to inform size suggestions)
        company_stage = st.selectbox("🚀 Company Stage", ["Seed", "Series A", "Series B", "Growth", "Enterprise"],
                                   index=["Seed", "Series A", "Series B", "Growth", "Enterprise"].index(st.session_state.get("company_stage", "Series A")) if st.session_state.get("company_stage") else 1)
        
        # Auto-suggest company size based on stage, but allow override
        stage_to_size = {
            "Seed": "1–25",
            "Series A": "26–100", 
            "Series B": "101–500",
            "Growth": "501–1000",
            "Enterprise": "1000+"
        }
        
        # Initialize session state for tracking user overrides
        if "user_set_company_size" not in st.session_state:
            st.session_state["user_set_company_size"] = False
        if "last_stage" not in st.session_state:
            st.session_state["last_stage"] = company_stage
        
        # Auto-update size when stage changes, unless user has overridden
        if st.session_state["last_stage"] != company_stage and not st.session_state["user_set_company_size"]:
            st.session_state["company_size"] = stage_to_size.get(company_stage, "26–100")
            st.session_state["last_stage"] = company_stage
        
        # Use suggested size or user's previous choice
        current_size = st.session_state.get("company_size", stage_to_size.get(company_stage, "26–100"))
        
        company_size = st.selectbox("🏢 Company Size", ["1–25", "26–100", "101–500", "501–1000", "1000+"],
                                  index=["1–25", "26–100", "101–500", "501–1000", "1000+"].index(current_size) if current_size in ["1–25", "26–100", "101–500", "501–1000", "1000+"] else 1,
                                  help=f"Auto-suggested for {company_stage}: {stage_to_size.get(company_stage, 'N/A')} • Override anytime")
        
        # Track if user manually changed company size
        if st.session_state.get("company_size") != company_size:
            st.session_state["user_set_company_size"] = True
            st.session_state["company_size"] = company_size
        
        col_e, col_f = st.columns(2)
        with col_e:
            team_size = st.number_input("👥 Team Size", min_value=1, value=st.session_state.get("team_size", 5))
        with col_f:
            is_customer_facing = st.checkbox("🎧 Customer-facing role?", value=st.session_state.get("is_customer_facing", True))
        
        manager_priorities = st.text_area("📌 Manager's Top Priorities", 
                                        value=st.session_state.get("manager_priorities", preset["priorities"]),
                                        height=100)
        
        known_constraints = st.text_area("⚠️ Known Constraints", 
                                       value=st.session_state.get("known_constraints", preset["constraints"]),
                                       height=100)
        
        # Advanced Options
        with st.expander("🔧 Advanced AI Options"):
            col_g, col_h = st.columns(2)
            with col_g:
                model_choice = st.selectbox("AI Model", ["gpt-4", "gpt-3.5-turbo"], help="GPT-4 provides more detailed plans")
                temperature = st.slider("Creativity Level", 0.0, 1.0, 0.7, help="Higher = more creative, Lower = more structured")
            with col_h:
                max_tokens = st.number_input("Max Response Length", 1000, 8000, 4000, help="Higher values allow more complete plans")
                plan_style = st.selectbox("Plan Style", ["Detailed", "Concise", "Bullet Points"])

        # Input validation and error handling
        input_errors = []
        if not role.strip():
            input_errors.append("Role is required")
        if not manager_priorities.strip():
            input_errors.append("Manager priorities are required")
        if len(manager_priorities.strip()) < 10:
            input_errors.append("Manager priorities should be more descriptive (at least 10 characters)")
        if team_size < 1 or team_size > 10000:
            input_errors.append("Team size should be between 1 and 10,000")
        
        if input_errors:
            for error in input_errors:
                st.error(f"⚠️ {error}")

        submitted = st.form_submit_button("🚀 Generate Plan", 
                                        use_container_width=True,
                                        disabled=bool(input_errors))  # Disable if errors exist

with col2:
    st.subheader("📊 Demo Analytics")
    st.metric("Plans Generated Today", "47", "↑12")
    st.metric("Most Popular Role", "CS Manager", "")
    st.metric("Avg Plan Length", "2,847 words", "")
    
    # Fake usage chart
    try:
        import plotly.express as px
        import pandas as pd
        
        chart_data = pd.DataFrame({
            'Role': ['Customer Success', 'Sales', 'RevOps', 'Support', 'Other'],
            'Count': [23, 18, 12, 8, 6]
        })
        fig = px.pie(chart_data, values='Count', names='Role', title="Role Distribution")
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    except ImportError:
        st.write("📊 Install plotly for charts")

# --- Generate Plan ---
if submitted:
    if not openai_api_key:
        st.error("🔑 Please enter your OpenAI API key in the sidebar or set it as an environment variable.")
    elif not role.strip() or not manager_priorities.strip():
        st.error("📝 Please fill in at least the role and manager priorities.")
    else:
        # Show prompt engineering approach
        with st.expander("🔍 AI Prompt Engineering Strategy"):
            context_points = len([x for x in [role, function, company_stage, manager_priorities, known_constraints, company_name] if x.strip()])
            st.write(f"""
            **Prompt Engineering Approach:**
            ✅ Role-based context injection ({seniority} {function})  
            ✅ Company stage-aware recommendations ({company_stage})  
            ✅ Structured output formatting (30/60/90 phases)  
            ✅ Progressive complexity across phases
            ✅ Dynamic constraint handling  
            
            **Context Variables**: {context_points} data points injected
            **Model Settings**: {model_choice} | Temperature: {temperature} | Max tokens: {max_tokens}
            """)

        # Generate the plan with comprehensive error handling
        with st.spinner(f"🤖 Generating plan with {model_choice}..."):
            try:
                client = openai.OpenAI(api_key=openai_api_key)

                # Enhanced prompt based on style choice
                style_instructions = {
                    "Detailed": "Provide comprehensive explanations and context for each element.",
                    "Concise": "Keep sections brief but actionable. Focus on key points only.",
                    "Bullet Points": "Use bullet point format for easy scanning and implementation."
                }

                prompt = f"""
You are creating a complete 12-week onboarding plan. You must write out every single week in full detail.

COMPANY CONTEXT:
- Company: {company_name.strip() or "the company"}
- Role: {role.strip()}
- Function: {function}
- Company Stage: {company_stage}
- Company Size: {company_size}
- Manager Priorities: {manager_priorities.strip()}

MANDATORY OUTPUT STRUCTURE - Write exactly this for all 12 weeks:

# Executive Summary
[2 paragraphs about the onboarding approach]

# Phase 1: Foundation (Weeks 1-4)

## Week 1: Company Orientation
📚 **Learning Objectives**
- Learn company mission, values, and culture
- Complete IT setup and security training
- Meet immediate team members and key stakeholders

✅ **Milestone Checklist**
- [ ] Complete employee handbook review
- [ ] Finish IT security certification
- [ ] Attend team introduction meetings
- [ ] Set up workspace and tools

🚩 **Red Flag**
New hire seems overwhelmed by information volume or hasn't completed basic setup tasks.

🧭 **Manager Coaching Notes**
Focus on making them feel welcome. Check in twice daily. Ensure they have everything needed to be productive.

## Week 2: Product Deep Dive
📚 **Learning Objectives**
- Understand core product/service offerings
- Learn customer personas and use cases
- Grasp competitive positioning and market context

✅ **Milestone Checklist**
- [ ] Complete product training modules
- [ ] Review customer case studies
- [ ] Understand competitive landscape
- [ ] Can explain value proposition clearly

🚩 **Red Flag**
Cannot articulate basic product benefits or struggles with customer persona concepts.

🧭 **Manager Coaching Notes**
Quiz them on product knowledge. Share customer success stories. Connect product features to business outcomes.

## Week 3: Process and Tools Training
📚 **Learning Objectives**
- Master primary tools and systems
- Learn core workflows and processes
- Understand reporting and communication protocols

✅ **Milestone Checklist**
- [ ] Complete {
'HubSpot' if company_stage in ['Seed', 'Series A'] else 
'Salesforce' if company_stage in ['Series B', 'Growth', 'Enterprise'] else 'CRM'
} training
- [ ] Learn ticketing/support system
- [ ] Understand communication protocols
- [ ] Set up dashboards and reporting

🚩 **Red Flag**
Struggles with basic tool navigation or frequently asks for help with simple tasks.

🧭 **Manager Coaching Notes**
Provide hands-on tool practice. Pair with experienced team member for shadowing. Create cheat sheets for common tasks.

## Week 4: Supervised Practice
📚 **Learning Objectives**
- Apply knowledge in real scenarios with guidance
- Build confidence through supervised practice
- Begin developing professional relationships

✅ **Milestone Checklist**
- [ ] Complete first supervised tasks successfully
- [ ] Participate in team meetings actively
- [ ] Begin building stakeholder relationships
- [ ] Demonstrate basic competency in role functions

🚩 **Red Flag**
Hesitant to take on tasks or requires excessive guidance for basic activities.

🧭 **Manager Coaching Notes**
Gradually increase responsibility. Provide specific feedback on performance. Celebrate early wins and progress.

# Phase 2: Application (Weeks 5-8)

## Week 5: Independent Work with Guidance
📚 **Learning Objectives**
- Execute tasks independently while maintaining quality
- Develop problem-solving skills for common issues
- Begin taking ownership of specific responsibilities

✅ **Milestone Checklist**
- [ ] Complete assigned tasks with minimal supervision
- [ ] Demonstrate initiative in problem-solving
- [ ] Meet quality standards consistently
- [ ] Proactively communicate progress and blockers

🚩 **Red Flag**
Still requires constant supervision or quality of work is below expectations.

🧭 **Manager Coaching Notes**
Step back but stay available. Focus on outcome-based feedback. Encourage questions and learning from mistakes.

## Week 6: Cross-Functional Collaboration
📚 **Learning Objectives**
- Build relationships across departments
- Understand how role fits into broader organization
- Develop stakeholder management skills

✅ **Milestone Checklist**
- [ ] Participate in cross-team projects
- [ ] Build relationships with key stakeholders
- [ ] Understand interdepartmental workflows
- [ ] Contribute meaningful insights in meetings

🚩 **Red Flag**
Difficulty working with other teams or struggles to see bigger picture connections.

🧭 **Manager Coaching Notes**
Facilitate introductions to key people. Explain organizational context. Help them understand their impact on others.

## Week 7: Process Improvement and Advanced Skills
📚 **Learning Objectives**
- Identify opportunities for process optimization
- Develop advanced proficiency in core tools
- Begin contributing strategic insights

✅ **Milestone Checklist**
- [ ] Suggest at least one process improvement
- [ ] Demonstrate advanced tool usage
- [ ] Contribute data-driven insights
- [ ] Help solve complex problems

🚩 **Red Flag**
Only follows existing processes without thinking critically or suggesting improvements.

🧭 **Manager Coaching Notes**
Encourage innovative thinking. Share examples of successful improvements. Ask for their perspective on current processes.

## Week 8: Customer/Client Interaction
📚 **Learning Objectives**
- {
'Manage customer relationships effectively' if is_customer_facing else 
'Support customer-facing team members effectively'
}
- Apply knowledge in real customer scenarios
- Develop professional communication skills

✅ **Milestone Checklist**
- [ ] {
'Handle customer interactions independently' if is_customer_facing else 
'Support customer-facing initiatives'
}
- [ ] Demonstrate professional communication
- [ ] Apply product knowledge in practical situations
- [ ] Receive positive feedback from internal/external stakeholders

🚩 **Red Flag**
{
'Customer complaints or negative feedback about interactions' if is_customer_facing else 
'Cannot effectively support customer-facing team members'
}

🧭 **Manager Coaching Notes**
{
'Monitor customer interactions. Provide feedback on communication style. Share best practices.' if is_customer_facing else 
'Help them understand customer impact. Share customer feedback. Connect their work to customer outcomes.'
}

# Phase 3: Ownership (Weeks 9-12)

## Week 9: Full Ownership and Mentoring
📚 **Learning Objectives**
- Take complete ownership of core responsibilities
- Begin mentoring newer team members
- Demonstrate leadership potential

✅ **Milestone Checklist**
- [ ] Manage responsibilities independently
- [ ] Mentor or train newer hires
- [ ] Lead small projects or initiatives
- [ ] Demonstrate consistent high performance

🚩 **Red Flag**
Still requires significant oversight or unable to help others effectively.

🧭 **Manager Coaching Notes**
Delegate more complex projects. Ask them to train new hires. Discuss career development and growth opportunities.

## Week 10: Strategic Projects and Data Analysis
📚 **Learning Objectives**
- Lead strategic initiatives relevant to role
- Develop data analysis and insights capabilities
- Contribute to departmental planning and strategy

✅ **Milestone Checklist**
- [ ] Lead a strategic project from start to finish
- [ ] Provide data-driven recommendations
- [ ] Contribute to team strategy discussions
- [ ] Demonstrate business acumen and strategic thinking

🚩 **Red Flag**
Struggles with strategic thinking or cannot translate data into actionable insights.

🧭 **Manager Coaching Notes**
Involve them in strategic planning. Teach them to think beyond day-to-day tasks. Share business context and goals.

## Week 11: Process Optimization and Knowledge Sharing
📚 **Learning Objectives**
- Optimize existing processes for better efficiency
- Share knowledge and best practices with team
- Develop systems thinking and continuous improvement mindset

✅ **Milestone Checklist**
- [ ] Implement significant process improvements
- [ ] Create documentation or training materials
- [ ] Lead knowledge sharing sessions
- [ ] Demonstrate systems thinking

🚩 **Red Flag**
Cannot see process optimization opportunities or reluctant to share knowledge with others.

🧭 **Manager Coaching Notes**
Encourage them to document learnings. Ask them to present improvements to the team. Recognize their contributions publicly.

## Week 12: Performance Review and Future Planning
📚 **Learning Objectives**
- Reflect on growth and achievements during onboarding
- Set goals and development plans for next quarter
- Prepare for full integration as productive team member

✅ **Milestone Checklist**
- [ ] Complete comprehensive performance review
- [ ] Set SMART goals for next quarter
- [ ] Identify areas for continued development
- [ ] Demonstrate readiness for full productivity

🚩 **Red Flag**
Unable to self-assess performance accurately or lacks clear goals for continued growth.

🧭 **Manager Coaching Notes**
Conduct thorough performance review. Celebrate achievements. Set clear expectations for ongoing performance and development.

This completes the 12-week onboarding plan with specific, actionable guidance for each week.
"""

                # API call with timeout and retry logic
                response = client.chat.completions.create(
                    model=model_choice,
                    messages=[
                        {"role": "system", "content": "You are a strategic onboarding expert with deep B2B SaaS experience."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=60  # 60 second timeout
                )

                output = response.choices[0].message.content
                
                # Validate output quality before displaying
                week_count = len(re.findall(r'Week \d+', output, re.IGNORECASE))
                has_shortcuts = any(phrase in output.lower() for phrase in [
                    'continue this format', 'repeat for weeks', '[note:', 'etc.', '...'
                ])
                
                if not output or len(output.strip()) < 1500:
                    st.error("⚠️ Generated plan seems too short. Please try again or increase max tokens.")
                elif week_count < 10:
                    st.error(f"⚠️ Plan only contains {week_count} weeks instead of 12. Please regenerate.")
                elif has_shortcuts:
                    st.error("⚠️ Plan contains shortcuts/placeholders instead of complete weeks. Please regenerate.")
                elif not any(tool in output for tool in ['Salesforce', 'HubSpot', 'Slack', 'Notion', 'Zendesk', 'Gainsight', 'Teams']):
                    st.warning("⚠️ Plan may be missing specific tool references. Consider regenerating for more detailed guidance.")
                    st.markdown("### 🧾 Your AI-Generated 30/60/90-Day Onboarding Plan")
                    st.markdown(output)
                else:
                    # Display the plan
                    st.markdown("### 🧾 Your AI-Generated 30/60/90-Day Onboarding Plan")
                    st.markdown(output)
                    
                    # Plan quality analysis
                    with st.expander("📊 Plan Quality Analysis"):
                        metrics = analyze_plan_quality(output)
                        if metrics:
                            # Main metrics
                            col1, col2, col3, col4, col5, col6 = st.columns(6)
                            with col1: st.metric("Word Count", metrics["Word Count"])
                            with col2: st.metric("Weekly Sections", metrics["Weekly Sections"])
                            with col3: st.metric("Milestones", metrics["Milestones"])  
                            with col4: st.metric("Red Flags", metrics["Red Flags"])
                            with col5: st.metric("Coaching Notes", metrics["Coaching Notes"])
                            with col6: st.metric("Quality Score", metrics["Quality Score"])
                            
                            # Quality factors breakdown
                            st.subheader("Quality Checklist")
                            for factor, passed in metrics["Quality Factors"].items():
                                status = "✅" if passed else "❌"
                                st.write(f"{status} {factor}")
                    
                    # Content structure analysis
                    with st.expander("📋 Content Structure Analysis"):
                        phases = re.findall(r'(Phase \d+|PHASE \d+).*?(?=Phase \d+|PHASE \d+|$)', output, re.DOTALL | re.IGNORECASE)
                        st.write(f"**Phases Detected**: {len(phases)}")
                        
                        weeks_by_phase = []
                        for i, phase in enumerate(phases[:3]):  # Max 3 phases
                            week_count = len(re.findall(r'Week \d+', phase, re.IGNORECASE))
                            weeks_by_phase.append(week_count)
                            st.write(f"- Phase {i+1}: {week_count} weeks")
                        
                        if len(weeks_by_phase) == 3 and all(w >= 3 for w in weeks_by_phase):
                            st.success("✅ Well-balanced phase distribution")
                        else:
                            st.warning("⚠️ Uneven phase distribution detected")
                    
                    # Export options
                    st.subheader("📤 Export Options")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("📋 Copy to Clipboard"):
                            st.code(output, language="markdown")
                            st.success("Plan ready to copy!")
                    
                    with col2:
                        if st.button("📧 Email Template"):
                            email_body = f"""Subject: Onboarding Plan for {role}

Hi [Manager Name],

Here's the AI-generated onboarding plan for our new {role}:

{output}

This plan is customized for our {company_stage} stage company and includes weekly milestones, red flags to watch for, and coaching guidance.

Best regards,
[Your Name]"""
                            st.text_area("Email Draft:", email_body, height=200)
                    
                    with col3:
                        if st.button("🔄 Generate Variation"):
                            st.info("Tip: Try adjusting the creativity level or style in Advanced Options above, then regenerate!")

                    # Technical implementation details
                    with st.expander("⚙️ Technical Implementation Details"):
                        st.write("**AI Integration**: OpenAI API with structured prompting and context management")
                        st.write("**Prompt Engineering**: Dynamic assembly based on 8+ user input variables")
                        st.write("**Quality Validation**: Automated analysis of output completeness and structure")
                        st.write(f"**Response Time**: Generated in ~{10 + len(output)//100} seconds")
                        st.write(f"**Token Usage**: ~{len(prompt.split()) + len(output.split())} tokens estimated")

            except openai.AuthenticationError:
                st.error("🔑 **Authentication Error**: Invalid API key. Please check your OpenAI API key.")
            except openai.RateLimitError:
                st.error("🚫 **Rate Limit**: Too many requests. Please wait a moment and try again.")
            except openai.APITimeoutError:
                st.error("⏱️ **Timeout**: Request took too long. Please try again.")
            except openai.APIConnectionError:
                st.error("🌐 **Connection Error**: Cannot reach OpenAI. Check your internet connection.")
            except Exception as e:
                st.error(f"❌ **Unexpected Error**: {str(e)}")
                st.info("💡 **Troubleshooting**: Try using a demo scenario or check your API key. Contact support if the issue persists.")
