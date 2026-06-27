import streamlit as st
import httpx
import uuid
import time
import json

st.set_page_config(
    page_title="CodeForge AI",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ═══════════════════════════════════════════
   NUCLEAR RESET — kill every Streamlit gap
═══════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="collapsedControl"] { display: none !important; }
section[data-testid="stSidebar"]  { display: none !important; }

html, body { margin: 0 !important; padding: 0 !important; }

.stApp {
    background: #080810 !important;
    font-family: 'Inter', sans-serif;
    min-width: 1100px !important;
    overflow-x: auto !important;
}

/* Kill ALL default Streamlit padding */
.main .block-container {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100vw !important;
    width: 100vw !important;
    min-width: 1100px !important;
}
[data-testid="stAppViewContainer"] {
    padding: 0 !important;
    margin: 0 !important;
    width: 100vw !important;
    min-width: 1100px !important;
}
[data-testid="stAppViewContainer"] > .main {
    padding: 0 !important;
    margin: 0 !important;
}
/* The real fix: Streamlit's main view wraps block-container in its own
   padded element. Kill that padding directly at the source. */
[data-testid="stMain"] {
    padding: 0 !important;
    margin: 0 !important;
}
div[data-testid="stMainBlockContainer"] {
    padding: 0 !important;
    margin: 0 !important;
}
/* This is the main culprit — Streamlit adds gap between column children */
[data-testid="stVerticalBlock"] {
    gap: 0 !important;
    padding: 0 !important;
}
[data-testid="stVerticalBlock"] > div {
    gap: 0 !important;
    padding: 0 !important;
}
/* Kill empty iframe spacers (the iframe itself only — never the parent block) */
iframe[height="0"],
iframe[height="2"],
iframe[height="4"] {
    display: none !important;
    height: 0 !important;
}
/* Column wrapper */
[data-testid="column"] {
    padding: 0 !important;
    gap: 0 !important;
}
/* Only the TOP-LEVEL 3-column layout (direct child of the main block)
   should be forced to a minimum width / no-wrap. Nested column rows,
   like the Clear/New buttons inside the sidebar, must NOT inherit this
   or they overflow their narrow parent and float into the page. */
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-of-type {
    gap: 4px !important;
    padding: 0 !important;
    align-items: stretch !important;
    flex-wrap: nowrap !important;
    min-width: 1400px !important;
}
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-of-type > [data-testid="column"]:nth-of-type(1) {
    background: #0b0b1e !important;
    border-right: 1px solid rgba(99,102,241,0.08) !important;
}
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-of-type > [data-testid="column"]:nth-of-type(3) {
    background: #0b0b1e !important;
    border-left: 1px solid rgba(99,102,241,0.07) !important;
}

/* ═══════════════════════════════════════════
   CHAT MESSAGES
═══════════════════════════════════════════ */
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(99,102,241,0.1) !important;
    border-radius: 7px !important;
    padding: 8px 12px !important;
    margin-bottom: 6px !important;
}
/* Hide the round avatar icon so messages look like console log lines,
   not chat bubbles, matching the rest of the dark dashboard styling. */
