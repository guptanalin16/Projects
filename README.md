# Smart Attendance System Using Face Recognition
A project developed as part of the Bachelor of Technology in Computer Science Engineering and Information Technology program at The NorthCap University, Gurugram.

**Author:**
* Nalin Gupta 

## 📝 Overview

This project presents a **Smart Attendance System** that leverages facial recognition technology to automate attendance tracking in educational and professional settings. It aims to replace inefficient and error-prone manual methods with a contactless, real-time, and accurate solution, reducing administrative overhead and potential fraud.

The system captures facial images via webcam or uploads, compares them against a database of known individuals, and automatically records attendance in a CSV file. It features a user-friendly web interface built with Streamlit for easy interaction, configuration, and viewing of attendance reports and analytics.

## ✨ Key Features

* **Real-time Face Recognition:** Identifies individuals using a webcam feed.
* **Image Upload:** Allows attendance marking via uploaded images.
* **Automated Attendance Logging:** Records attendance with names and timestamps in a CSV file.
* **User Management:** Interface for adding, viewing, and potentially managing users (students/employees) and their facial data.
* **Data Visualization:** Displays attendance summaries and analytics using graphs.
* **Configurable Settings:**
    * Adjust camera resolution (Low, Medium, High).
    * Set face recognition confidence threshold.
    * Theme selection (Light/Dark).
* **Manual Entry:** Option for administrators to manually record or correct attendance.
* **Reporting:** Export attendance logs (potentially to Excel).
* **Mobile Access:** A dedicated interface for quick check-in using a selfie.
* **Persistent Storage:** Uses local CSV files for storing attendance and user data (minimal infrastructure required).

## 💻 Technology Stack

* **Language:** Python
* **Face Recognition:** `face_recognition` (based on dlib)
* **Web Framework/UI:** Streamlit
* **Image Processing:** OpenCV (`opencv-python`)
* **Data Handling:** Pandas
* **Configuration:** PyYAML (`pyyaml`)
* **Plotting (Implied):** Matplotlib, Seaborn (mentioned in the report for analytics)

## ⚙️ Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd <repository-directory>
    ```
2.  **Install dependencies:** Ensure you have Python and pip installed. Then, install the required libraries using the `requirements.txt` file:
    ```bash
    pip install -r requirements.txt
    ```
    *(The `requirements.txt` file should contain at least the following):*
    ```txt
    streamlit
    opencv-python
    face_recognition
    pyyaml
    pandas
    # Add matplotlib and seaborn if used directly for plotting
    ```
3.  **Prepare User Data:**
    * Ensure you have a mechanism or script to enroll users, capture their facial images, generate encodings, and store them (e.g., in `database.pkl` as suggested in the DFD).
    * Create necessary directories (e.g., `test_images/`, `dataset/`) if needed by the scripts.
4.  **Configuration:** Modify the `config.yaml` file to adjust system settings like prompts, titles, or default values if necessary.

## ▶️ Usage

1.  **Run the Streamlit application:**
    ```bash
    streamlit run Tracking.py
    ```
    *(Replace `Tracking.py` with the actual name of your main Streamlit script if different)*
2.  **Access the UI:** Open your web browser and navigate to the local URL provided by Streamlit (usually `http://localhost:8501`).
3.  **Mark Attendance:**
    * Use the "Tracking" or "Attendance" section.
    * Start the camera or upload an image.
    * The system will attempt to recognize faces and log attendance.
4.  **Manage Users:** Navigate to the "Database" or "Updating" section to add new users and their photos.
5.  **View Reports:** Access the "Reports" or "Dashboard" section to view attendance summaries and analytics.
6.  **Adjust Settings:** Use the "Settings" page to configure resolution, tolerance, etc.

## 🚀 Future Enhancements (Based on Report)

* Improve robustness to varying light conditions and facial angles.
* Implement multi-factor authentication (e.g., PIN + Face).
* Add more advanced real-time analytics and trend analysis.
* Support for multiple locations/campuses.
* Enhanced mobile experience with push notifications.
* Integrate machine learning for adaptive accuracy improvements.
* Integration with other institutional systems (scheduling, HR).
