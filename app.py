import os
import time
import urllib.parse

import streamlit as st

from violation_detection import (
    detect_violation,
    detect_number_plate,
    get_fine,
    get_user,
    log_challan,
    mark_notified,
)
from config import DEFAULT_COUNTRY_CODE

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Traffic Challan System",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# VIOLATION -> COLOR / ICON MAP
# =========================================================

VIOLATION_STYLE = {
    "Triple Ride":  {"icon": "🏍️", "color": "#a78bfa", "bg": "#2e1065"},
    "No Parking":   {"icon": "🚫", "color": "#60a5fa", "bg": "#1e3a5f"},
    "No Helmet":    {"icon": "🪖", "color": "#fbbf24", "bg": "#78350f"},
    "Overspeed":    {"icon": "⚡", "color": "#f87171", "bg": "#7f1d1d"},
}
DEFAULT_STYLE = {"icon": "⚠️", "color": "#e5e7eb", "bg": "#374151"}


def violation_style(name):
    return VIOLATION_STYLE.get(name, DEFAULT_STYLE)


# =========================================================
# GLOBAL STYLE
# =========================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=JetBrains+Mono:wght@500&display=swap');

html, body, [class*="css"] { font-family: 'Manrope', sans-serif; }
code, .stCode, pre { font-family: 'JetBrains Mono', monospace !important; }

.block-container { padding-top: 1.2rem; padding-bottom: 3rem; max-width: 1200px; }