[data-testid="stChatMessageAvatarUser"],
[data-testid="stChatMessageAvatarAssistant"],
[data-testid="stChatMessage"] [data-testid="stAvatarIcon-user"],
[data-testid="stChatMessage"] [data-testid="stAvatarIcon-assistant"] {
    display: none !important;
}
[data-testid="stChatMessage"] p  { font-size:12px!important; color:#b0b0d8!important; line-height:1.6!important; }
[data-testid="stChatMessage"] li { font-size:11px!important; color:#9090c0!important; }
[data-testid="stChatMessage"] strong { color:#e2e8f0!important; }
[data-testid="stChatMessage"] code {
    background:rgba(99,102,241,0.15)!important; color:#a5b4fc!important;
    padding:1px 4px!important; border-radius:3px!important;
    font-family:'JetBrains Mono',monospace!important; font-size:10px!important;
}

/* ═══════════════════════════════════════════
   CHAT INPUT
═══════════════════════════════════════════ */
[data-testid="stChatInput"] {
    background: rgba(15,15,35,0.98) !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
    border-radius: 10px !important;
    font-size: 13px !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: rgba(99,102,241,0.55) !important;
    box-shadow: 0 0 0 2px rgba(99,102,241,0.08) !important;
}
[data-testid="stChatInput"] textarea { color:#e2e8f0!important; background:transparent!important; }

/* ═══════════════════════════════════════════
   CODE BLOCKS
═══════════════════════════════════════════ */
[data-testid="stCode"] { border-radius:6px!important; border:1px solid rgba(99,102,241,0.1)!important; overflow:hidden!important; }
[data-testid="stCode"] pre  { background:#04040c!important; }
[data-testid="stCode"] code { font-size:11px!important; line-height:1.5!important; font-family:'JetBrains Mono',monospace!important; }

/* ═══════════════════════════════════════════
   PROGRESS BAR
═══════════════════════════════════════════ */
.stProgress > div > div {
    background: linear-gradient(90deg,#4f46e5,#7c3aed,#a855f7) !important;
    border-radius: 99px !important;
    box-shadow: 0 0 8px rgba(99,102,241,0.5) !important;
}
.stProgress { margin: 4px 0 !important; }

/* ═══════════════════════════════════════════
   BUTTONS
═══════════════════════════════════════════ */
.stButton button {
    border-radius: 7px !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.15s ease !important;
    padding: 4px 10px !important;
    height: 30px !important;
    min-height: 30px !important;
}
[data-testid="stDownloadButton"] button {
    background: rgba(99,102,241,0.07) !important;
    border: 1px solid rgba(99,102,241,0.22) !important;
    color: #818cf8 !important;
    border-radius: 7px !important;
    font-size: 10px !important;
    font-weight: 600 !important;
    height: 28px !important;
}
/* Artifact section toggle buttons (Requirements/Plan/Code/etc.).
   st.container(key=...) genuinely wraps its children in the DOM, unlike
   st.markdown divs. Streamlit exposes the key as a "st-key-<key>" class
   on the wrapper, so we can reliably style just these buttons. */
[class*="st-key-toggle_box_"] button {
    background: rgba(99,102,241,0.04) !important;
    border: 1px solid rgba(99,102,241,0.1) !important;
    border-top: none !important;
    border-radius: 0 0 7px 7px !important;
    color: rgba(140,140,200,0.65) !important;
    font-size: 9px !important;
    font-weight: 600 !important;
    height: 22px !important;
    min-height: 22px !important;
    box-shadow: none !important;
    width: 100% !important;
}
[class*="st-key-toggle_box_"] button:hover {
    background: rgba(99,102,241,0.09) !important;
    color: #a5b4fc !important;
}
[class*="st-key-toggle_box_"] button p {
    font-size: 9px !important;
    color: rgba(140,140,200,0.65) !important;
}

/* Quick Example cards — subtle lift + accent-colored glow on hover */
.example-card {
    background: #0e0e24;
    border: 1px solid rgba(99,102,241,0.09);
    transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
}
.example-card:hover {
    transform: translateY(-2px);
    border-color: var(--accent);
    box-shadow: 0 4px 16px -4px var(--accent), 0 0 0 1px var(--accent);
}

/* System status cards — same lift + glow treatment, accent-colored per card */
.system-card {
    transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
}
.system-card:hover {
    transform: translateY(-2px);
    border-color: var(--accent) !important;
    box-shadow: 0 4px 16px -6px var(--accent);
}

/* Example card buttons */
.exbtn .stButton button {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(99,102,241,0.1) !important;
    border-radius: 6px !important;
    color: rgba(120,120,190,0.9) !important;
    font-size: 11px !important;
    width: 100% !important;
    height: 30px !important;
    min-height: 30px !important;
    transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease !important;
}
.exbtn .stButton button:hover {
    background: rgba(99,102,241,0.1) !important;
    border-color: rgba(99,102,241,0.3) !important;
    color: #a5b4fc !important;
}

/* ═══════════════════════════════════════════
   FILE UPLOADER — dark theme, compact
═══════════════════════════════════════════ */
[data-testid="stFileUploader"] {
    padding: 0 !important;
    margin: 0 0 8px 0 !important;
}
[data-testid="stFileUploader"] section {
    background: #11112a !important;
    border: 1px dashed rgba(99,102,241,0.25) !important;
    border-radius: 8px !important;
    padding: 10px !important;
    min-height: unset !important;
}
[data-testid="stFileUploaderDropzone"] {
    background: #11112a !important;
    padding: 4px !important;
    min-height: unset !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] {
    color: #6868a0 !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] span {
    font-size: 10px !important;
    color: #c0c0e8 !important;
    font-weight: 600 !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] small {
    font-size: 8px !important;
    color: #4a4a78 !important;
}
[data-testid="stFileUploader"] label { font-size: 10px !important; }
[data-testid="stFileUploader"] svg { fill: #6366f1 !important; }
[data-testid="stBaseButton-secondary"] {
    background: rgba(99,102,241,0.1) !important;
    color: #a5b4fc !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
    font-size: 9px !important;
}

/* ═══════════════════════════════════════════
   ALERTS
═══════════════════════════════════════════ */
[data-testid="stAlert"] { border-radius: 7px !important; font-size: 11px !important; padding: 6px 10px !important; margin: 4px 0 !important; }

/* ═══════════════════════════════════════════
   TYPOGRAPHY DEFAULTS
═══════════════════════════════════════════ */
p      { color:#5555aa!important; font-size:12px!important; line-height:1.4!important; margin:0!important; }
li     { color:#5555aa!important; font-size:11px!important; }
strong { color:#e2e8f0!important; }
hr     { border-color:rgba(99,102,241,0.07)!important; margin:6px 0!important; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "messages"      not in st.session_state: st.session_state.messages      = []
if "session_id"    not in st.session_state: st.session_state.session_id    = str(uuid.uuid4())
if "show_sections" not in st.session_state: st.session_state.show_sections = {}
if "active_step"   not in st.session_state: st.session_state.active_step   = 0
if "last_upload"   not in st.session_state: st.session_state.last_upload   = None

# ── Backend health check ──────────────────────────────────────────────────────
try:
    health     = httpx.get("http://localhost:8000/health", timeout=3)
    hdata      = health.json()
    chunks     = hdata.get("rag_chunks", 0)
    backend_ok = True
except Exception:
    chunks     = 0
    backend_ok = False


# ══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════
def format_notebook(text: str, color: str) -> str:
    lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
    boxes, flows, bullets = [], [], []
    for line in lines[:50]:
        clean = line.lstrip("*-•#>123456789.").strip()
        if not clean or len(clean) < 3: continue
        if any(s in clean for s in ["→", "->"]): flows.append(clean)
        elif len(clean) < 55 and clean.endswith(":"): boxes.append(clean.rstrip(":").strip())
        else: bullets.append(clean)
    c    = color
    html = "<div style='padding:0.5rem;font-family:JetBrains Mono,monospace;'>"
    if boxes:
        html += "<div style='display:flex;flex-wrap:wrap;gap:4px;margin-bottom:8px;'>"
        for b in boxes[:6]:
            html += f"<span style='border:1px solid {c}38;border-radius:4px;padding:2px 8px;font-size:9px;color:{c};background:{c}0a;font-weight:600;'>{b}</span>"
        html += "</div>"
    if flows:
        for fl in flows[:2]:
            parts = [p.strip() for p in fl.replace("->","→").split("→") if p.strip()]
            fhtml = ""
            for j, part in enumerate(parts[:5]):
                fhtml += f"<span style='background:{c}0a;border:1px solid {c}28;border-radius:3px;padding:2px 6px;font-size:9px;color:#c0c0e0;'>{part[:25]}</span>"
                if j < len(parts)-1: fhtml += f"<span style='color:{c};font-size:10px;opacity:0.5;margin:0 2px;'>→</span>"
            html += f"<div style='display:flex;align-items:center;flex-wrap:wrap;gap:2px;margin-bottom:6px;padding:5px;background:rgba(0,0,0,0.3);border-radius:5px;'>{fhtml}</div>"
    if bullets:
        for item in bullets[:10]:
            if len(item) > 100: item = item[:100]+"..."
            html += f"<div style='display:flex;gap:5px;margin-bottom:3px;'><span style='color:{c};opacity:0.55;flex-shrink:0;font-size:9px;'>▸</span><span style='font-size:10px;color:#7070a0;line-height:1.4;'>{item}</span></div>"
    html += "</div>"
    return html


def build_json(artifacts: dict) -> dict:
    return {
        "pipeline_status": {
            "total_agents": 7,
            "completed": sum(1 for k in ["requirements","plan","code","documentation","tests","deployment"] if artifacts.get(k)),
            "session_id": st.session_state.session_id[:16],
            "model": "llama-3.3-70b-versatile",
            "rag_enabled": True,
            "guardrails_enabled": True,
        },
        "agents": {
            "requirement_analyzer": {"status": "completed" if artifacts.get("requirements") else "skipped"},
            "planner":              {"status": "completed" if artifacts.get("plan")          else "skipped"},
            "code_generator":       {"status": "completed" if artifacts.get("code")          else "skipped", "lines": len(artifacts.get("code","").split("\n"))},
            "bug_fixer":            {"status": "completed"},
            "documentation":        {"status": "completed" if artifacts.get("documentation") else "skipped"},
            "testing":              {"status": "completed" if artifacts.get("tests")         else "skipped"},
            "deployment":           {"status": "completed" if artifacts.get("deployment")    else "skipped"},
        }
    }


def show_artifacts_fn(artifacts: dict, msg_id: str):
    json_str = json.dumps(build_json(artifacts), indent=2)
    sections = [
        ("📋","Requirements","#818cf8","requirements","notebook"),
        ("🗺️","Plan",        "#a78bfa","plan",         "notebook"),
        ("💻","Code",         "#34d399","code",         "code_py"),
        ("📚","Docs",         "#fbbf24","documentation","notebook"),
        ("🧪","Tests",        "#4ade80","tests",        "code_py"),
        ("🚀","Deploy",       "#60a5fa","deployment",   "code_yaml"),
        ("🔧","JSON",         "#a78bfa","_json",        "json"),
    ]
    for icon, title, color, field, stype in sections:
        has = (field == "_json") or bool(artifacts.get(field))
        if not has: continue
        key     = f"{msg_id}_{field}"
        is_open = st.session_state.show_sections.get(key, False)
        c       = color
        bg      = "rgba(99,102,241,0.07)" if is_open else "rgba(255,255,255,0.01)"
        border  = c if is_open else "rgba(99,102,241,0.08)"
        r       = "7px 7px 0 0" if is_open else "7px"
        bb      = "none" if is_open else f"1px solid {border}"
        stxt    = "▼ collapse" if is_open else "▶ expand"
        sc      = f"{c}55" if is_open else "rgba(99,102,241,0.25)"
        st.markdown(
            f"<div style='display:flex;align-items:center;gap:8px;padding:7px 12px;background:{bg};border-radius:{r};border:1px solid {border};border-bottom:{bb};cursor:pointer;'><div style='width:24px;height:24px;border-radius:6px;background:{c}0d;border:1px solid {c}25;display:flex;align-items:center;justify-content:center;font-size:12px;flex-shrink:0;'>{icon}</div><div style='flex:1;'><p style='font-size:11px;font-weight:700;color:#e2e8f0;margin:0;'>{title}</p><p style='font-size:8px;color:{sc};margin:0;'>{stxt}</p></div><span style='background:{c}0d;border:1px solid {c}25;border-radius:4px;padding:1px 6px;font-size:7px;color:{c};font-weight:700;text-transform:uppercase;'>{field.replace('_','')}</span></div>",
            unsafe_allow_html=True
        )
        toggle_label = "▼  Collapse" if is_open else "▶  Click to expand"
        toggle_box = st.container(key=f"toggle_box_{key}")
        with toggle_box:
            if st.button(toggle_label, key=f"btn_{key}", use_container_width=True):
                st.session_state.show_sections[key] = not is_open
                st.rerun()
        if is_open:
            ps = f"background:#03030a;border:1px solid {c}15;border-top:none;border-radius:0 0 7px 7px;padding:0.5rem;"
            if stype == "notebook":
                st.markdown(f"<div style='{ps}'>" + format_notebook(artifacts.get(field,""), c) + "</div>", unsafe_allow_html=True)
            elif stype == "code_py":
                st.markdown(f"<div style='{ps}'>", unsafe_allow_html=True)
                st.code(artifacts[field], language="python")
                st.download_button("⬇️ Download", artifacts[field], "code.py", use_container_width=True, key=f"dl_{key}")
                st.markdown("</div>", unsafe_allow_html=True)
            elif stype == "code_yaml":
                st.markdown(f"<div style='{ps}'>", unsafe_allow_html=True)
                st.code(artifacts[field], language="yaml")
                st.download_button("⬇️ Download", artifacts[field], "docker-compose.yml", use_container_width=True, key=f"dl_{key}")
                st.markdown("</div>", unsafe_allow_html=True)
            elif stype == "json":
                st.markdown(f"<div style='{ps}'>", unsafe_allow_html=True)
                st.code(json_str, language="json")
                st.download_button("⬇️ JSON", json_str, "output.json", mime="application/json", use_container_width=True, key=f"dl_{key}")
                st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div style='height:3px;'></div>", unsafe_allow_html=True)


def render_agent_pipeline(active_idx: int, placeholder):
    """Render a horizontal row of 7 dots, one per agent, lighting up
    sequentially as the pipeline progresses. active_idx is the index
    (0-6) of the agent currently running; all prior dots show as done."""
    pipeline_steps = [
        ("🔍","Analyze",  "#818cf8"),
        ("📋","Plan",     "#60a5fa"),
        ("⌨️","Generate", "#4ade80"),
        ("🔧","Fix",      "#f87171"),
        ("📄","Document", "#fbbf24"),
        ("🧪","Test",     "#22d3ee"),
        ("🚀","Deploy",   "#a78bfa"),
    ]
    dots_html = "<div style='display:flex;align-items:center;justify-content:center;gap:6px;padding:14px 8px;'>"
    for i, (icon, label, color) in enumerate(pipeline_steps):
        if i < active_idx:
            state = "done"
        elif i == active_idx:
            state = "active"
        else:
            state = "pending"

        if state == "done":
            circle = (f"background:{color};border:1px solid {color};"
                       f"box-shadow:0 0 8px {color}; color:#06060f;")
            label_color = color
        elif state == "active":
            circle = (f"background:{color}25;border:2px solid {color};"
                       f"box-shadow:0 0 12px {color}; color:{color};"
                       f"animation:pulse-dot 1s ease-in-out infinite;")
            label_color = color
        else:
            circle = "background:rgba(255,255,255,0.03);border:1px solid rgba(99,102,241,0.12);color:#3a3a6e;"
            label_color = "#3a3a6e"

        dots_html += (
            "<div style='display:flex;flex-direction:column;align-items:center;gap:4px;flex:1;'>"
            f"<div style='width:30px;height:30px;border-radius:50%;{circle}"
            "display:flex;align-items:center;justify-content:center;font-size:13px;'>"
            f"{'✓' if state=='done' else icon}</div>"
            f"<div style='font-size:8px;font-weight:600;color:{label_color};white-space:nowrap;'>{label}</div>"
            "</div>"
        )
        if i < len(pipeline_steps) - 1:
            line_color = color if i < active_idx else "rgba(99,102,241,0.12)"
            dots_html += f"<div style='height:1px;flex:0.4;background:{line_color};margin-top:-16px;'></div>"
    dots_html += "</div>"

    placeholder.markdown(
        "<style>@keyframes pulse-dot{0%,100%{opacity:1;}50%{opacity:0.5;}}</style>" + dots_html,
        unsafe_allow_html=True
    )


def handle_response(prompt: str):
    with st.chat_message("assistant"):
        pipeline_placeholder = st.empty()
        status_placeholder = st.empty()
        try:
            pipeline_stages = [
                (0, "Guardrails validating input..."),
                (1, "Requirement Analyzer reading request..."),
                (2, "Planner building roadmap..."),
                (3, "Code Generator writing implementation..."),
            ]
            for step, msg in pipeline_stages:
                render_agent_pipeline(step, pipeline_placeholder)
                status_placeholder.markdown(
                    f"<div style='text-align:center;font-size:10px;color:#7878b0;'>{msg}</div>",
                    unsafe_allow_html=True
                )
                st.session_state.active_step = step
                time.sleep(0.3)
            response = httpx.post(
                "http://localhost:8000/chat",
                json={"message": prompt, "session_id": st.session_state.session_id},
                timeout=180,
            )
            render_agent_pipeline(5, pipeline_placeholder)
            status_placeholder.markdown(
                "<div style='text-align:center;font-size:10px;color:#7878b0;'>"
                "Bug Fixer + Docs + Tests + Deploy running...</div>",
                unsafe_allow_html=True
            )
            st.session_state.active_step = 5; time.sleep(0.3)
            render_agent_pipeline(7, pipeline_placeholder)
            status_placeholder.markdown(
                "<div style='text-align:center;font-size:10px;color:#4ade80;font-weight:600;'>"
                "✓ All 7 agents completed!</div>",
                unsafe_allow_html=True
            )
            st.session_state.active_step = 6; time.sleep(0.3)
            pipeline_placeholder.empty()
            status_placeholder.empty()
            data = response.json()
            if data.get("status") == "blocked":
                st.warning(f"Blocked: {data.get('response','Safety filter triggered')}"); return
            if data.get("status") == "error":
                st.error(f"Error: {data.get('error')}"); return
            artifacts   = data.get("artifacts", {})
            rag_used    = data.get("rag_used", False)
            memory_used = data.get("memory_used", False)
            msg_id      = str(uuid.uuid4())[:8]
            st.markdown(
                "<div style='background:rgba(16,185,129,0.05);border:1px solid rgba(16,185,129,0.15);"
                "border-radius:8px;padding:8px 12px;margin-bottom:8px;"
                "display:flex;align-items:center;gap:8px;'>"
                "<span style='font-size:14px;'>✅</span>"
                "<div><p style='font-size:11px;font-weight:700;color:#4ade80;margin:0;'>All 7 agents completed</p>"
                "<p style='font-size:9px;color:rgba(74,222,128,0.4);margin:0;'>Analyze → Plan → Code → Fix → Docs → Test → Deploy</p></div>"
                "<p style='font-size:9px;color:rgba(74,222,128,0.25);margin:0 0 0 auto;font-weight:600;'>Click cards below</p>"
                "</div>", unsafe_allow_html=True
            )
            if rag_used:
                st.markdown("<div style='background:rgba(59,130,246,0.04);border:1px solid rgba(59,130,246,0.12);border-radius:6px;padding:5px 10px;margin-bottom:4px;font-size:10px;color:#60a5fa;font-weight:600;'>🧠 RAG context injected</div>", unsafe_allow_html=True)
            if memory_used:
                st.markdown("<div style='background:rgba(124,58,237,0.04);border:1px solid rgba(124,58,237,0.12);border-radius:6px;padding:5px 10px;margin-bottom:4px;font-size:10px;color:#a78bfa;font-weight:600;'>💾 Memory used</div>", unsafe_allow_html=True)
            show_artifacts_fn(artifacts, msg_id)
            st.session_state.messages.append({
                "role":"assistant","content":"All 7 agents completed!",
                "artifacts":artifacts,"rag_used":rag_used,"memory_used":memory_used,"msg_id":msg_id,
            })
            st.rerun()
        except httpx.TimeoutException:
            pipeline_placeholder.empty(); status_placeholder.empty()
            st.error("Timeout. Try a simpler prompt.")
        except Exception as e:
            pipeline_placeholder.empty(); status_placeholder.empty()
            st.error(f"Error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# LAYOUT — inject a full-height flex container via HTML, columns just for
# Streamlit widget placement. The real visual panels live inside st.markdown.
# ══════════════════════════════════════════════════════════════════════════════
left_col, center_col, right_col = st.columns([1.4, 5.5, 1.6], gap="small")

# ══════════════════════════════════════════════════════════════════════════════
# LEFT — Workflow Panel
# ══════════════════════════════════════════════════════════════════════════════
with left_col:
    st.markdown("""
    <div style='padding:40px 10px 10px;'>

    <!-- Brand -->
    <div style='display:flex;align-items:center;gap:7px;margin-bottom:6px;'>
        <span style='color:#6366f1;font-size:15px;font-weight:900;font-family:JetBrains Mono,monospace;'>&lt;/&gt;</span>
        <div>
            <div style='font-size:11px;font-weight:800;color:#e2e8f0;line-height:1.2;'>CodeForge AI</div>
            <div style='font-size:8px;color:rgba(99,102,241,0.4);'>AI-Powered Dev System</div>
        </div>
    </div>
    <div style='height:1px;background:rgba(99,102,241,0.07);margin-bottom:8px;'></div>
    <div style='font-size:7px;font-weight:800;letter-spacing:0.12em;text-transform:uppercase;
    color:rgba(99,102,241,0.35);margin-bottom:6px;'>Workflow</div>
    """, unsafe_allow_html=True)

    steps = [
        ("📈","#34d399","Analyze",  "Analyze requirements or existing code"),
        ("📋","#60a5fa","Plan",     "Create implementation plan and architecture"),
        ("</>","#4ade80","Generate", "Generate code and implement features"),
        ("🔧","#f87171","Fix",      "Fix bugs and resolve issues"),
        ("📄","#fbbf24","Document", "Generate documentation and guides"),
        ("🧪","#22d3ee","Test",     "Create and run tests"),
        ("🚀","#a78bfa","Deploy",   "Deploy and monitor applications"),
    ]
    active = st.session_state.active_step
    for i, (icon, color, label, desc) in enumerate(steps):
        is_active = (i == active)
        bg     = f"{color}12" if is_active else "rgba(255,255,255,0.015)"
        border = f"{color}50" if is_active else "rgba(99,102,241,0.06)"
        lc     = "#e2e8f0" if is_active else "#8888b8"
        st.markdown(f"""
        <div style='position:relative;background:{bg};border:1px solid {border};
        border-radius:8px;padding:8px 10px;margin-bottom:6px;'>
            <div style='display:flex;align-items:flex-start;gap:8px;'>
                <div style='width:26px;height:26px;border-radius:6px;background:{color}1a;
                border:1px solid {color}35;display:flex;align-items:center;justify-content:center;
                font-size:12px;flex-shrink:0;color:{color};font-weight:700;'>{icon}</div>
                <div>
                    <div style='font-size:11px;font-weight:700;color:{lc};line-height:1.3;'>{label}</div>
                    <div style='font-size:9px;color:#454575;line-height:1.35;margin-top:1px;'>{desc}</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:1px;background:rgba(99,102,241,0.06);margin:10px 0 10px;'></div>", unsafe_allow_html=True)

    # Upload box (now appears first, before the backend status badge)
    uploaded_file = st.file_uploader("Upload", type=["pdf","txt","md","py"], label_visibility="collapsed")
    if uploaded_file:
        if st.button("Ingest Document", use_container_width=True):
            with st.status("Processing..."):
                try:
                    res = httpx.post("http://localhost:8000/upload",
                        files={"file": (uploaded_file.name, uploaded_file.getvalue())}, timeout=60)
                    d = res.json()
                    if d.get("status") == "ok":
                        st.session_state.last_upload = {
                            "filename": d.get("filename", uploaded_file.name),
                            "chunks_added": d.get("chunks_added", 0),
                            "preview": d.get("preview", ""),
                            "summary": d.get("summary", ""),
                        }
                        st.success(f"Added {d['chunks_added']} chunks!")
                        st.rerun()
                    else: st.error(d.get("error"))
                except Exception as e: st.error(str(e))

    # Show preview + summary of the most recently uploaded document
    if st.session_state.get("last_upload"):
        lu = st.session_state.last_upload
        st.markdown(
            "<div style='background:rgba(99,102,241,0.05);border:1px solid rgba(99,102,241,0.15);"
            "border-radius:7px;padding:9px 10px;margin:6px 0;'>"
            f"<div style='font-size:9px;font-weight:700;color:#a5b4fc;margin-bottom:4px;'>📄 {lu['filename']}</div>"
            "<div style='font-size:8px;font-weight:700;color:rgba(99,102,241,0.6);"
            "text-transform:uppercase;letter-spacing:0.06em;margin-bottom:3px;'>Summary</div>"
            f"<div style='font-size:9px;color:#9090c8;line-height:1.5;margin-bottom:8px;'>{lu['summary']}</div>"
            "<div style='font-size:8px;font-weight:700;color:rgba(99,102,241,0.6);"
            "text-transform:uppercase;letter-spacing:0.06em;margin-bottom:3px;'>Preview</div>"
            f"<div style='font-size:8.5px;color:#5a5a90;line-height:1.5;"
            "font-family:JetBrains Mono,monospace;'>" + lu['preview'] + "</div>"
            "</div>",
            unsafe_allow_html=True
        )

    # Backend badge
    if backend_ok:
        st.markdown("<div style='display:inline-flex;align-items:center;gap:4px;padding:3px 8px;background:rgba(16,185,129,0.06);border:1px solid rgba(16,185,129,0.15);border-radius:5px;font-size:9px;color:#34d399;font-weight:700;margin:8px 0;'><div style='width:4px;height:4px;border-radius:50%;background:#34d399;box-shadow:0 0 4px #34d399;'></div>Backend online</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='display:inline-flex;align-items:center;gap:4px;padding:3px 8px;background:rgba(239,68,68,0.06);border:1px solid rgba(239,68,68,0.15);border-radius:5px;font-size:9px;color:#f87171;font-weight:700;margin:8px 0;'><div style='width:4px;height:4px;border-radius:50%;background:#f87171;'></div>Backend offline</div>", unsafe_allow_html=True)

    if chunks > 0:
        st.markdown(f"<div style='background:rgba(59,130,246,0.06);border:1px solid rgba(59,130,246,0.15);border-radius:5px;padding:4px 7px;font-size:9px;color:#60a5fa;margin:0 0 8px;font-weight:600;'>📚 {chunks} chunks loaded</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="small")
    with c1:
        if st.button("Clear", use_container_width=True):
            st.session_state.messages = []; st.session_state.show_sections = {}; st.session_state.active_step = 0; st.rerun()
    with c2:
        if st.button("New", use_container_width=True):
            st.session_state.messages = []; st.session_state.show_sections = {}; st.session_state.session_id = str(uuid.uuid4()); st.session_state.active_step = 0; st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CENTER — Main Content
# ══════════════════════════════════════════════════════════════════════════════
with center_col:
    # Outer wrapper — flows from top naturally
    st.markdown("""
    <div style='background:#080810;padding:40px 12px 0;'>
    <div style='font-size:13px;font-weight:800;color:#e2e8f0;line-height:1.6;
    letter-spacing:-0.2px;margin:0 0 12px;'>⚡ Quick Examples</div>
    """, unsafe_allow_html=True)

    # 4 example cards
    ec1, ec2, ec3, ec4 = st.columns(4, gap="small")
    examples = [
        (ec1,"≡", "#6366f1","Todo API",     "Complete todo API with CRUD",
         "Build a complete todo REST API with FastAPI and PostgreSQL including CRUD operations, JWT authentication, and pagination"),
        (ec2,"🛡","#a78bfa","Auth System",  "User auth and authorization",
         "Build a JWT authentication system with login, register, refresh tokens and role-based access using FastAPI"),
        (ec3,"🗄","#34d399","Data Pipeline","Data processing pipeline ETL",
         "Build a data pipeline that reads CSV files, validates and cleans data and stores results in SQLite"),
        (ec4,"🔗","#fbbf24","URL Shortener","URL shortener with analytics",
         "Build a URL shortener service with FastAPI, SQLite, custom aliases and click analytics"),
    ]
    for col, icon, color, title, desc, ex_prompt in examples:
        with col:
            st.markdown(f"""
            <div class='example-card' style='--accent:{color};border-radius:8px;
            padding:10px 10px 8px;margin-bottom:3px;min-height:88px;'>
                <span style='font-size:17px;color:{color};display:block;margin-bottom:4px;'>{icon}</span>
                <div style='font-size:11px;font-weight:700;color:#e2e8f0;margin-bottom:3px;'>{title}</div>
                <div style='font-size:9px;color:#45458a;line-height:1.4;'>{desc}</div>
            </div>""", unsafe_allow_html=True)
            st.markdown("<div class='exbtn'>", unsafe_allow_html=True)
            if st.button(f"▶ {title}", key=f"ex_{title}", use_container_width=True):
                st.session_state.example = ex_prompt
            st.markdown("</div>", unsafe_allow_html=True)

    # Agent output header + Clear button
    hcol1, hcol2 = st.columns([5, 1])
    with hcol1:
        st.markdown("""
        <div style='display:flex;align-items:center;gap:6px;margin:8px 0 5px;'>
            <span style='font-size:12px;'>✨</span>
            <div style='font-size:12px;font-weight:800;color:#e2e8f0;'>Agent Output</div>
        </div>
        """, unsafe_allow_html=True)
    with hcol2:
        if st.button("🗑 Clear", key="clear_output", use_container_width=True):
            st.session_state.messages = []
            st.session_state.show_sections = {}
            st.session_state.active_step = 0
            st.rerun()

    # Output area
    if not st.session_state.messages:
        st.markdown("""
        <div style='background:#0c0c1f;border:1px solid rgba(99,102,241,0.09);
        border-radius:8px;padding:16px;min-height:420px;'>
        <div style='font-size:11px;color:#5a5a90;line-height:1.5;'>
            AI-generated architecture, plans and outputs appear here.
            <div style='margin-top:14px;padding:12px 14px;background:rgba(99,102,241,0.04);
            border:1px solid rgba(99,102,241,0.08);border-radius:8px;
            font-family:JetBrains Mono,monospace;font-size:11px;line-height:1.7;'>
                <div style='color:#4ade80;font-weight:700;margin-bottom:6px;'>📋 Project Analysis Complete</div>
                <div style='color:#7878b0;'>• Type: <span style='color:#a5b4fc;'>Web Application</span></div>
                <div style='color:#7878b0;'>• Framework: <span style='color:#a5b4fc;'>FastAPI</span></div>
                <div style='color:#7878b0;'>• Database: <span style='color:#a5b4fc;'>PostgreSQL</span></div>
                <div style='color:#7878b0;'>• Authentication: <span style='color:#a5b4fc;'>JWT</span></div>
                <div style='color:#7878b0;margin-bottom:10px;'>• Status: <span style='color:#4ade80;'>Ready for implementation</span></div>
                <div style='color:#818cf8;font-weight:700;margin-bottom:6px;'>✨ Recommended Architecture</div>
                <div style='color:#5a5a90;white-space:pre;'>project/
├── app/
│   ├── api/
│   ├── core/
│   ├── models/
│   └── schemas/
├── tests/
├── docs/
└── requirements.txt</div>
            </div>
        </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background:#0c0c1f;border:1px solid rgba(99,102,241,0.09);
        border-radius:8px;padding:12px;'>
        """, unsafe_allow_html=True)
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg.get("artifacts") and msg.get("msg_id"):
                    show_artifacts_fn(msg["artifacts"], msg["msg_id"])
        st.markdown("</div>", unsafe_allow_html=True)

    # Chat input pinned at bottom
    st.markdown("<div style='padding:6px 0 4px;'>", unsafe_allow_html=True)
    if prompt := st.chat_input("Describe what you want to build..."):
        st.session_state.messages.append({"role":"user","content":prompt})
        st.rerun()
    st.markdown("</div></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# RIGHT — System Panel
# ══════════════════════════════════════════════════════════════════════════════
with right_col:
    sys_cards = [
        ("👥","#6366f1","AGENTS", "7",         "Active agents"),
        ("🤖","#a78bfa","MODEL",  "Llama 3.3", "Large Language Model"),
        ("🗄","#34d399","RAG",    "Enabled",   "Retrieval Augmented Generation"),
        ("📡","#4ade80","STATUS", "Online",    "All systems operational"),
    ]
    cards_html = ""
    for icon, color, label, value, desc in sys_cards:
        if label == "STATUS":
            dot_html = (
                "<div style='width:5px;height:5px;border-radius:50%;"
                f"background:{color};margin-left:auto;box-shadow:0 0 5px {color};'></div>"
            )
        else:
            dot_html = ""
        cards_html += (
            f"<div class='system-card' style='--accent:{color};background:#0f0f24;"
            "border:1px solid rgba(99,102,241,0.08);"
            "border-radius:9px;padding:11px 12px;margin-bottom:8px;'>"
            "<div style='display:flex;align-items:center;gap:8px;margin-bottom:7px;'>"
            f"<div style='width:26px;height:26px;border-radius:7px;background:{color}15;"
            f"border:1px solid {color}30;display:flex;align-items:center;"
            f"justify-content:center;font-size:13px;'>{icon}</div>"
            f"<div style='font-size:8px;font-weight:700;color:{color};"
            f"text-transform:uppercase;letter-spacing:0.1em;'>{label}</div>"
            f"{dot_html}"
            "</div>"
            "<div style='font-size:18px;font-weight:800;color:#e2e8f0;"
            f"letter-spacing:-0.4px;line-height:1;margin-bottom:4px;'>{value}</div>"
            "<div style='font-size:9px;color:#3a3a6e;line-height:1.3;'>"
            f"{desc}</div>"
            "</div>"
        )

    tech_items = [
        ("⚡","Llama 3.3 70B","#6366f1"),
        ("🔗","LangGraph",    "#34d399"),
        ("🧠","Hybrid RAG",   "#a78bfa"),
        ("🛡️","Guardrails",  "#fbbf24"),
        ("🌐","FastAPI",      "#60a5fa"),
        ("📐","Pydantic",     "#f87171"),
    ]
    tech_rows_html = ""
    for t_icon, t_name, t_color in tech_items:
        tech_rows_html += (
            "<div style='display:flex;align-items:center;gap:7px;padding:5px 0;"
            "border-bottom:1px solid rgba(99,102,241,0.04);'>"
            f"<span style='font-size:11px;flex-shrink:0;'>{t_icon}</span>"
            f"<span style='font-size:10px;font-weight:600;color:#6868a8;flex:1;'>{t_name}</span>"
            f"<div style='width:4px;height:4px;border-radius:50%;background:{t_color};"
            f"box-shadow:0 0 4px {t_color};flex-shrink:0;'></div>"
            "</div>"
        )

    right_panel_html = (
        "<div style='padding:40px 10px 10px;'>"
        "<div style='font-size:12px;font-weight:800;color:#e2e8f0;margin-bottom:10px;'>System</div>"
        f"{cards_html}"
        "<div style='height:1px;background:rgba(99,102,241,0.07);margin:10px 0 8px;'></div>"
        "<div style='font-size:8px;font-weight:800;letter-spacing:0.12em;"
        "text-transform:uppercase;color:rgba(99,102,241,0.4);margin-bottom:8px;'>"
        "Tech Stack</div>"
        f"<div>{tech_rows_html}</div>"
        "</div>"
    )
    st.markdown(right_panel_html, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PROCESS MESSAGES / EXAMPLES
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.messages:
    last = st.session_state.messages[-1]
    if last["role"] == "user":
        msgs = st.session_state.messages
        if len(msgs) < 2 or msgs[-2]["role"] != "assistant":
            handle_response(last["content"])

if "example" in st.session_state:
    ex_prompt = st.session_state.example
    del st.session_state.example
    st.session_state.messages.append({"role":"user","content":ex_prompt})
    handle_response(ex_prompt)