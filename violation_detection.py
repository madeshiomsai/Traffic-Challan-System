"""
Core logic for the Traffic Challan System:

- detect_violation()     -> reads the violation type from an image
- detect_number_plate()  -> reads the vehicle registration number
- get_fine()             -> looks up the fine amount for a violation
- get_user()             -> looks up the registered owner by plate
- log_challan()          -> records an issued challan in Chalan.db
- get_challan_history()  -> returns previously issued challans
- mark_notified()        -> flags a challan as sent to the owner
"""

import sqlite3

from groq import Groq

from config import GROQ_API_KEY, VISION_MODEL, CHALAN_DB, USER_DB

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is not set. Set it as an environment variable "
        "or in a .env file before running the app (see config.py)."
    )

client = Groq(api_key=GROQ_API_KEY)


# =========================================================
# HELPERS
# =========================================================

def _image_to_base64(image_path):
    import base64
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _strip_think_tags(text):
    if "<think>" in text:
        if "</think>" in text:
            text = text.split("</think>")[-1]
        else:
            text = text.split("<think>")[-1]
    return text.strip()


def normalize_plate(plate):
    if not plate:
        return ""
    return "".join(ch for ch in str(plate).upper() if ch.isalnum())


# =========================================================
# DETECT TRAFFIC VIOLATION
# =========================================================

ALLOWED_VIOLATIONS = ["Triple Ride", "No Parking", "No Helmet", "Overspeed"]


def detect_violation(image_path):
    image_base64 = _image_to_base64(image_path)

    response = client.chat.completions.create(
        model=VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Analyze this traffic image.
Identify ONLY ONE violation.

Allowed violations:
1. Triple Ride
2. No Parking
3. No Helmet
4. Overspeed

Return ONLY one of these exact names:
Triple Ride
No Parking
No Helmet
Overspeed

Do not provide reasoning, explanation, markdown, <think> tags, or any additional text.""",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                    },
                ],
            }
        ],
    )

    result = _strip_think_tags(response.choices[0].message.content.strip())
    result_lower = result.lower()

    for name in ALLOWED_VIOLATIONS:
        if name.lower() in result_lower:
            return name

    # Handle slight model variations (e.g. "triple riding")
    for keyword, name in [
        ("triple", "Triple Ride"),
        ("parking", "No Parking"),
        ("helmet", "No Helmet"),
        ("overspeed", "Overspeed"),
        ("speed", "Overspeed"),
    ]:
        if keyword in result_lower:
            return name

    return result


# =========================================================
# DETECT NUMBER PLATE
# =========================================================

def detect_number_plate(image_path):
    image_base64 = _image_to_base64(image_path)

    response = client.chat.completions.create(
        model=VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Read the vehicle registration number plate from this image.

Return ONLY the registration number.

VERY IMPORTANT:
- Do NOT provide reasoning, <think> tags, explanations, or markdown.
- Do NOT write "Number Plate:" or "Registration:".
- Return only letters and numbers.

Examples:
TS10ED8176
TS09PA3330
MH43BA2518
TS10EX2850""",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                    },
                ],
            }
        ],
    )

    result = _strip_think_tags(response.choices[0].message.content.strip())

    for label in ["Number Plate:", "NUMBER PLATE:", "number plate:",
                  "Registration:", "REGISTRATION:", "registration:",
                  "<think>", "</think>", "`", "*", "#"]:
        result = result.replace(label, "")

    # Take the last non-empty line in case the model added a lead-in sentence
    lines = [line.strip() for line in result.splitlines() if line.strip()]
    if lines:
        result = lines[-1]

    return "".join(ch for ch in result.upper() if ch.isalnum())


# =========================================================
# GET FINE
# =========================================================

def get_fine(violation):
    conn = sqlite3.connect(CHALAN_DB)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT fine FROM violations WHERE LOWER(violation_name) = LOWER(?)",
        (violation,),
    )
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 0


# =========================================================
# GET USER (owner lookup by plate) -- no photo field
# =========================================================

def get_user(number_plate):
    conn = sqlite3.connect(USER_DB)
    cursor = conn.cursor()

    detected_plate = normalize_plate(number_plate)

    cursor.execute("""
        SELECT name, vehicle_reg, vehicle_type, vehnum, mobile
        FROM users
    """)
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        if normalize_plate(row[1]) == detected_plate:
            return {
                "name": row[0],
                "vehicle_reg": row[1],
                "vehicle_type": row[2],
                "vehnum": row[3],
                "mobile": row[4],
            }

    return None


# =========================================================
# CHALLAN HISTORY
# =========================================================

def log_challan(violation, fine, vehicle_reg, user=None):
    """Insert an issued challan into the history table. Returns the new row id."""
    conn = sqlite3.connect(CHALAN_DB)
    cursor = conn.cursor()

    driver_name = user["name"] if user else None
    vehicle_type = user["vehicle_type"] if user else None
    mobile = user["mobile"] if user else None

    cursor.execute("""
        INSERT INTO challans (driver_name, vehicle_reg, vehicle_type, violation, fine, mobile)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (driver_name, vehicle_reg, vehicle_type, violation, fine, mobile))

    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def mark_notified(challan_id):
    conn = sqlite3.connect(CHALAN_DB)
    cursor = conn.cursor()
    cursor.execute("UPDATE challans SET notified = 1 WHERE id = ?", (challan_id,))
    conn.commit()
    conn.close()


def get_challan_history(limit=200):
    conn = sqlite3.connect(CHALAN_DB)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, driver_name, vehicle_reg, vehicle_type, violation, fine,
               mobile, challan_date, notified
        FROM challans
        ORDER BY challan_date DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows
