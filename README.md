# 📊 Survey Data Management System (Dashboard)

A robust, standalone Windows desktop application designed to streamline the upload, cleaning, and management of university survey data. Built with modern web-based UI technologies but packaged as a lightweight, offline Windows executable.

## 🚀 Key Features

- **Interactive GUI:** Modern, highly responsive user interface with dynamic sidebars and styling.
- **5 Dedicated Modules:** Seamlessly navigate between:
  1. Home
  2. Student Satisfaction
  3. Exit Survey
  4. Graduate Employability
  5. Database Management
- **Automated Data Processing:** Upload raw CSV files, perform automated data cleaning, and securely map them to the database.
- **Secure Authentication:** Admin login portal with encrypted password update functionality.
- **Local Offline Storage:** Fully integrated SQLite database (`survey.db`) for secure local data retention.
- **Standalone Windows App:** Packaged as a `.exe` file, complete with a professional Windows Setup Installer.

## 🛠️ Technologies Used

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![NiceGUI](https://img.shields.io/badge/NiceGUI-UI_Framework-17b897?style=for-the-badge)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)
![PyInstaller](https://img.shields.io/badge/PyInstaller-Compilation-00529B?style=for-the-badge)
![Inno Setup](https://img.shields.io/badge/Inno_Setup-Windows_Installer-lightgrey?style=for-the-badge&logo=windows)

- **Programming Language:** Python 3
- **UI Framework:** [NiceGUI](https://nicegui.io/) (FastAPI & Vue.js based)
- **Database:** SQLite3
- **Executable Compilation:** PyInstaller (Compiled with custom icons)
- **Windows Installer:** Inno Setup Compiler 6 (Custom AppData installation for write-access)
- **Version Control:** Git & GitHub

## 🎥 Module Demonstrations & Walkthrough

Below are the demonstrations of the 5 main pages. All demonstration videos are stored locally in the `upload/` directory of this repository.

### 1. Home
*Overview of the dashboard, main navigation, and system status.*
<video src="upload/home_video.mp4" controls="controls" width="100%">
</video>

### 2. Student Satisfaction
*Managing, cleaning, and visualizing student satisfaction survey datasets.*
<video src="upload/student_satisfaction_video.mp4" controls="controls" width="100%">
</video>

### 3. Exit Survey
*Handling exit survey records and analyzing feedback.*
<video src="upload/exit_survey_video.mp4" controls="controls" width="100%">
</video>

### 4. Graduate Employability
*Tracking and managing graduate employability statistics.*
<video src="upload/graduate_employability_video.mp4" controls="controls" width="100%">
</video>

### 5. Database Management
*Admin controls, changing secure passwords, and raw database handling.*
<video src="upload/database_management_video.mp4" controls="controls" width="100%">
</video>

---

## ⚙️ Installation & Usage Instructions

### Option 1: Using the Windows Installer (Recommended)
1. Navigate to the `Releases` section of this repository.
2. Download **`Survey_Dashboard_Setup.exe`**.
3. Run the installer and follow the modern wizard instructions.
4. Launch the application from your Desktop shortcut or Start Menu. *(Note: Installed in localappdata to ensure SQLite write permissions).*

### Option 2: Portable Version
1. Download the portable `Survey_Dashboard.exe` and the `survey.db` file.
2. Place both files in the same folder on your computer or a USB drive.
3. Double-click `Survey_Dashboard.exe` to run the app instantly—no installation required!

### Option 3: Running from Source
1. Clone this repository:
   ```bash
   git clone [https://github.com/yourusername/Survey_Dashboard.git](https://github.com/yourusername/Survey_Dashboard.git)