# 🧹 Google Drive Cleaner

A Python tool to detect and clean duplicate files and folders in your Google Drive.
For now that's all but i'm thinking about compressing big files (movies, pictures, etc...)

---

## ✨ Features

- 🔑 Authenticate securely with your Google account
- 📂 Retrieve and list all files and folders
- 🧠 Detect duplicate folders based on structure and content
- 🧠 Detect duplicate files within folders based on name and modification time (based on regex)
- 🗑️ Move duplicates to trash
- 📝 Optionally rename files to remove duplicate indicators
- 🧪 Save file metadata to JSON for manual verification

---

## 🚀 Getting Started

### Prerequisites

- Python 3.7+
- Google Drive API enabled
- OAuth2 credentials (`client_secret.json`)

### Installation

```bash
git clone https://github.com/yourusername/google-drive-duplicate-cleaner.git
cd google-drive-duplicate-cleaner
pip install -r requirements.txt
```
🚨 I recommend using virtual environments

### Create your Google Drive API (that's free)
See more details [here](https://www.youtube.com/watch?v=9K2P2bWEd90&t=481s&ab_channel=JieJenn)

### Setup
Place your client_secret.json file in the config/ directory.
Run the script:
```bash
python main.py
```

## 🧪 Testing
Tests are located in the tests/ directory. To run tests:
TO DO
Run:
```bash
pytest
```

## 🔧 Configuration
All configuration variables are located in config.py.​

## 📄 License
This project is licensed under the Attribution Assurance License. See the LICENSE file for details.​
Open Source Initiative

## 🙏 Acknowledgments
Developed by Guillaume Poirier. If you use this tool, please provide attribution.