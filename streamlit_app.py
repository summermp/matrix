import streamlit as st
import pandas as pd
from supabase import create_client, Client
import time
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit.components.v1 import html

url = st.secrets["my_secret"]["supabase_url"]
api_key = st.secrets["my_secret"]["supabase_key"]

supabase: Client = create_client(url, api_key)

st.set_page_config(page_title='Matrix Mini R4', page_icon="🤖",
                   initial_sidebar_state="expanded", layout='wide')
st.sidebar.image('./static/img/matrix.png')
st.markdown("""<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">""",
            unsafe_allow_html=True)
test = {
    "timestamp": pd.date_range(start="2024-05-01 12:00", periods=10, freq="5s"),
    "voltage": [3.7, 3.6, 3.8, 3.5, 3.9, 3.4, 3.3, 3.8, 3.7, 3.6],
    "percentage": [80, 75, 70, 65, 60, 55, 45, 85, 90, 88],
    "distance": [15.2, 14.8, 15.5, 15.0, 14.6, 16.1, 17.0, 14.9, 15.3, 14.7]
}

def fetch_data():
    response = supabase.table('sensor_data').select(
        '*').order('timestamp', desc=True).limit(10).execute()
    data = response.data
    return pd.DataFrame(data)

def display_icon(icon_name, desc, value, unit, placeholder, color='green'):
    icon_html = f"""
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <div style="margin:0; padding:0;">
        <span><i class="material-icons" style="font-size: 24px; color: {color};">{icon_name}</i></span>
        <span><b>{desc}:</b> {value:.2f} <b>{unit}</b></span>
    </div>
    """
    placeholder.markdown(icon_html, unsafe_allow_html=True)

html("""<script>
    // Locate elements
    var decoration = window.parent.document.querySelectorAll('[data-testid="stDecoration"]')[0];
    var sidebar = window.parent.document.querySelectorAll('[data-testid="stSidebar"]')[0];
    // Observe sidebar size
    function outputsize() {
        decoration.style.left = `${sidebar.offsetWidth}px`;
    }
    new ResizeObserver(outputsize).observe(sidebar);
    // Adjust sizes
    outputsize();
    decoration.style.height = "6.0rem";  // Height of the decoration bar
    decoration.style.right = "45px";  // Distance from the right
    decoration.style.fontSize = "24px";  // Font size for the title
    decoration.style.fontWeight = "bold";  // Font size for the title
    decoration.style.textAlign = "center";  // Align the title to the center

    // Set dynamic title and background color
    decoration.style.backgroundColor = "limegreen";  // Background color
    decoration.innerHTML = "🚗💡🔋 Unlock the power of real-time autonomous vehicle monitoring 🚀🌍 <br> <span style='color:blue;'>Thanks to Matrix Robotics for the sample Matrix Mini R4 kit!</span>";  // Setting the title text

    </script>""", width=0, height=0)

with st.sidebar:
    st.markdown("With <b style='color:blue;'>Matrix Mini R4</b>, <b style='color:red;'>Streamlit</b>, and <b style='color:green;'>Supabase</b>! Track vital vehicle stats like ", unsafe_allow_html=True)
    percentage_placeholder = st.empty()  # Placeholder for battery percentage
    voltage_placeholder = st.empty()    # Placeholder for voltage data
    distance_placeholder = st.empty()   # Placeholder for distance data
    st.markdown("🎯 <b>Real-time, effortless upkeep</b>", unsafe_allow_html=True)
    
    st.markdown("""
    
    ### Skills Unlocked:
    - 🧠 **Critical Thinking**
    - 🤖 **Robotics Skills**
    - ⚙️ **Mechanical Structure**
    - 💻 **Programming**
""", unsafe_allow_html=True)
    st.link_button("➡️ Go to Matrix official page",
                   "https://www.matrixrobotics.com")

chart_placeholder = st.empty()
message_placeholder = st.empty()
counter = 0
# Infinite loop to update data in real-time
while True:
    df = fetch_data()
    if df.empty:  # Check if the DataFrame is empty
        message_placeholder.warning("⚠️ No data available from Supabase.")
        voltage_placeholder.empty()
        percentage_placeholder.empty()
        distance_placeholder.empty()
        chart_placeholder.empty()
    else:
        message_placeholder.empty()  # Clear the warning message

        # Extract the latest values
        latest_data = df.iloc[0]  # Get the latest row
        voltage = latest_data['voltage']
        percentage = latest_data['percentage']
        distance = latest_data['distance']/10

        display_icon('electric_bolt', 'Voltage',
                     voltage, "V", voltage_placeholder)
        # Display battery percentage with conditional icon
        if percentage >= 90:
            display_icon('battery_full', 'Percentage', percentage,
                         "%", percentage_placeholder, "limegreen")
        elif percentage >= 75:
            display_icon('battery_4_bar', 'Percentage', percentage,
                         "%", percentage_placeholder, "lime")
        elif percentage >= 50:
            display_icon('battery_3_bar', 'Percentage', percentage,
                         "%", percentage_placeholder, "palegreen")
        elif percentage >= 25:
            display_icon('battery_2_bar', 'Percentage', percentage,
                         "%", percentage_placeholder, "gold")
        else:
            display_icon('battery_alert', 'Percentage', percentage,
                         "%", percentage_placeholder, "red")

        display_icon('terrain', 'Obstacle Proximity', distance,
                     "cm", distance_placeholder)

        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Create a subplot with 2 rows and 1 column
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,  # Share x-axis for both subplots
            vertical_spacing=0.1,  # Adjust space between the plots
            subplot_titles=('Voltage over Time',
                            'Battery Percentage over Time')
        )

        # Add voltage trace to the first subplot (row=1, col=1)
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['voltage'],
                       mode='lines+markers', name='Voltage'),
            row=1, col=1
        )

        # Add percentage trace to the second subplot (row=2, col=1)
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['percentage'],
                       mode='lines+markers', name='Percentage'),
            row=2, col=1
        )

        # Update layout to add titles and labels
        fig.update_layout(
            height=600,  # Set the height of the whole figure
            title_text='Real-Time Voltage and Battery Percentage',
            yaxis_title='Voltage (V)',
            yaxis2_title='Percentage (%)',
            showlegend=False
        )

        # Clear and show the updated chart
        counter += 1
        chart_placeholder.plotly_chart(
            fig, use_container_width=True, key=f"chart_{counter}")

    time.sleep(5)  # Refresh every 5 second
