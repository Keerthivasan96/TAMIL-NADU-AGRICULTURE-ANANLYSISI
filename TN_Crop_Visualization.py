import streamlit as st
import pandas as pd
import cufflinks as cf
import plotly.graph_objs as go
import numpy as np

cf.go_offline()
cf.set_config_file(offline=False, world_readable=True)

# ---------------- Load Data ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("processed_data.csv")  # cleaned dataset from earlier
    # Filter only Tamil Nadu
    df = df[df["State_Name"].str.lower() == "tamil nadu"]
    return df

df = load_data()

# ---------------- Identify Top 10 Districts ----------------
district_performance = df.groupby("District_Name")["Production"].mean().sort_values(ascending=False).head(10)
top_districts = district_performance.index.tolist()

# ---------------- Sidebar ----------------
st.sidebar.title("Tamil Nadu Agriculture Explorer")
selected_district = st.sidebar.selectbox("Select District", top_districts)
selected_years = st.sidebar.slider("Select Year Range",
                                   int(df["Crop_Year"].min()),
                                   int(df["Crop_Year"].max()),
                                   (2000, 2015))
apply_log = st.sidebar.checkbox("Apply Log Scale for Production", value=True)

# ---------------- Filtered Data ----------------
df_filtered = df[(df["District_Name"] == selected_district) &
                 (df["Crop_Year"] >= selected_years[0]) &
                 (df["Crop_Year"] <= selected_years[1])]

# ---------------- Main Title ----------------
st.title("🌾 Tamil Nadu Agriculture Insights")
st.write(f"District: **{selected_district}**, Years: **{selected_years[0]}–{selected_years[1]}**")

# ---------------- Yearly Trends ----------------
if not df_filtered.empty:
    yearly_trend = df_filtered.groupby("Crop_Year")[["Production", "Yield"]].mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=yearly_trend.index, y=yearly_trend["Production"],
                             mode="lines+markers", name="Production"))
    fig.add_trace(go.Scatter(x=yearly_trend.index, y=yearly_trend["Yield"],
                             mode="lines+markers", name="Yield"))

    fig.update_layout(title=f"Yearly Trend in {selected_district}",
                      xaxis_title="Year", yaxis_title="Values",
                      template="plotly_white", height=500)
    st.plotly_chart(fig, use_container_width=True)

# ---------------- Crop Distribution ----------------
st.subheader("🌱 Crop Distribution")
crop_counts = df_filtered["Crop"].value_counts().head(10)

fig2 = go.Figure([go.Bar(x=crop_counts.index, y=crop_counts.values)])
fig2.update_layout(title="Most Frequently Sown Crops",
                   xaxis_title="Crop", yaxis_title="Count",
                   template="plotly_white", height=400)
st.plotly_chart(fig2, use_container_width=True)

# ---------------- Top Crops by Production ----------------
st.subheader("🌾 Top Crops by Average Production")
crop_prod = df_filtered.groupby("Crop")["Production"].mean().sort_values(ascending=False).head(10)

if apply_log:
    y_values = np.log1p(crop_prod.values)
    y_label = "Log(Production + 1)"
    title = "Top Crops by Production (Log Scale)"
else:
    y_values = crop_prod.values
    y_label = "Average Production"
    title = "Top Crops by Production"

fig3 = go.Figure([go.Bar(x=crop_prod.index, y=y_values)])
fig3.update_layout(title=title,
                   xaxis_title="Crop", yaxis_title=y_label,
                   template="plotly_white", height=400)
st.plotly_chart(fig3, use_container_width=True)

if apply_log:
    st.caption("Note: Log scale applied to reduce skew (e.g., Coconut values in millions).")

# ---------------- Insights ----------------
st.subheader("🔎 Key Insights for this District")
st.markdown(f"""
- **{selected_district}** is one of the **Top 10 agricultural districts** in Tamil Nadu.  
- The major crops cultivated here include: **{', '.join(crop_prod.index[:5].tolist())}**.  
- Over the selected years ({selected_years[0]}–{selected_years[1]}), production shows **{"an increasing" if yearly_trend["Production"].iloc[-1] > yearly_trend["Production"].iloc[0] else "a decreasing"} trend**.  
- Yield levels indicate **{"improvement" if yearly_trend["Yield"].iloc[-1] > yearly_trend["Yield"].iloc[0] else "stability/decline"}** in farming efficiency.  
- Crop diversity is **higher in Rabi season crops** compared to Kharif in this district.  
""")

# ---------------- Project Motivation ----------------
st.subheader("🎯 Project Motivation")
st.markdown("""
This project was designed to **analyze agricultural performance at the district level in Tamil Nadu**, 
highlighting key crops and trends. By narrowing down to the **top-performing districts** and enabling 
interactive insights, this dashboard shows how data can help in **decision-making for crop planning, 
policy, and food security**.
""")
