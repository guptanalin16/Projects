import face_recognition as frg
import pickle as pkl 
import os 
import cv2 
import numpy as np
import yaml
from collections import defaultdict
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import json
import shutil

information = defaultdict(dict)
cfg = yaml.load(open('config.yaml','r'),Loader=yaml.FullLoader)
DATASET_DIR = cfg['PATH']['DATASET_DIR']
PKL_PATH = cfg['PATH']['PKL_PATH']
ATTENDANCE_PATH = cfg['PATH']['ATTENDANCE_PATH']
LOGS_DIR = cfg['PATH'].get('LOGS_DIR', 'logs/')
BACKUP_DIR = cfg['PATH'].get('BACKUP_DIR', 'backup/')

# Create necessary directories if they don't exist
for directory in [DATASET_DIR, LOGS_DIR, BACKUP_DIR]:
    Path(directory).mkdir(exist_ok=True)

def get_databse():
    if not os.path.exists(PKL_PATH):
        # Create empty database if it doesn't exist
        with open(PKL_PATH, 'wb') as f:
            pkl.dump({}, f)
    
    with open(PKL_PATH,'rb') as f:
        database = pkl.load(f)
    return database

def recognize(image, TOLERANCE): 
    database = get_databse()
    known_encoding = [database[id]['encoding'] for id in database.keys()] 
    name = 'Unknown'
    id = 'Unknown'
    face_locations = frg.face_locations(image)
    face_encodings = frg.face_encodings(image,face_locations)
    results = []
    
    for (top,right,bottom,left),face_encoding in zip(face_locations,face_encodings):
        matches = frg.compare_faces(known_encoding,face_encoding,tolerance=TOLERANCE)
        distance = frg.face_distance(known_encoding,face_encoding)
        name = 'Unknown'
        id = 'Unknown'
        if True in matches:
            match_index = matches.index(True)
            name = database[match_index]['name']
            id = database[match_index]['id']
            distance = round(distance[match_index],2)
            cv2.putText(image,str(distance),(left,top-30),cv2.FONT_HERSHEY_SIMPLEX,0.75,(0,255,0),2)
            # Add to results if known person
            if id != 'Unknown':
                confidence = 1 - distance  # Convert distance to confidence score
                results.append({
                    'name': name, 
                    'id': id, 
                    'confidence': round(confidence, 2),
                    'face_location': (top, right, bottom, left)
                })
                
        cv2.rectangle(image,(left,top),(right,bottom),(0,255,0),2)
        cv2.putText(image,name,(left,top-10),cv2.FONT_HERSHEY_SIMPLEX,0.75,(0,255,0),2)
    return image, name, id, results

def isFaceExists(image): 
    try:
        if image is None:
            return False
            
        # Ensure image is in the correct format
        if type(image) != np.ndarray:
            return False
            
        # Use a smaller image for faster face detection
        small_image = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)
            
        face_location = frg.face_locations(small_image)
        return len(face_location) > 0
    except Exception as e:
        print(f"Error in face detection: {str(e)}")
        return False

