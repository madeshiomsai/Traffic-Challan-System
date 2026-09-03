# Traffic Challan System

AI-based traffic violation detection, fine lookup, owner lookup, and WhatsApp
challan notification — built with Streamlit + Groq vision models + SQLite.

## What changed from the original version
- **No driver photos anywhere** — owner lookup returns and displays only text
  details (name, vehicle registration, vehicle type, vehicle ID, mobile).
- **Challan history is now logged** to a `challans` table in `Chalan.db` every
  time a challan is generated (your original database already had this table
  defined but nothing was writing to it).
- **New pages**: a "Challan History" page (search/filter past challans,
  re-send WhatsApp notifications) and a cleaned-up "Registered Users" page.
- **API key moved out of source code** into an environment variable (see
  Setup below) instead of being hardcoded in the `.py` files.

## Project structure
```
traffic_challan_system/
├── app.py                        # Main Streamlit app (upload + detect + notify)
├── pages/
│   ├── 1_Challan_History.py      # Browse & re-send past challans
│   └── 2_User_Database.py        # Registered owners (text only)
├── violation_detection.py        # Detection, DB lookups, challan logging
├── database_setup.py             # (Re)creates Chalan.db tables
├── config.py                     # API key + DB path configuration
├── Chalan.db                     # Violations + fines + challan history
├── user.db                       # Registered vehicle owners
├── images/                       # Sample test images
└── requirements.txt
```

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set your Groq API key as an environment variable (get one at
   https://console.groq.com/keys — **generate a new one**, since the keys
   that were hardcoded in the original files were already exposed in plain
   text and should be treated as compromised):

   ```
   # macOS / Linux
   export GROQ_API_KEY="your_key_here"

   # Windows PowerShell
   $env:GROQ_API_KEY = "your_key_here"
   ```

   Or create a `.env` file in this folder:
   ```
   GROQ_API_KEY=your_key_here
   ```

3. (Optional) rebuild the database tables:
   ```
   python database_setup.py
   ```

4. Run the app:
   ```
   streamlit run app.py
   ```

## Notes
- WhatsApp sending uses `wa.me` links (opens WhatsApp Web/App with the
  message pre-filled) — there's no paid WhatsApp Business API involved.
- The default country code for mobile numbers is `91` (India); change
  `DEFAULT_COUNTRY_CODE` in `config.py` if needed.
