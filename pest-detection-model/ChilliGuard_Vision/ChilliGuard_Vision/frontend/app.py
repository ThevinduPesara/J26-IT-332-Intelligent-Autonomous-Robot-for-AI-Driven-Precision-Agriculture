from io import BytesIO
import os

import pandas as pd
import requests
import streamlit as st
from PIL import Image


st.set_page_config(
    page_title="ChilliGuard Vision",
    page_icon="🌶️",
    layout="wide",
    initial_sidebar_state="expanded",
)

BACKEND_URL = os.getenv("PEST_BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")

HERO_IMAGE = (
    "https://thumb.wikimedia.org/wikipedia/commons/thumb/c/cc/"
    "Paprika_mit_Blattlaus_Befall-2-Josef_Schlaghecken.jpg/"
    "1280px-Paprika_mit_Blattlaus_Befall-2-Josef_Schlaghecken.jpg"
)

CLASS_DETAILS = {
    "MP": ("Aphid", "Small sap-feeding pests that may appear in groups on leaves and stems."),
    "BT": ("Whitefly", "Small white sap-feeding insects commonly found on the underside of leaves."),
    "T": ("Thrips", "Very small elongated insects that can be difficult to see in field images."),
    "C": ("Caterpillar", "Leaf-feeding larvae that are generally larger than the other target pests."),
}


def html(content: str) -> None:
    st.html(content.strip())


