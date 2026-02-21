import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Agent Secure Portal", layout="wide")

# 2. Connect to your Data
DATA_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSGHrehWfRjbr4oEw58UofOXIZGrCy94xLaDXfXXzUnwfkRZ6qaVTNUThwpjSVY-bX9ZO9Ma2PiOeG2/pub?output=csv"

@st.cache_data(ttl=60) # Refreshes every 1 minute for better "live" feel
def load_data():
    data = pd.read_csv(DATA_URL)
    data['Pending'] = pd.to_numeric(data['Pending'], errors='coerce').fillna(0)
    data['Current DC'] = data['Current DC'].astype(str).str.strip()
    return data

# --- LOGIN SYSTEM ---
st.sidebar.title("🔐 Agent Login")
user_dc = st.sidebar.text_input("Enter your DC Code (e.g. 608LBK)", "").strip()

if user_dc == "":
    st.title("🚚 Welcome to the Logistics Portal")
    st.info("Please enter your DC Code in the sidebar to view your pending tasks.")
    st.image("https://img.freepik.com/free-vector/security-concept-illustration_114360-468.jpg", width=300)
else:
    try:
        df = load_data()
        
        # Check if the entered DC actually exists in your data
        if user_dc in df['Current DC'].unique():
            filtered_df = df[df['Current DC'] == user_dc]
            
            st.title(f"👋 Hello, Station {user_dc}")
            st.success(f"Login Successful. You have {len(filtered_df)} pending items.")

            # 3. Metrics for that specific Agent
            breach_count = len(filtered_df[filtered_df['Pending'] > 2])
            total_cod = filtered_df['COD'].sum()

            col1, col2, col3 = st.columns(3)
            col1.metric("Your Total Pending", f"{len(filtered_df)} AWB")
            col2.metric("SLA BREACHES", f"{breach_count}", delta="Action Required", delta_color="inverse")
            col3.metric("Your COD to Collect", f"RM {total_cod:,.2f}")

            # 4. Search within their own data
            search_awb = st.text_input("🔍 Search by AWB or Recipient Name")
            if search_awb:
                filtered_df = filtered_df[
                    filtered_df['AWB'].str.contains(search_awb, case=False, na=False) | 
                    filtered_df['Recipient Name'].str.contains(search_awb, case=False, na=False)
                ]

            # 5. Data Table
            st.subheader("Your Delivery Priority List")
            st.dataframe(
                filtered_df[['AWB', 'Recipient Name', 'Recipient Phone', 'Route', 'Status', 'Pending', 'COD']],
                use_container_width=True
            )
        else:
            st.error(f"❌ DC Code '{user_dc}' not found. Please check your code and try again.")
            st.warning("Hint: Make sure there are no spaces in the code.")

    except Exception as e:
        st.error(f"Error: {e}")
