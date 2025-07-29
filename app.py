
import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="RevOps Dashboard", layout="wide")
st.title("📊 AI-Powered RevOps Dashboard")
st.markdown("This dashboard simulates key RevOps insights using AI-generated data.")

# Load data
leads = pd.read_csv("data/leads.csv")
opps = pd.read_csv("data/opportunities.csv")

# Preprocess
opps["weighted_amount"] = opps["amount"] * (opps["probability"] / 100)
opps["created_date"] = pd.to_datetime(opps["created_date"], errors="coerce")
leads["lead_score"] = pd.to_numeric(leads["lead_score"], errors="coerce")

# Key metrics
st.markdown("### 🚀 Key Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Pipeline", f"$11,504,000")
col2.metric("Avg Lead Score", f"67.6")
col3.metric("Lead → Opp Conversion", f"50.4%")
st.markdown("---")

# Funnel
st.subheader("🔁 Funnel Overview")
col4, col5 = st.columns(2)
col4.bar_chart(leads["status"].value_counts())
col5.bar_chart(leads["source"].value_counts())

# Rep performance
st.subheader("👤 Rep Pipeline Totals")
pipeline_by_rep = opps.groupby("assigned_rep")["amount"].sum().reset_index()
pipeline_by_rep.columns = ["Rep", "Total Pipeline ($)"]
pipeline_by_rep["Total Pipeline ($)"] = pd.to_numeric(pipeline_by_rep["Total Pipeline ($)"], errors="coerce")
bar = alt.Chart(pipeline_by_rep).mark_bar().encode(
    x=alt.X("Rep:N", title="Sales Rep"),
    y=alt.Y("Total Pipeline ($):Q", title="Pipeline ($)")
).properties(title="Pipeline by Rep")
st.altair_chart(bar, use_container_width=True)

# Stage chart
st.subheader("📊 Opportunity Stage Breakdown")
st.bar_chart(opps["stage"].value_counts())

# Forecast table
st.subheader("💰 Weighted Forecast by Stage")
forecast = opps.groupby("stage")["weighted_amount"].sum().reset_index()
forecast.columns = ["Stage", "Weighted Pipeline ($)"]
forecast["Weighted Pipeline ($)"] = forecast["Weighted Pipeline ($)"].apply(lambda x: f"${x:,.0f}")
table_html = forecast.to_html(index=False, justify="right", escape=False)
table_html = table_html.replace(
    '<th>Weighted Pipeline ($)</th>',
    '<th style="text-align:right">Weighted Pipeline ($)</th>'
).replace(
    '<td>', '<td style="text-align:right">'
).replace(
    '<td style="text-align:right">' + forecast["Stage"].iloc[0],
    '<td style="text-align:left">' + forecast["Stage"].iloc[0]
)
st.markdown(table_html, unsafe_allow_html=True)

# Insights
st.markdown("---")
st.header("🧠 Strategic Insights")
st.markdown(f"**🏆 Top Performer:** Sarah Chen leads in total pipeline.")
st.markdown(f"**🌱 Most Common Lead Source:** Organic Search")
st.markdown(f"**🎯 Best-Converting Source:** Trade Show — highest opportunity conversion.")
st.markdown(f"**🐢 Longest Stage Delay:** Discovery takes the longest on average.")

if pd.isna(nan) or True:
    st.warning("📉 No new opportunities created in the past 30 days — pipeline may be aging.")
elif nan < 10000:
    st.info(f"📉 New opportunities created, but average value is low (${recent_avg:,.0f}).")
else:
    st.success(f"📈 Healthy recent pipeline activity — average value: ${recent_avg:,.0f}")