st.html(
    f"""
    <style>
    #MainMenu, footer, [data-testid="stHeader"], [data-testid="stToolbar"] {{
        display: none !important;
    }}

    html, body, [class*="css"] {{
        font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}

    .stApp {{
        background:
            radial-gradient(circle at 6% 0%, rgba(75, 255, 145, 0.07), transparent 28%),
            radial-gradient(circle at 96% 8%, rgba(255, 99, 71, 0.05), transparent 25%),
            #06100b;
        color: #f6fff8;
    }}

    .block-container {{
        max-width: 1460px;
        padding: 1.5rem 2.5rem 4rem 2.5rem;
    }}

    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #071b12 0%, #06130d 55%, #050d09 100%);
        border-right: 1px solid rgba(255,255,255,0.07);
    }}

    .brand {{ padding: 8px 2px 18px; }}
    .brand-name {{ color: #fff; font-size: 1.55rem; font-weight: 820; letter-spacing: -0.035em; }}
    .brand-copy {{ color: #8ea197; font-size: .86rem; line-height: 1.55; margin-top: 6px; }}

    .status {{
        border: 1px solid rgba(255,255,255,0.075);
        border-radius: 15px;
        background: rgba(255,255,255,0.032);
        padding: 14px 15px;
        margin: 2px 0 18px;
    }}
    .online {{ color: #59ff9f; font-weight: 780; }}
    .offline {{ color: #ff7d7d; font-weight: 780; }}
    .status-note {{ color: #7f9388; font-size: .78rem; margin-top: 5px; }}

    .hero {{
        min-height: 420px;
        border-radius: 30px;
        overflow: hidden;
        padding: 54px 56px;
        margin-bottom: 24px;
        border: 1px solid rgba(255,255,255,0.09);
        box-shadow: 0 30px 85px rgba(0,0,0,0.30);
        background:
            linear-gradient(90deg, rgba(2,15,9,.98) 0%, rgba(3,18,11,.92) 40%, rgba(3,18,11,.55) 67%, rgba(3,18,11,.24) 100%),
            url('{HERO_IMAGE}');
        background-size: cover;
        background-position: center 48%;
    }}

    .hero-badge {{
        display: inline-block;
        padding: 8px 14px;
        border-radius: 999px;
        border: 1px solid rgba(82,255,151,.28);
        background: rgba(82,255,151,.10);
        color: #61ffa5;
        font-size: .72rem;
        font-weight: 820;
        letter-spacing: .10em;
        text-transform: uppercase;
    }}

    .hero-title {{
        color: #fff;
        max-width: 770px;
        margin-top: 25px;
        font-size: clamp(3rem, 5vw, 5.2rem);
        font-weight: 850;
        line-height: .98;
        letter-spacing: -0.055em;
    }}

    .hero-copy {{
        max-width: 710px;
        color: rgba(255,255,255,.74);
        font-size: 1.02rem;
        line-height: 1.75;
        margin: 22px 0 24px;
    }}

    .chips {{ display: flex; flex-wrap: wrap; gap: 10px; }}
    .chip {{
        border: 1px solid rgba(255,255,255,.08);
        background: rgba(255,255,255,.055);
        color: rgba(255,255,255,.84);
        border-radius: 11px;
        padding: 9px 13px;
        font-size: .80rem;
        font-weight: 620;
    }}

    .cards {{
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 14px;
        margin: 4px 0 30px;
    }}

    .pest-card {{
        min-height: 158px;
        border: 1px solid rgba(255,255,255,.075);
        border-radius: 20px;
        background: linear-gradient(145deg, rgba(255,255,255,.052), rgba(255,255,255,.02));
        padding: 21px;
        box-shadow: 0 15px 45px rgba(0,0,0,.11);
    }}

    .pest-code {{ color: #5dffa1; font-size: .76rem; font-weight: 800; letter-spacing: .08em; }}
    .pest-name {{ color: #fff; font-size: 1.06rem; font-weight: 780; margin: 8px 0 7px; }}
    .pest-copy {{ color: #8fa197; font-size: .82rem; line-height: 1.55; }}

    .section-kicker {{ color: #57ff9d; font-size: .72rem; font-weight: 820; letter-spacing: .11em; text-transform: uppercase; margin-bottom: 7px; }}
    .section-title {{ color: #fff; font-size: 2rem; font-weight: 820; letter-spacing: -.035em; margin-bottom: 7px; }}
    .section-copy {{ color: #8ea197; font-size: .94rem; line-height: 1.6; margin-bottom: 22px; }}

    .result-card {{
        border: 1px solid rgba(78,255,150,.20);
        border-radius: 23px;
        background: linear-gradient(135deg, rgba(48,255,136,.12), rgba(255,255,255,.025));
        padding: 27px;
        margin: 8px 0 20px;
    }}
    .result-label {{ color: #8ca096; font-size: .71rem; font-weight: 820; letter-spacing: .11em; text-transform: uppercase; }}
    .result-main {{ color: #fff; font-size: 2.3rem; font-weight: 840; letter-spacing: -.04em; margin-top: 6px; }}
    .result-copy {{ color: rgba(255,255,255,.68); font-size: .92rem; line-height: 1.6; margin-top: 10px; }}

    .note-card {{
        border: 1px solid rgba(255,255,255,.07);
        border-radius: 16px;
        background: rgba(255,255,255,.03);
        padding: 16px;
        margin-top: 12px;
    }}
    .note-title {{ color: #fff; font-size: .90rem; font-weight: 760; margin-bottom: 6px; }}
    .note-copy {{ color: #8b9e94; font-size: .80rem; line-height: 1.58; }}

    div[data-testid="stFileUploader"], div[data-testid="stCameraInput"] {{
        border: 1px dashed rgba(83,255,153,.28);
        border-radius: 19px;
        background: rgba(255,255,255,.017);
        padding: 10px;
    }}

    div[data-testid="stMetric"] {{
        border: 1px solid rgba(255,255,255,.07);
        border-radius: 16px;
        background: rgba(255,255,255,.032);
        padding: 16px;
    }}

    .stButton > button {{ min-height: 46px; border-radius: 12px; font-weight: 720; }}

    @media (max-width: 1000px) {{
        .cards {{ grid-template-columns: repeat(2, minmax(0,1fr)); }}
        .hero {{ padding: 38px; }}
    }}

    @media (max-width: 650px) {{
        .block-container {{ padding-left: 1rem; padding-right: 1rem; }}
        .cards {{ grid-template-columns: 1fr; }}
        .hero {{ padding: 27px; min-height: 360px; }}
    }}
    </style>
    """
)


@st.cache_data(ttl=3, show_spinner=False)
def backend_health():
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=2.5)
        response.raise_for_status()
        return True, response.json()
    except requests.RequestException:
        return False, {}


@st.cache_data(ttl=8, show_spinner=False)
def get_model_info():
    try:
        response = requests.get(f"{BACKEND_URL}/model", timeout=4)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return {}


def backend_asset(path: str) -> str:
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return f"{BACKEND_URL}{path}"


