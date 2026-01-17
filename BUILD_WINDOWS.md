# Building Campaign Manager 2026 for Windows

## Prerequisites
1. Install Python 3.10+ from https://python.org
2. Download this project folder to your Windows PC

## Build Steps

Open Command Prompt or PowerShell in the project folder and run:

```cmd
# Create virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\activate

# Install dependencies
pip install rich pyinstaller

# Build executable
pyinstaller --onefile --console --name "CampaignManager2026" main.py
```

## Result
The executable will be created at:
```
dist\CampaignManager2026.exe
```

Double-click to play, or run from Command Prompt.

## Troubleshooting
- If you get "python not found", make sure Python is added to PATH during installation
- If antivirus blocks it, add an exception for the dist folder
