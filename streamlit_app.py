import streamlit as st
import pandas as pd
from supabase import create_client, Client
import time

# Initialize connection to Supabase
supabase_url = "https://lweqgypqengrrymrkgao.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx3ZXFneXBxZW5ncnJ5bXJrZ2FvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzIzMDkzOTEsImV4cCI6MjA0Nzg4NTM5MX0.VIFgwdupjFDFi6bwu72VIX0PrcaY0WtCq_iDyy504PU"
supabase: Client = create_client(supabase_url, supabase_key)

# Streamlit page configuration
st.title("Real-time Temperature and Humidity Monitor 🌡️💧")
st.markdown("Data fetched from Supabase in real-time.")
# Function to fetch data from Supabase
def fetch_data():
    response = supabase.table('sensor_data').select('*').order('id', desc=True).limit(10).execute()
    data = response.data
    return pd.DataFrame(data)

# Placeholder for real-time data display
data_placeholder = st.empty()  # Table placeholder
chart_placeholder = st.empty()  # Chart placeholder
message_placeholder = st.empty()  # Message placeholder

# Infinite loop to update data in real-time
while True:
    df = fetch_data()
    if df.empty:  # Check if the DataFrame is empty
        message_placeholder.warning("⚠️ No data available from Matrix Mini R4.")
        data_placeholder.empty()  # Clear any previous table
        chart_placeholder.empty()  # Clear any previous chart
    else:
        message_placeholder.empty()  # Clear the warning message
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        # Display the latest 10 readings
        data_placeholder.dataframe(df)
        chart_placeholder.line_chart(df[['voltage', 'percentage']])
        
    time.sleep(5)  # Refresh every 5 seconds
