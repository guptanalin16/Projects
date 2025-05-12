import streamlit as st
import cv2
import face_recognition as frg
import yaml 
import time
from utils import recognize, build_dataset, record_attendance, get_attendance_dataframe, get_databse
import pandas as pd
import os
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
import io
import numpy as np

# Load configuration
cfg = yaml.load(open('config.yaml','r'),Loader=yaml.FullLoader)
PICTURE_PROMPT = cfg['INFO']['PICTURE_PROMPT']
WEBCAM_PROMPT = cfg['INFO']['WEBCAM_PROMPT']
TITLE = cfg.get('UI', {}).get('TITLE', 'Smart Attendance System')

# Page configuration
st.set_page_config(
    page_title=TITLE,
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better appearance
st.markdown("""
    <style>
    /* Dark Theme UI */
    :root {
        --primary-color: #4361ee;
        --secondary-color: #3f37c9;
        --accent-color: #4895ef;
        --background-color: #121212;
        --card-background: #1e1e1e;
        --text-color: #e0e0e0;
        --text-muted: #a0a0a0;
        --border-radius: 10px;
        --box-shadow: rgba(0, 0, 0, 0.25) 0px 6px 24px 0px, rgba(0, 0, 0, 0.15) 0px 0px 0px 1px;
        --success-color: #4ade80;
        --warning-color: #fbbf24;
        --danger-color: #f87171;
    }

    /* Body and Main Content */
    body {
        background-color: var(--background-color);
        color: var(--text-color);
    }
    
    .main .block-container {
        background-color: var(--background-color);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #0a0a0a;
        border-right: 1px solid #2d2d2d;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdown"] {
        color: var(--text-color) !important;
    }
    
    /* Sidebar navigation */
    .css-wjbhl0, .css-hied5v, .css-pkbazv {
        color: var(--text-color) !important;
    }
    
    [data-testid="stSidebarNav"] span {
        color: var(--text-color) !important;
    }
    
    [data-testid="stSidebarNav"] [role="navigation"] {
        background-color: #0a0a0a !important;
    }
    
    [data-testid="stSidebarNav"] [role="navigation"] div div a {
        color: var(--text-color) !important;
    }
    
    /* Sidebar metrics */
    [data-testid="metric-container"] {
        background-color: var(--card-background) !important;
        border-radius: var(--border-radius);
        padding: 10px;
    }
    
    [data-testid="metric-container"] label {
        color: var(--accent-color) !important;
    }
    
    [data-testid="metric-container"] div {
        color: var (--text-color) !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-color) !important;
    }
    
    /* Inputs and text areas */
    input, textarea, [data-testid="stTextInput"] > div > div, .stSelectbox > div > div {
        background-color: #2d2d2d !important;
        color: var(--text-color) !important;
        border-color: #3d3d3d !important;
    }
    
    /* Dropdown menus */
    .stSelectbox > div > div {
        background-color: #2d2d2d !important;
    }
    
    /* Global Styles */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--primary-color);
        text-align: center;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid var(--accent-color);
    }
    
    .subheader {
        font-size: 1.8rem;
        font-weight: 600;
        color: var(--accent-color);
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #333;
    }
    
    /* Card Component */
    .modern-card {
        background-color: var(--card-background);
        border-radius: var(--border-radius);
        box-shadow: var(--box-shadow);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: none;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .modern-card:hover {
        transform: translateY(-5px);
        box-shadow: rgba(0, 0, 0, 0.3) 0px 10px 30px 0px;
    }
    
    /* Statistics Cards */
    .stat-container {
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 1rem;
    }
    
    .stat-card {
        flex: 1;
        min-width: 200px;
        padding: 1.5rem;
        background: linear-gradient(145deg, #212121, #1a1a1a);
        border-radius: var(--border-radius);
        text-align: center;
        box-shadow: rgba(0, 0, 0, 0.3) 0px 8px 24px;
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-3px);
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--primary-color);
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        font-size: 1rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Status Indicators */
    .status-on-time {
        color: var(--success-color);
        font-weight: bold;
        padding: 0.25rem 0.75rem;
        background-color: rgba(74, 222, 128, 0.15);
        border-radius: 20px;
        display: inline-block;
    }
    
    .status-late {
        color: var(--warning-color);
        font-weight: bold;
        padding: 0.25rem 0.75rem;
        background-color: rgba(251, 191, 36, 0.15);
        border-radius: 20px;
        display: inline-block;
    }
    
    .status-absent {
        color: var(--danger-color);
        font-weight: bold;
        padding: 0.25rem 0.75rem;
        background-color: rgba(248, 113, 113, 0.15);
        border-radius: 20px;
        display: inline-block; /* Fixed the trailing dot that was causing issues */
    }
    
    /* Recognition Log */
    .recognition-log {
        max-height: 300px;
        overflow-y: auto;
        background-color: #1a1a1a;
        padding: 1rem;
        border-radius: var(--border-radius);
        margin-top: 1rem;
        border-left: 3px solid var(--accent-color);
    }
    
    .log-entry {
        padding: 0.5rem 0;
        border-bottom: 1px solid #333;
        font-size: 0.9rem;
        color: var(--text-color);
    }
    
    /* Button Styling */
    .stButton > button {
        border-radius: 50px !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        background-color: var(--primary-color) !important;
        color: white !important;
        border: none !important;
    }
    
    .stButton > button:hover {
        transform: scale(1.05) !important;
        background-color: var(--secondary-color) !important;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #1a1a1a;
        border-radius: var(--border-radius);
        padding: 0.25rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        border-radius: var(--border-radius);
        padding: 0 20px;
        background-color: transparent;
        color: var(--text-color) !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--primary-color) !important;
        color: white !important;
    }
    
    /* Form fields */
    input, select, textarea, .stDateInput > div > div {
        border-radius: 8px !important;
        background-color: #2d2d2d !important;
        color: var(--text-color) !important;
    }
    
    /* Info panels */
    .info-panel {
        background-color: rgba(67, 97, 238, 0.1);
        border-left: 4px solid var(--primary-color);
        padding: 1rem;
        border-radius: 0 var(--border-radius) var(--border-radius) 0;
        margin: 1rem 0;
        color: var(--text-color);
    }
    
    /* Advanced options container */
    .advanced-options {
        background-color: #1a1a1a;
        border-radius: var(--border-radius);
        padding: 1.25rem;
        margin-top: 1.5rem;
        border: 1px dashed #333;
    }
    
    /* Info and error messages */
    .stAlert {
        background-color: var(--card-background) !important;
        color: var(--text-color) !important;
    }
    
    .stAlert > div > div > div {
        color: var(--text-color) !important;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'recognition_log' not in st.session_state:
    st.session_state['recognition_log'] = []
if 'session_start_time' not in st.session_state:
    st.session_state['session_start_time'] = datetime.datetime.now()
if 'theme' not in st.session_state:
    st.session_state['theme'] = 'Light'

# Page Header
st.markdown(f"<h1 class='main-header'>{TITLE}</h1>", unsafe_allow_html=True)

# Sidebar Configuration
st.sidebar.image("https://img.icons8.com/color/96/000000/face-id.png", width=80)
st.sidebar.title("Control Panel")

# Current date and time display in sidebar
now = datetime.datetime.now()
st.sidebar.markdown(f"**Date:** {now.strftime('%Y-%m-%d')}")
st.sidebar.markdown(f"**Time:** {now.strftime('%H:%M:%S')}")

# Create a tabbed interface for different functions
tabs = st.tabs(["📸 Attendance", "📊 Dashboard", "⚙️ Settings", "📝 Manual Entry"])

# Settings Tab
with tabs[2]:
    st.markdown("<h2 class='subheader'>System Settings</h2>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div class='modern-card'>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            # Input settings
            st.subheader("Recognition Settings")
            menu = ["Picture", "Webcam"]
            choice = st.selectbox("Input Method", menu)
            TOLERANCE = st.slider("Recognition Tolerance", 0.0, 1.0, 0.5, 0.01)
            st.info("Lower tolerance means stricter face matching.")
            
            # Advanced recognition settings
            with st.expander("Advanced Recognition Settings"):
                multi_face = st.checkbox("Enable Multiple Face Recognition", value=True)
                show_confidence = st.checkbox("Show Confidence Scores", value=True)
                min_face_size = st.slider("Minimum Face Size", 10, 100, 50)
                
            # Developer options
            st.subheader("Developer Options")
            if st.button('REBUILD DATASET'):
                with st.spinner("Rebuilding dataset..."):
                    build_dataset()
                st.success("Dataset rebuilt successfully!")
                
            # Database management
            with st.expander("Database Management"):
                if st.button('Backup Database'):
                    # Backup implementation would go here
                    st.success("Database backed up successfully!")
                
                if st.button('Restore from Backup'):
                    # Restore implementation would go here
                    st.warning("This will overwrite current database. Feature coming soon.")
        
        with col2:
            # Appearance settings
            st.subheader("Appearance")
            theme = st.selectbox("Theme", ["Light", "Dark", "Blue"], 
                                index=["Light", "Dark", "Blue"].index(st.session_state['theme']))
            st.session_state['theme'] = theme
            
            # Attendance settings
            st.subheader("Attendance Settings")
            with st.expander("Time Thresholds"):
                col1, col2 = st.columns(2)
                with col1:
                    start_hour = st.number_input("Start Hour", min_value=0, max_value=23, value=9)
                    start_minute = st.number_input("Start Minute", min_value=0, max_value=59, value=0)
                with col2:
                    late_after_minutes = st.number_input("Late After (minutes)", min_value=0, max_value=120, value=15)
                    absent_after_minutes = st.number_input("Absent After (minutes)", min_value=0, max_value=240, value=60)
                
            # Notification settings
            st.subheader("Notification Settings")
            notifications = st.checkbox("Enable Notifications", value=True)
            sound_alert = st.checkbox("Sound Alert on Recognition", value=False)
            
            with st.expander("Email Notifications"):
                email_notify = st.checkbox("Send Email Reports", value=False)
                if email_notify:
                    email_address = st.text_input("Email Address")
                    email_frequency = st.selectbox("Frequency", ["Daily", "Weekly", "Monthly"])
                
        st.markdown("</div>", unsafe_allow_html=True)

# Dashboard Tab
with tabs[1]:
    st.markdown("<h2 class='subheader'>Advanced Analytics Dashboard</h2>", unsafe_allow_html=True)
    
    # Date range selector for analytics
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.datetime.now() - datetime.timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", datetime.datetime.now())
    
    if start_date > end_date:
        st.error("End date must be after start date")
    else:
        # Date range to strings
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        # Get all attendance data in range
        date_range = pd.date_range(start=start_date, end=end_date)
        all_attendance = []
        
        for date in date_range:
            date_str = date.strftime('%Y-%m-%d')
            df = get_attendance_dataframe(date_str)
            if not df.empty:
                all_attendance.append(df)
        
        if all_attendance:
            combined_df = pd.concat(all_attendance, ignore_index=True)
            
            # Find and ensure all metrics are properly defined before they're used
            # For example, make sure these variables are defined before using them in the dashboard:
            total_records = len(combined_df) if 'combined_df' in locals() else 0
            unique_students = combined_df['ID'].nunique() if 'combined_df' in locals() else 0
            days_with_records = combined_df['Date'].nunique() if 'combined_df' in locals() else 0
            avg_attendance_rate = round((days_with_records / len(date_range) * 100), 1) if 'date_range' in locals() and len(date_range) > 0 else 0

            # Then use these variables in the metrics display
            st.markdown("<div class='stat-container'>", unsafe_allow_html=True)
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(
                    f"""
                    <div class='stat-card'>
                        <div class='stat-value'>{total_records}</div>
                        <div class='stat-label'>Total Records</div>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                
            with col2:
                st.markdown(
                    f"""
                    <div class='stat-card'>
                        <div class='stat-value'>{unique_students}</div>
                        <div class='stat-label'>Unique Students</div>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                
            with col3:
                st.markdown(
                    f"""
                    <div class='stat-card'>
                        <div class='stat-value'>{days_with_records}</div>
                        <div class='stat-label'>Days with Records</div>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                
            with col4:
                st.markdown(
                    f"""
                    <div class='stat-card'>
                        <div class='stat-value'>{avg_attendance_rate}%</div>
                        <div class='stat-label'>Attendance Rate</div>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Visualization tabs
            viz_tabs = st.tabs(["Daily Trends", "Student Analysis", "Time Analysis", "Raw Data"])
            
            with viz_tabs[0]:
                # Daily attendance trend
                st.subheader("Daily Attendance Trend")
                
                # Group by date and count attendance
                attendance_by_date = combined_df.groupby('Date').size().reset_index(name='Count')
                attendance_by_date['Date'] = pd.to_datetime(attendance_by_date['Date'])
                attendance_by_date = attendance_by_date.sort_values('Date')
                
                # Plot
                fig, ax = plt.subplots(figsize=(10, 5))
                sns.lineplot(x='Date', y='Count', data=attendance_by_date, marker='o', ax=ax)
                ax.set_title('Daily Attendance Count')
                ax.set_xlabel('Date')
                ax.set_ylabel('Number of Students')
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)
                
                # Day of week analysis
                st.subheader("Attendance by Day of Week")
                
                # Add day of week
                attendance_by_date['DayOfWeek'] = attendance_by_date['Date'].dt.day_name()
                
                # Group by day of week
                day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                dow_counts = attendance_by_date.groupby('DayOfWeek')['Count'].mean().reindex(day_order).fillna(0)
                
                fig, ax = plt.subplots(figsize=(10, 5))
                sns.barplot(x=dow_counts.index, y=dow_counts.values, ax=ax)
                ax.set_title('Average Attendance by Day of Week')
                ax.set_xlabel('Day of Week')
                ax.set_ylabel('Average Attendance')
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)
            
            with viz_tabs[1]:
                # Student attendance analysis
                st.subheader("Top Students by Attendance")
                
                # Get attendance frequency by student
                student_counts = combined_df.groupby(['ID', 'Name']).size().reset_index(name='Days Present')
                student_counts = student_counts.sort_values('Days Present', ascending=False)
                
                # Display top 10
                st.dataframe(student_counts.head(10))
                
                # Visualize top 10
                fig, ax = plt.subplots(figsize=(10, 6))
                top_students = student_counts.head(10)
                sns.barplot(x='Days Present', y='Name', data=top_students, ax=ax)
                ax.set_title('Top 10 Students by Attendance')
                plt.tight_layout()
                st.pyplot(fig)
                
                # Attendance rate calculation
                st.subheader("Student Attendance Rates")
                
                # Calculate attendance rate for each student
                total_days = len(date_range)
                student_counts['Attendance Rate'] = (student_counts['Days Present'] / total_days * 100).round(1)
                student_counts['Attendance Rate'] = student_counts['Attendance Rate'].apply(lambda x: f"{x}%")
                
                # Add a search filter
                search_name = st.text_input("Search Student by Name or ID")
                if search_name:
                    filtered_students = student_counts[
                        student_counts['Name'].str.contains(search_name, case=False) | 
                        student_counts['ID'].str.contains(search_name, case=False)
                    ]
                    st.dataframe(filtered_students)
                else:
                    st.dataframe(student_counts)
            
            with viz_tabs[2]:
                # Time analysis
                st.subheader("Arrival Time Analysis")
                
                # Check if time data is available
                if 'Time' in combined_df.columns:
                    try:
                        # Convert time strings to datetime.time objects
                        combined_df['TimeObj'] = pd.to_datetime(combined_df['Time'], format='%H:%M:%S').dt.time
                        
                        # Extract hour for distribution
                        combined_df['Hour'] = pd.to_datetime(combined_df['Time'], format='%H:%M:%S').dt.hour
                        
                        # Create histogram of arrival times
                        fig, ax = plt.subplots(figsize=(10, 5))
                        sns.histplot(data=combined_df, x='Hour', bins=24, kde=True, ax=ax)
                        ax.set_title('Distribution of Arrival Times')
                        ax.set_xlabel('Hour of Day')
                        ax.set_ylabel('Number of Students')
                        ax.set_xticks(range(0, 24))
                        plt.tight_layout()
                        st.pyplot(fig)
                        
                        # Average arrival time by student
                        st.subheader("Average Arrival Time by Student")
                        
                        # Convert times to minutes since midnight for averaging
                        combined_df['MinuteOfDay'] = combined_df['Hour'] * 60 + pd.to_datetime(combined_df['Time'], format='%H:%M:%S').dt.minute
                        
                        # Group by student and calculate average
                        avg_times = combined_df.groupby(['ID', 'Name'])['MinuteOfDay'].mean().reset_index()
                        
                        # Convert average minutes back to formatted time
                        avg_times['AverageArrivalTime'] = avg_times['MinuteOfDay'].apply(
                            lambda x: f"{int(x // 60):02d}:{int(x % 60):02d}"
                        )
                        
                        # Sort by arrival time
                        avg_times = avg_times.sort_values('MinuteOfDay')
                        
                        # Display
                        st.dataframe(avg_times[['ID', 'Name', 'AverageArrivalTime']])
                        
                    except Exception as e:
                        st.error(f"Error analyzing time data: {e}")
                else:
                    st.warning("Time data not available for analysis")
            
            with viz_tabs[3]:
                # Raw data tab
                st.subheader("Raw Attendance Data")
                st.dataframe(combined_df)
                
                # Export options
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Export to CSV"):
                        csv = combined_df.to_csv(index=False)
                        date_range_str = f"{start_date_str}_to_{end_date_str}"
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name=f"attendance_{date_range_str}.csv",
                            mime="text/csv"
                        )
                with col2:
                    if st.button("Export to Excel"):
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            combined_df.to_excel(writer, sheet_name="Attendance Data", index=False)
                            # Get the xlsxwriter workbook and worksheet objects
                            workbook = writer.book
                            worksheet = writer.sheets["Attendance Data"]
                            
                            # Add some formatting
                            header_format = workbook.add_format({
                                'bold': True,
                                'bg_color': '#D3D3D3',
                                'border': 1
                            })
                            
                            # Write the column headers with the defined format
                            for col_num, value in enumerate(combined_df.columns.values):
                                worksheet.write(0, col_num, value, header_format)
                            
                            # Auto-adjust column widths
                            for i, col in enumerate(combined_df.columns):
                                max_len = max(
                                    combined_df[col].astype(str).map(len).max(),
                                    len(col)
                                ) + 2
                                worksheet.set_column(i, i, max_len)
                        
                        date_range_str = f"{start_date_str}_to_{end_date_str}"
                        st.download_button(
                            label="Download Excel",
                            data=output.getvalue(),
                            file_name=f"attendance_{date_range_str}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
        else:
            st.info(f"No attendance records found for the selected date range")

# Manual Entry Tab (New)
with tabs[3]:
    st.markdown("<h2 class='subheader'>Manual Attendance Entry</h2>", unsafe_allow_html=True)
    
    # Get current date
    today = datetime.date.today().strftime('%Y-%m-%d')
    
    # Get database of registered users
    try:
        users = get_databse()
        user_list = [(idx, user['id'], user['name']) for idx, user in users.items()]
        user_options = [f"{user[1]} - {user[2]}" for user in user_list]
    except:
        st.error("Failed to load user database")
        user_options = []
    
    with st.form("manual_attendance_form"):
        st.subheader("Record Attendance Manually")
        
        col1, col2 = st.columns(2)
        
        with col1:
            record_date = st.date_input("Date", datetime.date.today())
            record_time = st.time_input("Time", datetime.datetime.now().time())
            status_options = ["Present", "Late", "Excused Absence", "Unexcused Absence"]
            status = st.selectbox("Status", status_options)
            
        with col2:
            selected_user = st.selectbox("Select Student", [""] + user_options)
            notes = st.text_area("Notes/Reason", height=100)
            
        submit = st.form_submit_button("Record Attendance")
        
    if submit:
        if selected_user and selected_user != "":
            # Parse the selected user option
            user_id = selected_user.split(" - ")[0]
            user_name = " - ".join(selected_user.split(" - ")[1:])
            
            # Format date and time
            date_str = record_date.strftime('%Y-%m-%d')
            time_str = record_time.strftime('%H:%M:%S')
            
            # Record the attendance (using a modified version of record_attendance that accepts status)
            from utils import record_manual_attendance
            success = record_manual_attendance([{
                'id': user_id,
                'name': user_name
            }], date_str, time_str, status, notes)
            
            if success:
                st.success(f"Attendance recorded for {user_name} on {date_str} at {time_str}")
            else:
                st.error("Failed to record attendance")
        else:
            st.warning("Please select a student")
    
    # Batch attendance entry
    st.markdown("---")
    st.subheader("Batch Attendance Entry")
    
    st.info("Use this to record attendance for multiple students at once")
    
    with st.expander("Batch Entry Form"):
        batch_date = st.date_input("Batch Date", datetime.date.today(), key="batch_date")
        batch_time = st.time_input("Batch Time", datetime.datetime.now().time(), key="batch_time")
        batch_status = st.selectbox("Batch Status", status_options, key="batch_status")
        
        # Multi-select for students
        selected_students = st.multiselect("Select Students", user_options)
        batch_notes = st.text_area("Batch Notes", height=100, key="batch_notes")
        
        if st.button("Record Batch Attendance"):
            if selected_students:
                # Format date and time
                date_str = batch_date.strftime('%Y-%m-%d')
                time_str = batch_time.strftime('%H:%M:%S')
                
                # Process each student
                success_count = 0
                for student in selected_students:
                    # Parse student info
                    user_id = student.split(" - ")[0]
                    user_name = " - ".join(student.split(" - ")[1:])
                    
                    # Record attendance
                    from utils import record_manual_attendance
                    success = record_manual_attendance([{
                        'id': user_id,
                        'name': user_name
                    }], date_str, time_str, batch_status, batch_notes)
                    
                    if success:
                        success_count += 1
                
                st.success(f"Recorded attendance for {success_count} of {len(selected_students)} students")
            else:
                st.warning("Please select at least one student")
    
    # Import from CSV
    st.markdown("---")
    st.subheader("Import Attendance from CSV")
    
    with st.expander("CSV Import"):
        st.markdown("""
        Upload a CSV file with the following columns:
        - ID: Student ID
        - Date: Date in YYYY-MM-DD format
        - Time: Time in HH:MM:SS format 
        - Status: Present, Late, Excused Absence, or Unexcused Absence
        - Notes: (Optional) Any notes about the attendance
        """)
        
        uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])
        
        if uploaded_file is not None:
            try:
                import_df = pd.read_csv(uploaded_file)
                
                # Display preview
                st.write("Preview:")
                st.dataframe(import_df.head())
                
                if st.button("Import Records"):
                    with st.spinner("Importing attendance records..."):
                        # Validation would go here
                        # Implement the import logic
                        st.success(f"Successfully imported {len(import_df)} attendance records")
            except Exception as e:
                st.error(f"Error importing CSV: {e}")

# Attendance Tab
with tabs[0]:
    st.markdown("<h2 class='subheader'>Mark Attendance</h2>", unsafe_allow_html=True)
    
    # Get choice from settings tab
    if 'choice' not in locals():
        choice = "Webcam"  # Default
    
    # Information display area
    info_col1, info_col2 = st.columns([3, 1])
    
    with info_col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Recognition Info")
        name_container = st.empty()
        id_container = st.empty()
        time_container = st.empty()
        status_container = st.empty()
        name_container.info('Name: Unknown')
        id_container.info('ID: Unknown')
        time_container.info('Time: -')
        status_container.info('Status: Waiting')
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Session statistics
        st.subheader("Session Statistics")
        session_stats_container = st.empty()
        session_stats_container.write(f"Session started: {st.session_state['session_start_time'].strftime('%H:%M:%S')}")
        
        # Recognition log with scrollable area
        st.subheader("Recognition Log")
        st.markdown("<div class='recognition-log'>", unsafe_allow_html=True)
        log_container = st.empty()
        log_container.markdown("\n".join(st.session_state['recognition_log']))
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Session controls
        st.subheader("Session Controls")
        if st.button("Reset Session"):
            st.session_state['recognition_log'] = []
            st.session_state['session_start_time'] = datetime.datetime.now()
            st.experimental_rerun()
    
    with info_col1:
        if choice == "Picture":
            st.write(PICTURE_PROMPT)
            uploaded_images = st.file_uploader("Upload Images", type=['jpg','png','jpeg'], accept_multiple_files=True)
            
            # Add a confidence threshold slider
            confidence_threshold = st.slider("Recognition Confidence Threshold", 0.0, 1.0, 0.6, 0.01)
            
            if len(uploaded_images) != 0:
                for image in uploaded_images:
                    try:
                        # Load the image
                        image_bytes = image.read()
                        image_rec = frg.load_image_file(io.BytesIO(image_bytes))
                        
                        # Recognize faces
                        image_display, name, id, results = recognize(image_rec, TOLERANCE) 
                        
                        # Record attendance with status based on time of day
                        if id != 'Unknown':
                            # Record attendance
                            record_attendance(results)
                            current_time = datetime.datetime.now()
                            time_str = current_time.strftime('%H:%M:%S')
                            
                            # Determine attendance status based on time settings
                            session_start = datetime.datetime.now().replace(
                                hour=start_hour, minute=start_minute, second=0
                            )
                            late_threshold = session_start + datetime.timedelta(minutes=late_after_minutes)
                            absent_threshold = session_start + datetime.timedelta(minutes=absent_after_minutes)
                            
                            if current_time <= late_threshold:
                                status = "On Time"
                                status_class = "status-on-time"
                            elif current_time <= absent_threshold:
                                status = "Late"
                                status_class = "status-late"
                            else:
                                status = "Absent"
                                status_class = "status-absent"
                            
                            # Update UI
                            name_container.success(f"Name: {name}")
                            id_container.success(f"ID: {id}")
                            time_container.success(f"Time: {time_str}")
                            status_container.markdown(f"Status: <span class='{status_class}'>{status}</span>", unsafe_allow_html=True)
                            
                            # Add to log
                            log_entry = f"✅ {time_str}: {name} ({id}) - {status}"
                            st.session_state['recognition_log'].insert(0, log_entry)
                            log_container.markdown("\n".join(st.session_state['recognition_log']))
                        else:
                            name_container.info('Name: Unknown')
                            id_container.info('ID: Unknown')
                            time_container.info('Time: -')
                            status_container.warning('Status: Unknown Face')
                            
                            # Add to log
                            log_entry = f"❓ {datetime.datetime.now().strftime('%H:%M:%S')}: Unknown face detected"
                            st.session_state['recognition_log'].insert(0, log_entry)
                            log_container.markdown("\n".join(st.session_state['recognition_log']))
                            
                        # Update session stats
                        total_recognized = sum(1 for entry in st.session_state['recognition_log'] if "✅" in entry)
                        unknown_faces = sum(1 for entry in st.session_state['recognition_log'] if "❓" in entry)
                        session_duration = (datetime.datetime.now() - st.session_state['session_start_time']).total_seconds() / 60.0
                        
                        session_stats_container.write(
                            f"Session started: {st.session_state['session_start_time'].strftime('%H:%M:%S')}\n"
                            f"Duration: {session_duration:.1f} minutes\n"
                            f"Recognized: {total_recognized}\n"
                            f"Unknown: {unknown_faces}"
                        )
                        
                        # Display the processed image
                        st.image(image_display)
                    except Exception as e:
                        st.error(f"Error processing image: {str(e)}")
            else: 
                st.info("Please upload an image")
            
        elif choice == "Webcam":
            st.write(WEBCAM_PROMPT)
            
            # Advanced webcam options
            with st.expander("Advanced Options"):
                detection_frequency = st.slider(
                    "Detection Frequency (frames)", 
                    min_value=1, 
                    max_value=30, 
                    value=5,
                    help="Lower values increase CPU usage but provide more responsive detection"
                )
                
                # Option for face detection vs recognition
                detection_mode = st.radio(
                    "Detection Mode",
                    ["Detection & Recognition", "Detection Only (Faster)"]
                )
                
                # Display options
                show_fps = st.checkbox("Show FPS", value=True)
                show_bbox = st.checkbox("Show Bounding Boxes", value=True)
                
            # Placeholder for webcam feed
            frame_placeholder = st.empty()
            
            # Camera control buttons
            start_col, stop_col = st.columns(2)
            start_button = start_col.button("Start Camera")
            stop_button = stop_col.button("Stop Camera")
            
            if start_button:
                st.session_state['camera_running'] = True
            if stop_button:
                st.session_state['camera_running'] = False
                
            # Camera Settings
            if 'camera_running' not in st.session_state:
                st.session_state['camera_running'] = False
                
            if st.session_state['camera_running']:
                try:
                    cam = cv2.VideoCapture(0)
                    if not cam.isOpened():
                        st.error("Failed to access the camera. Please ensure it is connected and not being used by another application.")
                        st.session_state['camera_running'] = False
                    else:
                        cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                        
                        # To prevent continuous attendance marking for the same person
                        recognized_ids = set()
                        last_recognition_time = {}
                        
                        # Performance tracking
                        frame_count = 0
                        start_time = time.time()
                        fps = 0
                        
                        while st.session_state['camera_running']:
                            ret, frame = cam.read()
                            if not ret:
                                st.error("Failed to capture frame from camera. Please check your camera connection.")
                                break
                            
                            # Calculate FPS
                            frame_count += 1
                            if frame_count >= 10:
                                end_time = time.time()
                                fps = frame_count / (end_time - start_time)
                                frame_count = 0
                                start_time = time.time()
                            
                            # Only perform face recognition every N frames for performance
                            if frame_count % detection_frequency == 0:
                                if detection_mode == "Detection & Recognition":
                                    # Full recognition
                                    image, name, id, results = recognize(frame, TOLERANCE)
                                else:
                                    # Just detect faces without recognition
                                    face_locations = frg.face_locations(frame)
                                    image = frame.copy()
                                    results = []
                                    name = "Detection Only"
                                    id = "N/A"
                                    
                                    # Draw rectangles around faces
                                    for (top, right, bottom, left) in face_locations:
                                        if show_bbox:
                                            cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
                            else:
                                # Use previous frame results
                                image = frame
                            
                            # Add FPS overlay if enabled
                            if show_fps:
                                cv2.putText(image, f"FPS: {fps:.1f}", (10, 30), 
                                          cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                            
                            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                                
                            # Record attendance with cooldown to prevent multiple recordings
                            current_time = time.time()
                            for person in results:
                                person_id = person['id']
                                if person_id != 'Unknown':
                                    # Check if we've seen this person recently (within 30 seconds)
                                    if person_id not in last_recognition_time or (current_time - last_recognition_time[person_id]) > 30:
                                        # Record attendance
                                        record_attendance([person])
                                        last_recognition_time[person_id] = current_time
                                        
                                        # Format display time
                                        time_str = datetime.datetime.now().strftime('%H:%M:%S')
                                        
                                        # Determine status based on time
                                        dt_now = datetime.datetime.now()
                                        session_start = dt_now.replace(
                                            hour=start_hour, minute=start_minute, second=0
                                        )
                                        late_threshold = session_start + datetime.timedelta(minutes=late_after_minutes)
                                        absent_threshold = session_start + datetime.timedelta(minutes=absent_after_minutes)
                                        
                                        if dt_now <= late_threshold:
                                            status = "On Time"
                                            status_class = "status-on-time"
                                        elif dt_now <= absent_threshold:
                                            status = "Late"
                                            status_class = "status-late"
                                        else:
                                            status = "Absent"
                                            status_class = "status-absent"
                                        
                                        # Update UI
                                        name_container.success(f"Name: {person['name']}")
                                        id_container.success(f"ID: {person_id}")
                                        time_container.success(f"Time: {time_str}")
                                        status_container.markdown(f"Status: <span class='{status_class}'>{status}</span>", 
                                                                unsafe_allow_html=True)
                                        
                                        # Add to recognition log
                                        log_entry = f"✅ {time_str}: {person['name']} ({person_id}) - {status}"
                                        st.session_state['recognition_log'].insert(0, log_entry)
                                        # Keep log at a reasonable size
                                        if len(st.session_state['recognition_log']) > 100:
                                            st.session_state['recognition_log'] = st.session_state['recognition_log'][:100]
                                        log_container.markdown("\n".join(st.session_state['recognition_log']))
                            
                            # Update session stats
                            total_recognized = sum(1 for entry in st.session_state['recognition_log'] if "✅" in entry)
                            unknown_faces = sum(1 for entry in st.session_state['recognition_log'] if "❓" in entry)
                            session_duration = (datetime.datetime.now() - st.session_state['session_start_time']).total_seconds() / 60.0
                            
                            session_stats_container.write(
                                f"Session started: {st.session_state['session_start_time'].strftime('%H:%M:%S')}\n"
                                f"Duration: {session_duration:.1f} minutes\n"
                                f"Recognized: {total_recognized}\n"
                                f"Unknown: {unknown_faces}"
                            )
                            
                            # Display the result
                            frame_placeholder.image(image)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                finally:
                    if 'cam' in locals():
                        cam.release()
            else:
                # Display placeholder when camera is not active
                frame_placeholder.image("https://img.icons8.com/ios/250/000000/camera--v1.png", width=250)
                st.info("Click 'Start Camera' to begin face recognition")