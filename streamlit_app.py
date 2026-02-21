import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="LBK Logistics Portal", layout="wide")

# 2. Connect to your Link
# This is the link you just gave me
DATA_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSGHrehWfRjbr4oEw58UofOXIZGrCy94xLaDXfXXzUnwfkRZ6qaVTNUThwpjSVY-bX9ZO9Ma2PiOeG2/pub?output=csv"

@st.cache_data(ttl=600) # This refreshes the data every 10 minutes
def load_data():
    data = pd.read_csv(DATA_URL)
    # Ensure 'Pending' is a number so we can calculate
    data['Pending'] = pd.to_numeric(data['Pending'], errors='coerce').fillna(0)
    return data

try:
    df = load_data()

    # 3. Sidebar / Filters
    st.sidebar.header("Filter Options")
    all_dcs = ["All DCs"] + sorted(df['Current DC'].dropna().unique().tolist())
    selected_dc = st.sidebar.selectbox("Select Station / DC", all_dcs)

    # Filter data based on selection
    if selected_dc != "All DCs":
        filtered_df = df[df['Current DC'] == selected_dc]
    else:
        filtered_df = df

    # 4. Main Dashboard Header
    st.title("🚚 Real-Time Backlog Monitor")
    st.markdown(f"**Showing data for:** {selected_dc}")

    # 5. Top Key Metrics (The "Big Numbers")
    # We define a breach as anything pending more than 2 days
    breach_count = len(filtered_df[filtered_df['Pending'] > 2])
    total_cod = filtered_df['COD'].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Pending", f"{len(filtered_df)} AWB")
    col2.metric("SLA BREACH (>2 Days)", f"{breach_count}", delta="- Action Required", delta_color="inverse")
    col3.metric("Total COD", f"RM {total_cod:,.2f}")

    # 6. The Data Table
    st.subheader("Priority Delivery List")
    
    # Simple styling to highlight high pending days
    def color_rows(val):
        if val > 5: return 'color: red; font-weight: bold'
        if val > 2: return 'color: orange'
        return ''

    st.dataframe(
        filtered_df[['AWB', 'Recipient Name', 'Status', 'Pending', 'COD', 'Route', 'Current DC']],
        use_container_width=True,
        column_config={
            "AWB": st.column_config.TextColumn("Tracking Number"),
            "Pending": st.column_config.NumberColumn("Days Old")
        }
    )

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Check if your Google Sheet is still 'Published to Web' as a CSV.")
