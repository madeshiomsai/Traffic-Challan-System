# 🚦 AI-Based Traffic Challan System

An AI-powered **Traffic Violation Detection and E-Challan Management System** built with **Python, Streamlit, Groq Vision AI, and SQLite**.

The system analyzes traffic images to identify common violations, extracts the vehicle registration number, retrieves registered vehicle-owner information, calculates the applicable fine, records the challan, and provides WhatsApp-based notification support.

---

## 📌 Project Overview

Traditional traffic enforcement can require manual inspection of vehicles, identification of violations, and preparation of challans.

This project aims to simplify that workflow by combining **Computer Vision / Vision AI, database management, and a web-based dashboard** into one system.

The application allows a user to upload a traffic image and automatically:

1. Detect the traffic violation.
2. Read the vehicle number plate.
3. Identify the registered vehicle owner.
4. Retrieve the corresponding fine amount.
5. Generate and record a challan entry.
6. Maintain challan history.
7. Notify the vehicle owner through WhatsApp.
8. Manage registered vehicle information.

---

## ✨ Features

### 🤖 AI-Based Violation Detection

The system uses a **Groq Vision Model** to analyze uploaded traffic images.

Currently supported violations:

* 🏍️ Triple Ride
* 🚫 No Parking
* 🪖 No Helmet
* ⚡ Overspeed

The model is instructed to return a standardized violation category, which is then processed by the application.

---

### 🔢 Number Plate Detection

The system uses the vision model to extract the vehicle registration number from the uploaded traffic image.

Example:

```text
TS10ED8176
TS09PA3330
TS10EX2850
```

The extracted registration number is normalized before database matching to improve consistency.

---

### 👤 Vehicle Owner Lookup

After detecting the number plate, the system searches the registered-user SQLite database.

Owner information can include:

* Driver/Owner Name
* Vehicle Registration Number
* Vehicle Type
* Vehicle ID
* Mobile Number

Only text-based owner information is used by the current system.

---

### 💰 Automatic Fine Lookup

The application maintains violation and fine information in the SQLite database.

When a violation is detected, the corresponding fine is retrieved automatically.

```text
Violation → Database Lookup → Fine Amount
```

---

### 🧾 Challan History

Every generated challan can be recorded in the `challans` database table.

The system maintains information such as:

* Driver name
* Vehicle registration
* Vehicle type
* Violation
* Fine
* Mobile number
* Challan date
* Notification status

This makes it possible to review previously issued challans.

---

### 📱 WhatsApp Notification

The system provides WhatsApp notification support using a `wa.me` link.

The notification message can be prepared with the relevant challan information and opened in WhatsApp Web/App.

> This implementation does not use the paid WhatsApp Business API.

---

### 📊 Streamlit Dashboard

The project provides a web-based interface built with **Streamlit**.

The application contains functionality for:

* Traffic image upload
* AI violation detection
* Number plate detection
* Owner information lookup
* Fine calculation
* Challan creation
* Challan history
* Registered-user management
* WhatsApp notification

---

## 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │      User           │
                    │ Uploads Image       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Streamlit Web App  │
                    │       app.py        │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │    Groq Vision AI   │
                    └──────────┬──────────┘
                               │
                  ┌────────────┴────────────┐
                  │                         │
                  ▼                         ▼
        ┌──────────────────┐      ┌──────────────────┐
        │ Violation        │      │ Number Plate     │
        │ Detection        │      │ Detection        │
        └────────┬─────────┘      └────────┬─────────┘
                 │                         │
                 ▼                         ▼
        ┌──────────────────┐      ┌──────────────────┐
        │ Fine Database    │      │ User Database    │
        │   Chalan.db      │      │     user.db      │
        └────────┬─────────┘      └────────┬─────────┘
                 │                         │
                 └────────────┬────────────┘
                              ▼
                    ┌─────────────────────┐
                    │   Challan Record    │
                    │   & History         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ WhatsApp Notification│
                    └─────────────────────┘
```

---

## 🧠 How the System Works

### Step 1 — Upload Traffic Image

The user uploads an image containing a traffic situation through the Streamlit interface.

### Step 2 — Detect Violation

The image is converted into Base64 and sent to the configured Groq vision model.

The model identifies one of the supported violations:

```text
Triple Ride
No Parking
No Helmet
Overspeed
```

### Step 3 — Detect Number Plate

The same image is analyzed to extract the vehicle registration number.

The application cleans the result and converts it into a standardized alphanumeric format.

### Step 4 — Find Vehicle Owner

The detected registration number is compared with records stored in `user.db`.

If a matching vehicle is found, the registered owner's information is retrieved.

### Step 5 — Find Fine

The detected violation is matched against the `violations` table in `Chalan.db`.

The corresponding fine amount is returned.

### Step 6 — Create Challan Record

The challan information is inserted into the `challans` table.

The record contains information about the:

* Driver
* Vehicle
* Violation
* Fine
* Mobile number
* Date
* Notification status

### Step 7 — Notify Owner

The system can prepare a WhatsApp message containing the challan information and open it through WhatsApp.

### Step 8 — View Challan History

Previously generated challans can be reviewed through the **Challan History** page.

---

## 🛠️ Technology Stack

| Technology               | Purpose                                     |
| ------------------------ | ------------------------------------------- |
| 🐍 Python                | Core programming language                   |
| 🎨 Streamlit             | Web application and dashboard               |
| 🤖 Groq Vision AI        | Traffic violation and number-plate analysis |
| 🗄️ SQLite               | Database management                         |
| 📱 WhatsApp `wa.me`      | Notification support                        |
| 🔐 Environment Variables | API key configuration                       |

---

## 📂 Project Structure

```text
Traffic-Challan-System/
│
├── 📁 images/
│   └── Sample traffic images
│
├── 📁 pages/
│   ├── 1_Challan_History.py
│   └── 2_User_Database.py
│
├── 📄 app.py
│   └── Main Streamlit application
│
├── 📄 violation_detection.py
│   └── AI detection, number plate detection,
│       fine lookup, owner lookup and challan logging
│
├── 📄 database_setup.py
│   └── Database/table setup
│
├── 📄 config.py
│   └── Application configuration and API settings
│
├── 📄 requirements.txt
│   └── Python dependencies
│
├── 📄 .gitignore
│   └── Files excluded from Git
│
├── 🗄️ Chalan.db
│   └── Violation, fine and challan history database
│
└── 🗄️ user.db
    └── Registered vehicle-owner database