def predict_image(image_file, confidence: float):
    image_file.seek(0)
    response = requests.post(
        f"{BACKEND_URL}/predict/image",
        files={
            "file": (
                getattr(image_file, "name", "capture.jpg"),
                image_file.getvalue(),
                getattr(image_file, "type", "image/jpeg"),
            )
        },
        params={"confidence": confidence},
        timeout=120,
    )
    response.raise_for_status()
    return response.json()


def render_result(data: dict):
    primary = data.get("primary_detection")
    count = int(data.get("number_of_detections", 0))

    if primary:
        title = primary["display_name"]
        code = primary["class_name"]
        score = float(primary["confidence"])
        result_copy = (
            f"Highest-confidence detection: {title} ({code}) at {score * 100:.1f}%. "
            "All detected pests are listed below with image-space target centres."
        )
    else:
        title = "No pest detected"
        score = 0.0
        result_copy = (
            "No target pest was detected above the selected confidence threshold. "
            "Try a closer image if the pest is small or partly hidden."
        )

    html(
        f"""
        <div class="result-card">
            <div class="result-label">Detection result</div>
            <div class="result-main">{title}</div>
            <div class="result-copy">{result_copy}</div>
        </div>
        """
    )

    metric1, metric2, metric3 = st.columns(3)
    metric1.metric("Detections", count)
    metric2.metric("Top confidence", f"{score * 100:.1f}%" if primary else "—")

    found_classes = sum(
        1
        for item in data.get("class_summary", {}).values()
        if int(item.get("detections", 0)) > 0
    )
    metric3.metric("Pest classes found", found_classes)

    st.subheader("Detection view")
    left, right = st.columns(2)
    with left:
        st.caption("Original image")
        st.image(backend_asset(data["original_image_url"]), width="stretch")
    with right:
        st.caption("Detected pests")
        st.image(backend_asset(data["annotated_image_url"]), width="stretch")

    summary_rows = []
    for code, (display_name, _) in CLASS_DETAILS.items():
        item = data.get("class_summary", {}).get(code, {})
        summary_rows.append(
            {
                "Class": code,
                "Pest": display_name,
                "Detections": int(item.get("detections", 0)),
                "Average confidence": float(item.get("average_confidence", 0.0)),
                "Highest confidence": float(item.get("highest_confidence", 0.0)),
            }
        )

    summary = pd.DataFrame(summary_rows)
    st.subheader("Class summary")
    st.bar_chart(summary.set_index("Pest")[["Detections"]], height=260)

    display_summary = summary.copy()
    display_summary["Average confidence"] = display_summary["Average confidence"].map(lambda value: f"{value * 100:.1f}%")
    display_summary["Highest confidence"] = display_summary["Highest confidence"].map(lambda value: f"{value * 100:.1f}%")
    st.dataframe(display_summary, width="stretch", hide_index=True)

    detections = data.get("detections", [])
    if detections:
        st.subheader("Spray target coordinates")
        target_rows = []

        for index, detection in enumerate(detections, start=1):
            center = detection["target_center"]
            box = detection["bounding_box"]
            target_rows.append(
                {
                    "#": index,
                    "Class": detection["class_name"],
                    "Pest": detection["display_name"],
                    "Confidence": f"{detection['confidence'] * 100:.1f}%",
                    "Target X (px)": center["x"],
                    "Target Y (px)": center["y"],
                    "Target X (%)": f"{center['x_normalized'] * 100:.1f}",
                    "Target Y (%)": f"{center['y_normalized'] * 100:.1f}",
                    "Box": f"({box['x1']}, {box['y1']}) - ({box['x2']}, {box['y2']})",
                }
            )

        st.dataframe(pd.DataFrame(target_rows), width="stretch", hide_index=True)
        st.caption(
            "Target centres are image coordinates. A real spraying mechanism still needs camera-to-nozzle calibration before these values can control physical motion."
        )