/* ---------- Hero header ---------- */
.app-header {
    position: relative;
    overflow: hidden;
    background:
        radial-gradient(circle at 15% 20%, rgba(239,68,68,0.25), transparent 45%),
        radial-gradient(circle at 85% 80%, rgba(59,130,246,0.22), transparent 45%),
        linear-gradient(135deg, #111827 0%, #0b0f19 100%);
    padding: 34px 36px;
    border-radius: 20px;
    margin-bottom: 26px;
    border: 1px solid #262f42;
}
.app-title {
    font-size: 36px;
    font-weight: 800;
    color: #ffffff;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 14px;
    letter-spacing: -0.5px;
}
.app-subtitle { font-size: 15px; color: #9ca3af; margin-top: 8px; max-width: 640px; line-height: 1.5; }
.app-header-badges { margin-top: 16px; display: flex; gap: 8px; flex-wrap: wrap; }
.mini-badge {
    font-size: 11px; font-weight: 700; letter-spacing: 0.4px; text-transform: uppercase;
    color: #cbd5e1; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12);
    padding: 5px 10px; border-radius: 999px;
}

/* ---------- Status pill ---------- */
.status-pill {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 6px 16px; border-radius: 999px;
    font-size: 12px; font-weight: 800; letter-spacing: 0.6px; text-transform: uppercase;
}
.pill-success { background: #064e3b; color: #6ee7b7; border: 1px solid #0d6b52; }
.pill-warning { background: #78350f; color: #fcd34d; border: 1px solid #8a4110; }

/* ---------- Cards ---------- */
.info-card {
    background: #131a29;
    border: 1px solid #263042;
    border-radius: 16px;
    padding: 20px 22px;
    height: 100%;
    transition: border-color 0.15s ease, transform 0.15s ease;
}
.info-card:hover { border-color: #3b4a63; transform: translateY(-2px); }

.info-card-label {
    font-size: 12px; color: #8b95a7; text-transform: uppercase;
    letter-spacing: 0.6px; margin-bottom: 8px; font-weight: 700;
}
.info-card-value { font-size: 27px; font-weight: 800; color: #ffffff; display: flex; align-items: center; gap: 8px; }

.violation-card {
    border-radius: 16px;
    padding: 20px 22px;
    border: 1px solid;
}
.violation-icon-badge {
    display: inline-flex; align-items: center; justify-content: center;
    width: 44px; height: 44px; border-radius: 12px; font-size: 22px; margin-bottom: 10px;
}

.detail-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 12px 4px; border-bottom: 1px solid #263042; font-size: 15px;
}
.detail-row:last-child { border-bottom: none; }
.detail-row span:first-child { color: #8b95a7; font-weight: 600; }
.detail-row span:last-child { color: #f3f4f6; font-weight: 700; }

.owner-name-card {
    display: flex; align-items: center; gap: 14px;
    background: linear-gradient(135deg, #131a29, #0f1520);
    border: 1px solid #263042; border-radius: 16px; padding: 18px 22px; margin-bottom: 16px;
}
.owner-avatar {
    width: 52px; height: 52px; border-radius: 50%;
    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
    display: flex; align-items: center; justify-content: center;
    font-size: 22px; font-weight: 800; color: white; flex-shrink: 0;
}
.owner-name-text { font-size: 20px; font-weight: 800; color: #ffffff; }
.owner-name-sub { font-size: 13px; color: #8b95a7; }

.section-title {
    font-size: 20px; font-weight: 800; margin: 6px 0 16px 0;
    display: flex; align-items: center; gap: 10px; color: #f3f4f6;
}

hr.thin { border: none; border-top: 1px solid #263042; margin: 26px 0; }

/* ---------- Step chips ---------- */
.step-row { display: flex; gap: 10px; margin-bottom: 22px; }
.step-chip {
    flex: 1; text-align: center; padding: 10px 6px; border-radius: 10px;
    font-size: 13px; font-weight: 700; background: #131a29; color: #5b6577;
    border: 1px solid #263042; transition: all 0.2s ease;
}
.step-chip.done { background: #064e3b; color: #6ee7b7; border-color: #0d6b52; }
.step-chip.active { background: #1e3a5f; color: #93c5fd; border-color: #2b4d75; }

/* ---------- Buttons ---------- */
.stButton > button, .stLinkButton > a {
    border-radius: 10px !important;
    font-weight: 700 !important;
    transition: transform 0.12s ease, box-shadow 0.12s ease !important;
}
.stButton > button:hover, .stLinkButton > a:hover {
    transform: translateY(-1px);
}
.stButton > button[kind="primary"], .stLinkButton > a {
    background: linear-gradient(135deg, #ef4444, #dc2626) !important;
    border: none !important;
    box-shadow: 0 4px 14px rgba(239,68,68,0.25) !important;
}

/* ---------- Tabs ---------- */
.stTabs [data-baseweb="tab-list"] { gap: 4px; }
.stTabs [data-baseweb="tab"] {
    border-radius: 10px 10px 0 0; padding: 10px 18px; font-weight: 700; color: #8b95a7;
}
.stTabs [aria-selected="true"] { color: #f3f4f6 !important; }

/* ---------- Uploader ---------- */
[data-testid="stFileUploaderDropzone"] {
    border-radius: 14px !important;
    border: 1.5px dashed #3b4a63 !important;
    background: #0f1520 !important;
}

/* ---------- Code preview ---------- */
.stCodeBlock { border-radius: 12px !important; }

</style>
""", unsafe_allow_html=True)


# =========================================================
# SESSION STATE
# =========================================================

if "result" not in st.session_state:
    st.session_state.result = None
if "logged_challan_id" not in st.session_state:
    st.session_state.logged_challan_id = None


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown("### 🚦 Traffic Challan System")
    st.caption("AI-Based Violation Detection & Challan Generation")
    st.divider()

    st.markdown("**How it works**")
    st.markdown(
        "1. Upload a traffic photo\n"
        "2. Click *Generate Challan*\n"
        "3. Violation, fine & plate are detected\n"
        "4. Owner is looked up automatically\n"
        "5. Send the challan on WhatsApp"
    )
    st.divider()

    if st.session_state.result:
        st.success("Last challan generated ✅")
        if st.button("🔄 Start New Detection", use_container_width=True):
            st.session_state.result = None
            st.session_state.logged_challan_id = None
            st.rerun()
    else:
        st.info("No challan generated yet.")

    st.divider()
    st.page_link("app.py", label="🏠 Generate Challan")
    st.page_link("pages/1_Challan_History.py", label="📋 Challan History")
    st.page_link("pages/2_User_Database.py", label="👥 Registered Users")
    st.divider()
    st.caption("AI + SQL + Streamlit + WhatsApp")


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <div class="app-header">
        <div class="app-title">🚦 Traffic Challan System</div>
        <div class="app-subtitle">
            Upload a traffic photo to automatically detect violations,
            identify the vehicle, and notify the owner — powered by AI vision.
        </div>
        <div class="app-header-badges">
            <span class="mini-badge">🤖 AI Detection</span>
            <span class="mini-badge">🗄️ SQL Lookup</span>
            <span class="mini-badge">📱 WhatsApp Alerts</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# IMAGE UPLOAD
# =========================================================

upload_col, preview_col = st.columns([1.2, 1], gap="large")

with upload_col:
    st.markdown('<div class="section-title">📷 Upload Violation Image</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload a vehicle/traffic image",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed",
    )

    generate = False
    if uploaded_file is not None:
        generate = st.button("🚨  GENERATE CHALLAN", type="primary", use_container_width=True)
    else:
        st.info("👆 Upload an image to begin detection.")

with preview_col:
    st.markdown('<div class="section-title">🖼️ Preview</div>', unsafe_allow_html=True)
    if uploaded_file is not None:
        st.image(uploaded_file, use_container_width=True, caption="Uploaded Violation Image")
    else:
        st.markdown(
            '<div class="info-card" style="text-align:center; color:#5b6577; '
            'display:flex; align-items:center; justify-content:center; min-height:160px;">'
            'No image uploaded yet</div>',
            unsafe_allow_html=True,
        )


# =========================================================
# MAIN PROCESSING
# =========================================================

if uploaded_file is not None and generate:

    os.makedirs("temp", exist_ok=True)
    image_path = os.path.join("temp", uploaded_file.name)
    with open(image_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    steps = ["Violation", "Fine", "Number Plate", "Owner", "Log"]
    step_placeholder = st.empty()

    def render_steps(active_index, done_upto=-1):
        chips = ""
        for i, s in enumerate(steps):
            cls = "done" if i <= done_upto else ("active" if i == active_index else "")
            chips += f'<div class="step-chip {cls}">{s}</div>'
        step_placeholder.markdown(f'<div class="step-row">{chips}</div>', unsafe_allow_html=True)

    render_steps(0)
    progress = st.progress(0, text="Detecting traffic violation...")
    try:
        violation = detect_violation(image_path)
    except Exception as e:
        st.error(f"Violation detection error: {e}")
        st.stop()

    if not violation:
        progress.empty()
        st.error("Could not detect a traffic violation.")
        st.stop()

    render_steps(1, done_upto=0)
    progress.progress(30, text="Checking challan fine...")
    try:
        fine = get_fine(violation)
    except Exception as e:
        st.error(f"Fine database error: {e}")
        st.stop()

    render_steps(2, done_upto=1)
    progress.progress(55, text="Detecting vehicle number plate...")
    try:
        number_plate = detect_number_plate(image_path)
    except Exception as e:
        st.error(f"Number plate detection error: {e}")
        st.stop()

    if not number_plate:
        st.warning("Number plate could not be detected.")
        number_plate = "Not Detected"

    render_steps(3, done_upto=2)
    progress.progress(75, text="Searching registered vehicle owner...")
    try:
        user = get_user(number_plate)
    except Exception as e:
        st.error(f"User database error: {e}")
        st.stop()

    render_steps(4, done_upto=3)
    progress.progress(92, text="Logging challan...")
    try:
        challan_id = log_challan(violation, fine, number_plate, user)
    except Exception as e:
        challan_id = None
        st.warning(f"Could not log challan to history: {e}")

    render_steps(4, done_upto=4)
    progress.progress(100, text="Done!")
    time.sleep(0.3)
    progress.empty()
    step_placeholder.empty()

    st.session_state.result = {
        "violation": violation,
        "fine": fine,
        "number_plate": number_plate,
        "user": user,
    }
    st.session_state.logged_challan_id = challan_id


# =========================================================
# DISPLAY RESULTS
# =========================================================

result = st.session_state.result

if result:

    violation = result["violation"]
    fine = result["fine"]
    number_plate = result["number_plate"]
    user = result["user"]
    v_style = violation_style(violation)

    st.markdown('<hr class="thin">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🚨 Violation Details</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
            <div class="violation-card" style="background:{v_style['bg']}22; border-color:{v_style['color']}55;">
                <div class="violation-icon-badge" style="background:{v_style['color']}22; color:{v_style['color']};">{v_style['icon']}</div>
                <div class="info-card-label">Violation</div>
                <div class="info-card-value" style="color:{v_style['color']};">{violation}</div>
            </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div class="info-card">
                <div class="info-card-label">Fine Amount</div>
                <div class="info-card-value">💰 ₹{fine}</div>
            </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
            <div class="info-card">
                <div class="info-card-label">Number Plate</div>
                <div class="info-card-value" style="font-family:'JetBrains Mono',monospace; letter-spacing:1px;">🔢 {number_plate}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<hr class="thin">', unsafe_allow_html=True)

    # =====================================================
    # OWNER FOUND
    # =====================================================

    if user:

        name = user["name"]
        vehicle_reg = user["vehicle_reg"]
        vehicle_type = user["vehicle_type"]
        vehnum = user["vehnum"]
        mobile = user["mobile"]
        initials = "".join([p[0].upper() for p in name.split()[:2]]) if name else "?"

        st.markdown('<span class="status-pill pill-success">✅ Owner Found</span>', unsafe_allow_html=True)
        st.write("")

        tab_owner, tab_summary, tab_notify = st.tabs(
            ["👤  Person Details", "📄  Challan Summary", "📱  Notify Owner"]
        )

        # ---------------- TAB: PERSON DETAILS (no photo) ----------------
        with tab_owner:
            st.markdown(f"""
                <div class="owner-name-card">
                    <div class="owner-avatar">{initials}</div>
                    <div>
                        <div class="owner-name-text">{name}</div>
                        <div class="owner-name-sub">Registered Vehicle Owner</div>
                    </div>
                </div>
                <div class="info-card">
                    <div class="detail-row"><span>🚗 Vehicle Registration</span><span>{vehicle_reg}</span></div>
                    <div class="detail-row"><span>🏷️ Vehicle Type</span><span>{vehicle_type}</span></div>
                    <div class="detail-row"><span>🆔 Vehicle ID</span><span>{vehnum}</span></div>
                    <div class="detail-row"><span>📞 Mobile</span><span>{mobile}</span></div>
                    <div class="detail-row"><span>🔢 Detected Number Plate</span><span>{number_plate}</span></div>
                </div>
            """, unsafe_allow_html=True)

        # ---------------- TAB: CHALLAN SUMMARY ----------------
        with tab_summary:
            sc1, sc2 = st.columns(2)
            with sc1:
                st.markdown(f"""
                    <div class="info-card">
                        <div class="detail-row"><span>Owner</span><span>{name}</span></div>
                        <div class="detail-row"><span>Vehicle</span><span>{vehicle_reg}</span></div>
                        <div class="detail-row"><span>Vehicle Type</span><span>{vehicle_type}</span></div>
                    </div>""", unsafe_allow_html=True)
            with sc2:
                st.markdown(f"""
                    <div class="info-card">
                        <div class="detail-row"><span>Violation</span><span>{violation}</span></div>
                        <div class="detail-row"><span>Fine</span><span>₹{fine}</span></div>
                        <div class="detail-row"><span>Mobile</span><span>{mobile}</span></div>
                    </div>""", unsafe_allow_html=True)

        # ---------------- TAB: WHATSAPP NOTIFY ----------------
        with tab_notify:
            phone = "".join(ch for ch in str(mobile) if ch.isdigit())
            if len(phone) == 10:
                whatsapp_number = DEFAULT_COUNTRY_CODE + phone
            else:
                whatsapp_number = phone

            whatsapp_message = f"""TRAFFIC CHALLAN ALERT

Dear {name},

A traffic violation has been detected for your vehicle.

Vehicle Number: {vehicle_reg}
Vehicle Type: {vehicle_type}

Violation: {violation}
Fine Amount: ₹{fine}

Please pay the challan according to the applicable traffic rules.

Thank you.
Traffic Challan System"""

            encoded_message = urllib.parse.quote(whatsapp_message)
            whatsapp_url = f"https://wa.me/{whatsapp_number}?text={encoded_message}"

            st.markdown("**Preview of the message that will be sent:**")
            st.code(whatsapp_message, language=None)

            st.link_button(
                "📱  SEND CHALLAN ON WHATSAPP",
                whatsapp_url,
                use_container_width=True,
                type="primary",
            )
            st.caption("Click the button to open WhatsApp with the challan alert message pre-filled.")

            if st.session_state.logged_challan_id and st.button(
                "✅ Mark as notified", use_container_width=True
            ):
                mark_notified(st.session_state.logged_challan_id)
                st.success("Marked as notified in challan history.")

    # =====================================================
    # OWNER NOT FOUND
    # =====================================================

    else:
        st.markdown('<span class="status-pill pill-warning">⚠️ Owner Not Found</span>', unsafe_allow_html=True)
        st.write("")
        st.markdown(f"""
            <div class="info-card">
                <div class="info-card-label">Detected Number Plate</div>
                <div class="info-card-value" style="font-family:'JetBrains Mono',monospace;">{number_plate}</div>
            </div>""", unsafe_allow_html=True)
        st.info("This vehicle isn't in the registered users database yet, but the violation has still been logged in the challan history.")


# =========================================================
# FOOTER
# =========================================================

st.markdown('<hr class="thin">', unsafe_allow_html=True)
st.caption("Traffic Challan Automation System · AI + SQL + Streamlit + WhatsApp")
