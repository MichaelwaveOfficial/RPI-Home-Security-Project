
# 🏠 RPI Home Security Project

### ⚠️ Work in Progress

This project is currently an ongoing development and currently visible for demonstration purposes only. Further documentation
    will be provided as the project expands and features are implemented.

The aim is to proivde an accessible, customisable home security system leveraging a lower spec Raspberry Pi. This system 
processes motion, tracks detections and annotates them for you whilst giving the user access and control through the Flask 
web server where these captures can be accessed and emailed to your account.

This is a reattempt at what I envision my spin on accessbile home security should be and what it can offer.

## 📖 Table of Contents

-[Features](#Features)
-[Prerequisites](#Prerequisites)
-[Setup](#Setup)
-[Configuration](#Configuration)
-[RunningTheProject](#Run)

# 🚀 Features

    ✔️ Motion Detection
    ✔️ Object Detection
    ✔️ Object Tracking
    ✔️ Customizable Settings
    ✔️ Locally hosted web server

# 🔧 Prerequisites

    * In order for this project to be viable, these components are required. 

    ### Hardware:

        Raspberry Pi (--Model 4B onwards)
        Pi Camera Module V2
        MicroSD (--min 16GB, --class 10)
        Internet Connection

    ### Software:

        Raspberry Pi OS (Insert tutorial link here.)
        Python 3.11
        Gmail Account (Required for email alerts)

# 🛠 Setup

Clone this git repo with:

    * git clone https://github.com/MichaelwaveOfficial/rpi_security_system_rebuild_25.git

    * cd project folder

Install dependencies:

    * pip install -r requirements.txt 

# ⚙️ Configuration

    * setting up email alerts.

    In order for the email alerts to work, you will need to generate an app password from your google account
    which will 

    1. Log into current/create a new gmail account.

    2. Find Security > App Passwords.

    3. generate app password in settings, keep that safe!

Update the .env file with your credentials:

    * APP_EMAIL=example@gmail.com
    * APP_PASSWORD=your-generated-app-password
    * TARGET_EMAIL=recipient@email.com

# ▶️ Run

Run the project:

    * python main.py