with st.sidebar:
    html(
        """
        <div class="brand">
            <div class="brand-name">🌶️ ChilliGuard Vision</div>
            <div class="brand-copy">Pest detection and image-space spray targeting for chilli plants.</div>
        </div>
        """
    )

    online, health = backend_health()
    if online:
        html(
            f"""
            <div class="status">
                <div class="online">● Detection engine online</div>
                <div class="status-note">{health.get('device', 'Model connected')}</div>
            </div>
            """
        )
    else:
        html(
            """
            <div class="status">
                <div class="offline">● Detection engine offline</div>
                <div class="status-note">Start the FastAPI backend on port 8000.</div>
            </div>
            """
        )

    st.subheader("Detection settings")
    confidence = st.slider(
        "Confidence threshold",
        min_value=0.10,
        max_value=0.90,
        value=0.25,
        step=0.05,
        help="Raise this value to keep only stronger detections.",
    )

    st.divider()
    st.subheader("Model")
    model_info = get_model_info() if online else {}

    if model_info:
        st.markdown("**YOLOv8n pest detector**")
        st.caption("Fine-tuned on four chilli pest classes")

        c1, c2 = st.columns(2)
        c1.metric("Input", f"{model_info.get('image_size', 640)} px")
        c2.metric("Device", "GPU" if str(model_info.get("device")) == "0" else "CPU")

        metrics = model_info.get("validation_metrics", {})
        if metrics:
            st.caption("Recorded validation results")
            st.write(f"mAP@0.50: **{metrics.get('mAP50', 0) * 100:.1f}%**")
            st.write(f"Precision: **{metrics.get('precision', 0) * 100:.1f}%**")
            st.write(f"Recall: **{metrics.get('recall', 0) * 100:.1f}%**")
    else:
        st.caption("Model information is unavailable.")

    st.divider()
    st.subheader("Classes")
    st.markdown(
        """
**MP — Aphid**  
**BT — Whitefly**  
**T — Thrips**  
**C — Caterpillar**
        """
    )


html(
    """
    <div class="hero">
        <div class="hero-badge">Computer vision pest detection</div>
        <div class="hero-title">Chilli Pest<br>Detection & Targeting</div>
        <div class="hero-copy">
            Detect target pests on chilli plant images, review confidence scores and bounding boxes,
            and extract image-space target centres that can later be mapped to a precision spraying mechanism.
        </div>
        <div class="chips">
            <div class="chip">YOLOv8n</div>
            <div class="chip">4 pest classes</div>
            <div class="chip">GPU inference</div>
            <div class="chip">Camera input</div>
            <div class="chip">Spray target centres</div>
        </div>
    </div>
    """
)

html(
    """
    <div class="cards">
        <div class="pest-card">
            <div class="pest-code">MP</div>
            <div class="pest-name">Aphid</div>
            <div class="pest-copy">Small sap-feeding pests that may occur in clusters on chilli leaves and stems.</div>
        </div>
        <div class="pest-card">
            <div class="pest-code">BT</div>
            <div class="pest-name">Whitefly</div>
            <div class="pest-copy">Small white insects commonly found on the underside of leaves.</div>
        </div>
        <div class="pest-card">
            <div class="pest-code">T</div>
            <div class="pest-name">Thrips</div>
            <div class="pest-copy">Very small elongated pests that can be difficult to detect at long camera distances.</div>
        </div>
        <div class="pest-card">
            <div class="pest-code">C</div>
            <div class="pest-name">Caterpillar</div>
            <div class="pest-copy">Leaf-feeding larvae with a larger visual target than the other supported classes.</div>
        </div>
    </div>
    """
)

upload_tab, camera_tab, live_tab, system_tab = st.tabs(
    ["📤 Upload image", "📸 Camera capture", "🎥 Live camera", "ℹ️ System"]
)

with upload_tab:
    html(
        """
        <div class="section-kicker">Image analysis</div>
        <div class="section-title">Upload a chilli plant image</div>
        <div class="section-copy">Use a clear image where the target pest is visible. Close-range images are especially important for small pests such as thrips and whiteflies.</div>
        """
    )

    uploaded = st.file_uploader("Choose JPG, JPEG or PNG", type=["jpg", "jpeg", "png"])

    if uploaded is not None:
        preview = Image.open(BytesIO(uploaded.getvalue())).convert("RGB")
        image_col, info_col = st.columns([1.45, 0.55])

        with image_col:
            st.image(preview, caption="Selected image", width="stretch")

        with info_col:
            st.subheader("Image details")
            st.write(f"**File:** {uploaded.name}")
            st.write(f"**Resolution:** {preview.width} × {preview.height}")
            st.write(f"**Threshold:** {confidence:.2f}")
            html(
                """
                <div class="note-card">
                    <div class="note-title">For a cleaner result</div>
                    <div class="note-copy">Keep the leaf and pest in focus. Avoid heavy motion blur, extreme distance and strong glare.</div>
                </div>
                """
            )
            run_upload = st.button("Analyze image", type="primary", width="stretch")

        if run_upload:
            if not online:
                st.error("FastAPI backend is offline.")
            else:
                with st.spinner("Running pest detection..."):
                    try:
                        st.session_state["upload_result"] = predict_image(uploaded, confidence)
                    except requests.RequestException as error:
                        st.error(f"Prediction failed: {error}")

    if "upload_result" in st.session_state:
        st.divider()
        render_result(st.session_state["upload_result"])

