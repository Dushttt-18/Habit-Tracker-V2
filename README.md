# 🌱 Habit Tracker

A clean, modular habit & daily routine tracker built with Streamlit.  
Data is persisted in **Google Sheets** — free, always-on, and visible as a spreadsheet.

---

## Project Structure

```
habit-tracker/
├── app.py                  # Entry point — orchestration only
├── requirements.txt
├── .gitignore
├── config/
│   ├── __init__.py
│   └── settings.py         # All constants & config values
├── modules/
│   ├── __init__.py
│   ├── data.py             # Google Sheets read/write (data layer)
│   ├── stats.py            # Pure analytics — streaks, rates, heatmap
│   ├── ui.py               # CSS loader + reusable HTML components
│   ├── sidebar.py          # Sidebar: add/delete habits, date picker
│   ├── dashboard.py        # Stat cards + progress bar
│   ├── checklist.py        # Daily habit check-off UI
│   └── heatmap.py          # 30-day heatmap section
└── static/
    └── style.css           # All CSS — light theme design tokens
```

---

## Step 1 — Google Sheets Setup

### 1a. Create a Google Cloud project & enable APIs
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project (e.g. `habit-tracker`)
3. Enable **Google Sheets API** and **Google Drive API**
   - Search for each in the API Library and click Enable

### 1b. Create a Service Account
1. Go to **IAM & Admin → Service Accounts**
2. Click **Create Service Account** → give it a name → Done
3. Click on the service account → **Keys** tab → **Add Key → Create new key → JSON**
4. Download the `.json` file — you'll need its contents shortly

### 1c. Create a Google Sheet
1. Go to [sheets.google.com](https://sheets.google.com) and create a new spreadsheet
2. Name it exactly: **`HabitTracker`** (or change `SPREADSHEET_NAME` in `config/settings.py`)
3. Share the sheet with the service account email (from the JSON file, `client_email` field)  
   — give it **Editor** access

The app will auto-create the `habits` and `completions` tabs on first run.

---

## Step 2 — Local Setup (VS Code)

### Install dependencies
```bash
# Open terminal in VS Code (Ctrl + `)
python -m venv venv

# Activate:
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### Add your secrets
Edit `.streamlit/secrets.toml` — fill in your values from the JSON key file:

```toml
SPREADSHEET_NAME = "HabitTracker"

[gcp_service_account]
type                        = "service_account"
project_id                  = "your-project-id"
private_key_id              = "abc123"
private_key                 = "-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----\n"
client_email                = "habit-tracker@your-project.iam.gserviceaccount.com"
client_id                   = "123456789"
auth_uri                    = "https://accounts.google.com/o/oauth2/auth"
token_uri                   = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url        = "https://www.googleapis.com/robot/v1/metadata/x509/..."
```

### Run the app
```bash
streamlit run app.py
```
Opens at **http://localhost:8501** ✅

---

## Step 3 — Deploy FREE on Streamlit Community Cloud

1. Push this folder to a **GitHub repo** (`.gitignore` keeps secrets out)
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Pick your repo, set `app.py` as the main file
4. Click **Advanced settings → Secrets** and paste your full `secrets.toml` contents
5. Click **Deploy** → live at `yourname.streamlit.app` in ~60 seconds 🚀

---

## Adding New Features (Scalability)

| Feature | Where to add |
|---|---|
| New stat / metric | `modules/stats.py` (pure function) + `modules/dashboard.py` (render) |
| New UI section | New file `modules/your_section.py`, import in `app.py` |
| Change data backend | Only touch `modules/data.py` |
| Style change | Only touch `static/style.css` |
| New config value | `config/settings.py` |