def submitNew(name, id, image, old_idx=None):
    database = get_databse()
    #Read image 
    try:
        if type(image) != np.ndarray:
            image = cv2.imdecode(np.fromstring(image.read(), np.uint8), 1)

        # Check if image was loaded correctly
        if image is None or image.size == 0:
            print("Error: Image could not be processed")
            return -1

        isFaceInPic = isFaceExists(image)
        if not isFaceInPic:
            return -1
            
        #Encode image
        encoding = frg.face_encodings(image)[0]
        #Append to database
        #check if id already exists
        existing_id = [database[i]['id'] for i in database.keys()]
        #Update mode 
        if old_idx is not None: 
            new_idx = old_idx
        #Add mode
        else: 
            if id in existing_id:
                return 0
            new_idx = len(database)
        
        # Create database backup before modifying
        backup_database()
        
        # Add metadata
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        database[new_idx] = {
            'image': image,
            'id': id, 
            'name': name,
            'encoding': encoding,
            'added_on': timestamp,
            'last_updated': timestamp
        }
        
        # Save image to dataset directory for backup
        image_filename = f"{id}_{name.replace(' ', '_')}.jpg"
        image_path = os.path.join(DATASET_DIR, image_filename)
        cv2.imwrite(image_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        
        with open(PKL_PATH, 'wb') as f:
            pkl.dump(database, f)
            
        # Log the action
        log_activity(f"Added/Updated user {name} (ID: {id})")
        return True
    except Exception as e:
        print(f"Error in submitNew: {str(e)}")
        return -1

def get_info_from_id(id): 
    database = get_databse() 
    for idx, person in database.items(): 
        if person['id'] == id: 
            name = person['name']
            image = person['image']
            return name, image, idx       
    return None, None, None

def deleteOne(id):
    database = get_databse()
    id = str(id)
    deleted = False
    person_name = ""
    
    # Create backup before deleting
    backup_database()
    
    for key, person in database.items():
        if person['id'] == id:
            person_name = person['name']
            del database[key]
            deleted = True
            break
            
    with open(PKL_PATH,'wb') as f:
        pkl.dump(database,f)
        
    # Remove image from dataset directory if it exists
    if person_name:
        pattern = f"{id}_{person_name.replace(' ', '_')}.jpg"
        for file in os.listdir(DATASET_DIR):
            if file.startswith(f"{id}_"):
                try:
                    os.remove(os.path.join(DATASET_DIR, file))
                    print(f"Deleted file: {file}")
                except Exception as e:
                    print(f"Error deleting file {file}: {e}")
    
    if deleted:
        log_activity(f"Deleted user with ID: {id} (Name: {person_name})")
        
    return deleted

def build_dataset():
    counter = 0
    for image in os.listdir(DATASET_DIR):
        image_path = os.path.join(DATASET_DIR,image)
        if not image_path.endswith(('.jpg', '.jpeg', '.png')):
            continue
            
        try:
            image_name = image.split('.')[0]
            parsed_name = image_name.split('_')
            
            if len(parsed_name) < 2:
                print(f"Warning: Image {image} doesn't follow naming convention: id_name.jpg")
                continue
                
            person_id = parsed_name[0]
            person_name = ' '.join(parsed_name[1:])
            
            image_data = frg.load_image_file(image_path)
            face_encodings = frg.face_encodings(image_data)
            
            if not face_encodings:
                print(f"Warning: No face found in {image_path}")
                continue
                
            information[counter]['image'] = image_data 
            information[counter]['id'] = person_id
            information[counter]['name'] = person_name
            information[counter]['encoding'] = face_encodings[0]
            information[counter]['added_on'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            information[counter]['last_updated'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            counter += 1
        except Exception as e:
            print(f"Error processing {image_path}: {e}")

    # Create a backup before saving
    if os.path.exists(PKL_PATH):
        backup_database()
        
    with open(PKL_PATH,'wb') as f:
        pkl.dump(information,f)
        
    log_activity(f"Rebuilt dataset with {counter} entries")
    return counter

def record_attendance(people_detected):
    """Record attendance for detected people"""
    # Initialize attendance database if it doesn't exist
    if not os.path.exists(ATTENDANCE_PATH):
        attendance_db = {}
        with open(ATTENDANCE_PATH, 'wb') as f:
            pkl.dump(attendance_db, f)
    
    # Load attendance database
    try:
        with open(ATTENDANCE_PATH, 'rb') as f:
            attendance_db = pkl.load(f)
    except:
        attendance_db = {}
    
    # Get today's date as string
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    
    # Initialize today's records if not exists
    if today not in attendance_db:
        attendance_db[today] = {}
    
    current_time = datetime.datetime.now().strftime('%H:%M:%S')
    
    # Record each person's attendance
    for person in people_detected:
        person_id = person['id']
        if person_id != 'Unknown':
            if person_id not in attendance_db[today]:
                # Record new attendance
                status = determine_attendance_status(current_time)
                attendance_db[today][person_id] = {
                    'name': person['name'],
                    'time': current_time,
                    'status': status,
                    'method': 'Automatic',
                    'notes': 'Face recognition check-in'
                }
    
    # Save updated attendance database
    with open(ATTENDANCE_PATH, 'wb') as f:
        pkl.dump(attendance_db, f)
    
    return True

def record_manual_attendance(people, date_str=None, time_str=None, status="Present", notes=""):
    """Record attendance manually with optional date, time and status"""
    if not date_str:
        date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    if not time_str:
        time_str = datetime.datetime.now().strftime('%H:%M:%S')
    
    # Initialize attendance database if it doesn't exist
    if not os.path.exists(ATTENDANCE_PATH):
        attendance_db = {}
        with open(ATTENDANCE_PATH, 'wb') as f:
            pkl.dump(attendance_db, f)
    
    # Load attendance database
    try:
        with open(ATTENDANCE_PATH, 'rb') as f:
            attendance_db = pkl.load(f)
    except:
        attendance_db = {}
    
    # Initialize date's records if not exists
    if date_str not in attendance_db:
        attendance_db[date_str] = {}
    
    # Record each person's attendance
    for person in people:
        person_id = person['id']
        if person_id != 'Unknown':
            # Record with manual flag
            attendance_db[date_str][person_id] = {
                'name': person['name'],
                'time': time_str,
                'status': status,
                'method': 'Manual',
                'notes': notes
            }
    
    # Save updated attendance database
    with open(ATTENDANCE_PATH, 'wb') as f:
        pkl.dump(attendance_db, f)
        
    log_activity(f"Manual attendance recorded for {len(people)} people on {date_str}")
    return True

def determine_attendance_status(time_str):
    """Determine attendance status based on time of day and settings"""
    # Load settings or use defaults
    try:
        with open('config.yaml', 'r') as f:
            cfg = yaml.load(f, Loader=yaml.FullLoader)
        
        start_hour = cfg.get('ATTENDANCE', {}).get('START_HOUR', 9)
        start_minute = cfg.get('ATTENDANCE', {}).get('START_MINUTE', 0)
        late_threshold_minutes = cfg.get('ATTENDANCE', {}).get('LATE_THRESHOLD_MINUTES', 15)
    except:
        # Default values
        start_hour = 9
        start_minute = 0
        late_threshold_minutes = 15
    
    # Parse the current time
    current_time = datetime.datetime.strptime(time_str, '%H:%M:%S').time()
    
    # Create time objects for comparison
    start_time = datetime.time(hour=start_hour, minute=start_minute)
    late_time = (datetime.datetime.combine(datetime.date.today(), start_time) + 
                datetime.timedelta(minutes=late_threshold_minutes)).time()
    
    # Determine status
    if current_time <= start_time:
        return "On Time"
    elif current_time <= late_time:
        return "Late"
    else:
        return "Very Late"

def get_attendance_data(date=None):
    """Get attendance data for a specific date or all dates"""
    if not os.path.exists(ATTENDANCE_PATH):
        return {}
    
    with open(ATTENDANCE_PATH, 'rb') as f:
        attendance_db = pkl.load(f)
    
    if date:
        return attendance_db.get(date, {})
    return attendance_db

def get_attendance_dataframe(date=None):
    """Convert attendance data to pandas DataFrame for reporting"""
    attendance_data = get_attendance_data(date)
    
    if not attendance_data:
        return pd.DataFrame(columns=['Date', 'ID', 'Name', 'Time', 'Status', 'Method', 'Notes'])
    
    records = []
    if date:
        for person_id, details in attendance_data.items():
            records.append({
                'Date': date,
                'ID': person_id,
                'Name': details['name'],
                'Time': details['time'],
                'Status': details['status'],
                'Method': details.get('method', 'Automatic'),
                'Notes': details.get('notes', '')
            })
    else:
        for date, daily_data in attendance_data.items():
            for person_id, details in daily_data.items():
                records.append({
                    'Date': date,
                    'ID': person_id,
                    'Name': details['name'],
                    'Time': details['time'],
                    'Status': details['status'],
                    'Method': details.get('method', 'Automatic'),
                    'Notes': details.get('notes', '')
                })
    
    return pd.DataFrame(records)

def backup_database():
    """Create a backup of the database"""
    try:
        if os.path.exists(PKL_PATH):
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(BACKUP_DIR, f'database_backup_{timestamp}.pkl')
            shutil.copy2(PKL_PATH, backup_file)
            return backup_file
    except Exception as e:
        print(f"Backup failed: {e}")
        return None

def backup_attendance():
    """Create a backup of attendance data"""
    try:
        if os.path.exists(ATTENDANCE_PATH):
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(BACKUP_DIR, f'attendance_backup_{timestamp}.pkl')
            shutil.copy2(ATTENDANCE_PATH, backup_file)
            return backup_file
    except Exception as e:
        print(f"Attendance backup failed: {e}")
        return None

def log_activity(message):
    """Log system activity"""
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_file = os.path.join(LOGS_DIR, f'system_{datetime.datetime.now().strftime("%Y%m%d")}.log')
    
    with open(log_file, 'a') as f:
        f.write(f"[{timestamp}] {message}\n")

def get_student_statistics(student_id):
    """Get attendance statistics for a specific student"""
    all_attendance = get_attendance_data()
    
    if not all_attendance:
        return {}
    
    student_records = []
    for date, daily_data in all_attendance.items():
        if student_id in daily_data:
            record = daily_data[student_id]
            student_records.append({
                'Date': date,
                'Time': record['time'],
                'Status': record['status']
            })
    
    if not student_records:
        return {}
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(student_records)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    
    # Calculate statistics
    total_days = len(df)
    on_time_days = len(df[df['Status'] == 'On Time'])
    late_days = len(df[df['Status'] == 'Late'])
    very_late_days = len(df[df['Status'] == 'Very Late'])
    
    # Calculate average arrival time
    df['TimeObj'] = pd.to_datetime(df['Time'], format='%H:%M:%S').dt.time
    avg_hour = sum(t.hour for t in df['TimeObj']) / len(df['TimeObj'])
    avg_minute = sum(t.minute for t in df['TimeObj']) / len(df['TimeObj'])
    avg_time = f"{int(avg_hour):02d}:{int(avg_minute):02d}"
    
    # First and last dates
    first_date = df['Date'].min().strftime('%Y-%m-%d')
    last_date = df['Date'].max().strftime('%Y-%m-%d')
    
    # Calculate attendance by day of week
    df['DayOfWeek'] = df['Date'].dt.day_name()
    day_counts = df.groupby('DayOfWeek').size().to_dict()
    
    return {
        'total_days': total_days,
        'on_time_count': on_time_days,
        'on_time_percent': (on_time_days / total_days * 100) if total_days else 0,
        'late_count': late_days,
        'late_percent': (late_days / total_days * 100) if total_days else 0,
        'very_late_count': very_late_days,
        'very_late_percent': (very_late_days / total_days * 100) if total_days else 0,
        'avg_arrival_time': avg_time,
        'first_date': first_date,
        'last_date': last_date,
        'day_of_week_stats': day_counts
    }

def generate_analytics_report(start_date=None, end_date=None):
    """Generate comprehensive analytics report for a date range"""
    if not start_date:
        # Default to last 30 days
        end_date = datetime.datetime.now().date()
        start_date = end_date - datetime.timedelta(days=30)
    elif not end_date:
        # If only start_date provided, use today as end_date
        end_date = datetime.datetime.now().date()
    
    # Get date range
    date_range = pd.date_range(start=start_date, end=end_date)
    date_strings = [d.strftime('%Y-%m-%d') for d in date_range]
    
    # Get all attendance data in range
    all_data = []
    for date_str in date_strings:
        df = get_attendance_dataframe(date_str)
        if not df.empty:
            all_data.append(df)
    
    if not all_data:
        return {
            'status': 'empty',
            'message': 'No attendance data found for the selected date range'
        }
    
    # Combine all data
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Basic statistics
    total_records = len(combined_df)
    unique_students = combined_df['ID'].nunique()
    days_with_records = combined_df['Date'].nunique()
    
    # Status distribution
    status_counts = combined_df['Status'].value_counts().to_dict()
    
    # Time statistics
    combined_df['TimeObj'] = pd.to_datetime(combined_df['Time'], format='%H:%M:%S').dt.time
    combined_df['Hour'] = pd.to_datetime(combined_df['Time'], format='%H:%M:%S').dt.hour
    
    hour_distribution = combined_df['Hour'].value_counts().sort_index().to_dict()
    
    # Day of week analysis
    combined_df['DateObj'] = pd.to_datetime(combined_df['Date'])
    combined_df['DayOfWeek'] = combined_df['DateObj'].dt.day_name()
    day_of_week_counts = combined_df['DayOfWeek'].value_counts().to_dict()
    
    # Student statistics
    student_attendance = combined_df.groupby(['ID', 'Name']).size().reset_index(name='AttendanceCount')
    student_attendance = student_attendance.sort_values('AttendanceCount', ascending=False)
    
    top_attendees = student_attendance.head(10)[['ID', 'Name', 'AttendanceCount']].to_dict('records')
    
    # Method distribution
    method_counts = combined_df['Method'].value_counts().to_dict()
    
    # Create report
    report = {
        'status': 'success',
        'date_range': {
            'start': start_date.strftime('%Y-%m-%d') if isinstance(start_date, datetime.date) else start_date,
            'end': end_date.strftime('%Y-%m-%d') if isinstance(end_date, datetime.date) else end_date,
            'total_days': len(date_range)
        },
        'summary': {
            'total_records': total_records,
            'unique_students': unique_students,
            'days_with_records': days_with_records,
            'attendance_rate': round((days_with_records / len(date_range)) * 100, 1)
        },
        'status_distribution': status_counts,
        'time_analysis': {
            'hour_distribution': hour_distribution
        },
        'day_analysis': day_of_week_counts,
        'top_attendees': top_attendees,
        'method_distribution': method_counts
    }
    
    return report

def export_attendance_to_csv(start_date=None, end_date=None, file_path=None):
    """Export attendance data to CSV file"""
    if start_date and end_date:
        # Get data for date range
        date_range = pd.date_range(start=start_date, end=end_date)
        date_strings = [d.strftime('%Y-%m-%d') for d in date_range]
        
        all_data = []
        for date_str in date_strings:
            df = get_attendance_dataframe(date_str)
            if not df.empty:
                all_data.append(df)
        
        if not all_data:
            return False
        
        export_df = pd.concat(all_data, ignore_index=True)
    elif start_date:
        # Get data for single date
        export_df = get_attendance_dataframe(start_date)
    else:
        # Get all data
        export_df = get_attendance_dataframe()
    
    if export_df.empty:
        return False
    
    # Generate default filepath if none provided
    if not file_path:
        if not os.path.exists('exports'):
            os.makedirs('exports')
        
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = f"exports/attendance_export_{timestamp}.csv"
    
    # Export to CSV
    export_df.to_csv(file_path, index=False)
    log_activity(f"Exported attendance data to {file_path}")
    
    return file_path

def export_attendance_to_excel(start_date=None, end_date=None, file_path=None):
    """Export attendance data to formatted Excel file"""
    # Get the data same as CSV export
    if start_date and end_date:
        date_range = pd.date_range(start=start_date, end=end_date)
        date_strings = [d.strftime('%Y-%m-%d') for d in date_range]
        
        all_data = []
        for date_str in date_strings:
            df = get_attendance_dataframe(date_str)
            if not df.empty:
                all_data.append(df)
        
        if not all_data:
            return False
        
        export_df = pd.concat(all_data, ignore_index=True)
    elif start_date:
        export_df = get_attendance_dataframe(start_date)
    else:
        export_df = get_attendance_dataframe()
    
    if export_df.empty:
        return False
    
    # Generate default filepath if none provided
    if not file_path:
        if not os.path.exists('exports'):
            os.makedirs('exports')
        
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = f"exports/attendance_export_{timestamp}.xlsx"
    
    # Export to Excel with formatting
    writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
    
    # Write the main attendance sheet
    export_df.to_excel(writer, sheet_name='Attendance Records', index=False)
    
    # Get access to the workbook and the main worksheet
    workbook = writer.book
    worksheet = writer.sheets['Attendance Records']
    
    # Add formats
    header_format = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'valign': 'top',
        'fg_color': '#D7E4BC',
        'border': 1
    })
    
    # Add a format for dates
    date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})
    
    # Add a format for time
    time_format = workbook.add_format({'num_format': 'hh:mm:ss'})
    
    # Write the column headers with the header format
    for col_num, value in enumerate(export_df.columns.values):
        worksheet.write(0, col_num, value, header_format)
    
    # Set the column width and format based on data
    for i, col in enumerate(export_df.columns):
        column_len = max(export_df[col].astype(str).str.len().max(), len(col) + 2)
        worksheet.set_column(i, i, column_len)
        
        # Apply specific formatting
        if col == 'Date':
            worksheet.set_column(i, i, column_len, date_format)
        elif col == 'Time':
            worksheet.set_column(i, i, column_len, time_format)
    
    # Add analytics sheet with summary
    analytics_df = pd.DataFrame({
        'Metric': ['Total Records', 'Unique Students', 'Date Range'],
        'Value': [
            len(export_df),
            export_df['ID'].nunique(),
            f"{export_df['Date'].min()} to {export_df['Date'].max()}"
        ]
    })
    
    analytics_df.to_excel(writer, sheet_name='Summary', index=False)
    
    # Save the workbook
    writer.save()
    
    log_activity(f"Exported attendance data to Excel: {file_path}")
    return file_path