with camera_tab:
    html(
        """
        <div class="section-kicker">Camera capture</div>
        <div class="section-title">Take a field image</div>
        <div class="section-copy">Capture a single frame with the browser camera and send it to the detector.</div>
        """
    )

    capture = st.camera_input("Capture chilli plant image")
    if capture is not None:
        if st.button("Analyze captured image", type="primary", width="stretch"):
            if not online:
                st.error("FastAPI backend is offline.")
            else:
                with st.spinner("Analyzing camera frame..."):
                    try:
                        st.session_state["camera_result"] = predict_image(capture, confidence)
                    except requests.RequestException as error:
                        st.error(f"Prediction failed: {error}")

    if "camera_result" in st.session_state:
        st.divider()
        render_result(st.session_state["camera_result"])

with live_tab:
    html(
        """
        <div class="section-kicker">Live detection</div>
        <div class="section-title">Local webcam stream</div>
        <div class="section-copy">This mode uses the webcam connected to the computer running the FastAPI backend.</div>
        """
    )

    if online:
        stream_url = f"{BACKEND_URL}/camera/stream?confidence={confidence}"
        html(
            f"""
            <div style="overflow:hidden;border-radius:22px;border:1px solid rgba(255,255,255,.09);background:#020706;max-width:1100px;margin:auto;box-shadow:0 25px 70px rgba(0,0,0,.24);">
                <img src="{stream_url}" style="width:100%;height:auto;display:block;" alt="Live pest detection">
            </div>
            """
        )
        st.info("If the camera does not appear, close other applications that may be using the webcam.")
    else:
        st.error("FastAPI backend is offline.")

with system_tab:
    html(
        """
        <div class="section-kicker">System overview</div>
        <div class="section-title">Detection pipeline</div>
        <div class="section-copy">A compact computer-vision workflow designed for pest localization and later integration with targeted spraying.</div>
        """
    )

    left, right = st.columns([1.05, 0.95])
    with left:
        st.markdown(
            """
### Processing flow

1. A chilli plant image is captured or uploaded.  
2. The FastAPI service sends the image to the trained YOLOv8n model.  
3. The model returns pest class, confidence and bounding-box coordinates.  
4. The application calculates the centre of each detected box.  
5. Those image-space centres can later be converted into physical spray positions after camera/nozzle calibration.

### Supported classes

- **MP** — Aphid
- **BT** — Whitefly
- **T** — Thrips
- **C** — Caterpillar

### Deployment note

The detector provides image coordinates only. Real-world spraying requires geometric calibration, actuator limits and a safety layer before any nozzle command is issued.
            """
        )

    with right:
        st.image(HERO_IMAGE, caption="Capsicum leaf with aphid infestation", width="stretch")
        html(
            """
            <div class="note-card">
                <div class="note-title">Model scope</div>
                <div class="note-copy">The interface only reports the four classes learned by the trained model. A confidence score is not a guarantee that every field detection is correct.</div>
            </div>
            """
        )

    st.divider()
    st.subheader("Technical platform")
    t1, t2, t3, t4 = st.columns(4)
    t1.metric("Detector", "YOLOv8n")
    t2.metric("Backend", "FastAPI")
    t3.metric("Frontend", "Streamlit")
    t4.metric("Input", "640 px")

    st.caption(
        "Hero/reference image: Wikimedia Commons, 'Paprika mit Blattlaus Befall-2-Josef Schlaghecken.jpg', Schlaghecken Josef, CC BY 4.0."
    )