```

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/madeshiomsai/Traffic-Challan-System.git
```

Move into the project directory:

```bash
cd Traffic-Challan-System
```

---

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

For macOS/Linux:

```bash
source venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Configure Groq API Key

The project requires a Groq API key for vision-model processing.

Set the API key as an environment variable.

### Windows PowerShell

```powershell
$env:GROQ_API_KEY="your_api_key_here"
```

### Windows CMD

```cmd
set GROQ_API_KEY=your_api_key_here
```

### macOS/Linux

```bash
export GROQ_API_KEY="your_api_key_here"
```

You can also use a `.env` file if your configuration supports it:

```env
GROQ_API_KEY=your_api_key_here
```

**Never commit your real API key to GitHub.**

---

## 🗄️ Database Setup

If the database tables need to be recreated:

```bash
python database_setup.py
```

The project uses SQLite databases for storing:

* Violation/fine information
* Registered vehicle owners
* Challan history

---

## ▶️ Run the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

Streamlit will provide a local URL where you can access the application.

---

## 📱 WhatsApp Notification Flow

The notification workflow is:

```text
Challan Created
      ↓
Owner Mobile Number Retrieved
      ↓
WhatsApp Message Prepared
      ↓
wa.me Link Generated
      ↓
WhatsApp Web / App Opens
      ↓
Message Can Be Sent
```

The current implementation uses WhatsApp links rather than a paid WhatsApp Business API.

---

## 🗃️ Database Design

### `violations`

Stores violation names and their associated fines.

Example:

```text
Violation        Fine
----------------------
No Helmet        ...
No Parking       ...
Triple Ride      ...
Overspeed        ...
```

### `users`

Stores registered vehicle-owner information.

```text
Name
Vehicle Registration
Vehicle Type
Vehicle ID
Mobile Number
```

### `challans`

Stores generated challan history.

```text
Driver Name
Vehicle Registration
Vehicle Type
Violation
Fine
Mobile Number
Challan Date
Notification Status
```

---

## 🔐 Security

The project is designed to keep API credentials outside the source code.

Use environment variables for sensitive credentials:

```text
GROQ_API_KEY
```

Do not commit:

```text
.env
API keys
Passwords
Private credentials
```

Make sure sensitive files are included in `.gitignore`.

---

## 🎯 Supported Violations

| Violation       | AI Detection |
| --------------- | ------------ |
| 🪖 No Helmet    | ✅            |
| 🏍️ Triple Ride | ✅            |
| 🚫 No Parking   | ✅            |
| ⚡ Overspeed     | ✅            |

---

## 🚀 Future Enhancements

The project can be extended with:

* 🎥 Real-time CCTV/video-stream processing
* 🚦 Traffic signal violation detection
* 🔢 Dedicated license-plate OCR models
* 📍 GPS/location-based challans
* 👮 Police/admin authentication
* 💳 Online fine payment integration
* 📧 Email notifications
* 📱 SMS notifications
* 📊 Advanced traffic analytics
* ☁️ Cloud deployment
* 🔐 Role-based access control
* 🧠 Custom-trained traffic violation detection models
* 📈 Dashboard analytics and reports

---

## ⚠️ Current Limitations

This is an AI-assisted prototype and should not be treated as a fully automated legal enforcement system.

Detection accuracy can depend on:

* Image quality
* Camera angle
* Lighting conditions
* Visibility of the vehicle
* Number-plate clarity
* AI model performance

The current system primarily works with uploaded images rather than a continuously connected traffic-camera network.

---

## 💡 Project Objective

The main objective of this project is to demonstrate how **AI, Computer Vision/Vision Models, databases, and web applications** can be integrated to create an automated traffic violation and challan-management workflow.

```text
AI Detection
     +
Number Plate Recognition
     +
Database Management
     +
Fine Calculation
     +
Challan Management
     +
Notification
     =
AI-Based Traffic Challan System
```

---

## 👨‍💻 Author

**Madeshi Om Sai**

AI/ML & Data Analytics Enthusiast

GitHub:
https://github.com/madeshiomsai

---

## ⭐ Support

If you find this project useful, consider giving the repository a ⭐ on GitHub.

---

## 📄 License

This project is intended for educational and demonstration purposes.