def import_attendance_from_csv(file_path):
    """Import attendance records from CSV file"""
    try:
        # Read CSV file
        import_df = pd.read_csv(file_path)
        
        # Validate required columns
        required_cols = ['ID', 'Name', 'Date', 'Time', 'Status']
        missing_cols = [col for col in required_cols if col not in import_df.columns]
        
        if missing_cols:
            return {
                'success': False,
                'message': f"Missing required columns: {', '.join(missing_cols)}"
            }
        
        # Load existing attendance database
        if not os.path.exists(ATTENDANCE_PATH):
            attendance_db = {}
        else:
            with open(ATTENDANCE_PATH, 'rb') as f:
                attendance_db = pkl.load(f)
        
        # Create backup before modifying
        backup_attendance()
        
        # Add records from CSV
        records_added = 0
        for _, row in import_df.iterrows():
            date = row['Date']
            student_id = str(row['ID'])
            
            # Initialize date in db if not exists
            if date not in attendance_db:
                attendance_db[date] = {}
            
            # Add or update record
            attendance_db[date][student_id] = {
                'name': row['Name'],
                'time': row['Time'],
                'status': row['Status'],
                'method': 'Imported' if 'Method' not in row else row['Method'],
                'notes': '' if 'Notes' not in row else row['Notes']
            }
            records_added += 1
        
        # Save updated database
        with open(ATTENDANCE_PATH, 'wb') as f:
            pkl.dump(attendance_db, f)
        
        log_activity(f"Imported {records_added} attendance records from {file_path}")
        
        return {
            'success': True,
            'message': f"Successfully imported {records_added} records",
            'records_added': records_added
        }
    except Exception as e:
        return {
            'success': False,
            'message': f"Error importing records: {str(e)}"
        }

# Create a simple initialization function for first-time setup
def initialize_system():
    """Initialize the system with default directories and settings"""
    try:
        # Create required directories
        for directory in [DATASET_DIR, LOGS_DIR, BACKUP_DIR, 'exports']:
            Path(directory).mkdir(exist_ok=True)
        
        # Create empty database if it doesn't exist
        if not os.path.exists(PKL_PATH):
            with open(PKL_PATH, 'wb') as f:
                pkl.dump({}, f)
        
        # Create empty attendance database if it doesn't exist
        if not os.path.exists(ATTENDANCE_PATH):
            with open(ATTENDANCE_PATH, 'wb') as f:
                pkl.dump({}, f)
        
        log_activity("System initialized successfully")
        return True
    except Exception as e:
        print(f"Error initializing system: {e}")
        return False

if __name__ == "__main__": 
    deleteOne(4)

