"""邻里帮 V6.1 云端版。

用户端保留 V6.1 手机竖屏视觉，数据统一使用 Supabase。
后台端通过 admin_app.py 调用本文件中的 admin_main()。
"""

from __future__ import annotations

import base64
import email.utils
import hashlib
import hmac
import html
import json
import os
import random
import ssl
import time
import wave
from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.parse import urlencode

import numpy as np
import streamlit as st
import websocket
from dotenv import load_dotenv
from supabase import create_client


load_dotenv()

APP_NAME = "邻里帮"
COMMUNITY = "安靖社区"
COMMUNITY_INVITE_CODE = "ANJING2026"
COMMUNITY_PHONE = "16608008838"

REQUEST_TYPES = {
    "生活需求": {
        "icon": "bag",
        "tone": "green",
        "detail": "买药、取物、日常照看、生活咨询",
        "placeholder": "例如：老人想买降压药，家里人暂时不在身边。",
    },
    "上门事项": {
        "icon": "wrench",
        "tone": "orange",
        "detail": "维修、家政、理发、助浴、上门测量",
        "placeholder": "例如：想联系社区认证维修师傅看一下水龙头。",
    },
    "外出协助": {
        "icon": "walk",
        "tone": "blue",
        "detail": "陪诊、复查、办事、短途陪同",
        "placeholder": "例如：明天去医院复查，希望有人陪同。",
    },
    "社区反馈": {
        "icon": "message",
        "tone": "gray",
        "detail": "楼道、照明、通行、适老环境隐患",
        "placeholder": "例如：楼道堆了杂物，老人上下楼不方便。",
    },
}

PHONEBOOK_SERVICE_NAME = "自己选服务"
PHONEBOOK_CATEGORIES = [
    "水电维修",
    "家政保洁",
    "跑腿代办",
    "陪同外出",
    "便民理发",
    "健康照护",
]

FONT_LEVELS = {
    "标准": 1.0,
    "偏大": 1.12,
    "特大": 1.24,
}

TICKET_STATUSES = ["待接收", "处理中", "已预约", "已完成"]
ACTIVITY_STATUSES = ["待发布", "审核中", "已发布", "已隐藏"]


def secret(name: str, default: str = "") -> str:
    try:
        if name in st.secrets:
            return str(st.secrets[name]).strip()
    except FileNotFoundError:
        pass
    return os.getenv(name, default).strip()


@st.cache_resource
def supabase_client():
    url = secret("SUPABASE_URL")
    key = secret("SUPABASE_KEY")
    if not url or not key:
        st.error("缺少 Supabase 配置，请在 Streamlit secrets 中填写 SUPABASE_URL 和 SUPABASE_KEY。")
        st.stop()
    return create_client(url, key)


def db_error(exc: Exception) -> None:
    st.error("Supabase 表结构还没有准备好，或当前 key 没有权限。请先在 Supabase SQL Editor 运行本目录下的 supabase_schema_v6_cloud.sql。")
    st.caption(str(exc))
    st.stop()


def run_query(builder):
    try:
        return builder.execute().data
    except Exception as exc:
        db_error(exc)


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def esc(value) -> str:
    return html.escape("" if value is None else str(value))


def icon(name: str) -> str:
    paths = {
        "bag": '<path d="M7 9h10l1 10H6L7 9Z"/><path d="M9 9a3 3 0 0 1 6 0"/>',
        "wrench": '<path d="M15 6a5 5 0 0 0 3 7l-6 6-3-3 6-6a5 5 0 0 0 0-4Z"/><path d="M5 19l4-4"/>',
        "walk": '<path d="M13 5a2 2 0 1 0 0-4 2 2 0 0 0 0 4Z"/><path d="M11 7l-3 5 4 1 1 7"/><path d="M13 10l3 2"/><path d="M8 20l3-5"/>',
        "message": '<path d="M5 5h14v10H9l-4 4V5Z"/><path d="M8 9h8"/><path d="M8 12h5"/>',
        "mic": '<path d="M12 3a3 3 0 0 0-3 3v5a3 3 0 0 0 6 0V6a3 3 0 0 0-3-3Z"/><path d="M5 10a7 7 0 0 0 14 0"/><path d="M12 17v4"/><path d="M9 21h6"/>',
        "home": '<path d="M4 11 12 4l8 7"/><path d="M6 10v10h12V10"/><path d="M10 20v-6h4v6"/>',
        "ticket": '<path d="M5 5h14v14H5z"/><path d="M8 9h8"/><path d="M8 13h8"/><path d="M8 17h5"/>',
        "user": '<path d="M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z"/><path d="M4 21a8 8 0 0 1 16 0"/>',
        "users": '<path d="M9 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z"/><path d="M2 20a7 7 0 0 1 14 0"/><path d="M17 9a3 3 0 1 0-1-5.8"/><path d="M17 20h5a6 6 0 0 0-6-6"/>',
        "phone": '<path d="M7 4h4l1 4-2 1a12 12 0 0 0 5 5l1-2 4 1v4c0 1-1 2-2 2A15 15 0 0 1 5 6c0-1 1-2 2-2Z"/>',
        "speaker": '<path d="M4 10v4h4l5 4V6l-5 4H4Z"/><path d="M16 9a4 4 0 0 1 0 6"/>',
        "service": '<path d="M4 6h16"/><path d="M6 6v14h12V6"/><path d="M9 10h6"/><path d="M9 14h6"/>',
        "heart": '<path d="M20 7c0 6-8 11-8 11S4 13 4 7a4 4 0 0 1 7-2 4 4 0 0 1 9 2Z"/>',
    }
    body = paths.get(name, paths["ticket"])
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">{body}</svg>'


def css() -> None:
    scale = FONT_LEVELS.get(st.session_state.get("font", "标准"), 1.0)
    shell_width = 860 if st.session_state.get("app_mode") == "admin" else 430
    st.markdown(
        f"""
        <style>
        :root {{
            --green:#128457;
            --deep:#0E6845;
            --mint:#EAF4EF;
            --paper:#FFFDF8;
            --line:#E6E2DA;
            --text:#20272B;
            --sub:#727A7E;
            --orange:#F46B1F;
            --font-scale:{scale};
        }}
        .stApp {{ background:linear-gradient(180deg,#F8F5EF 0%,#FFFDF8 54%,#F4F8F4 100%); color:var(--text); }}
        [data-testid="stHeader"] {{ background:transparent; }}
        .block-container {{ max-width:{shell_width}px; padding:18px 12px 108px; }}
        html, body, .stMarkdown, .stTextInput label, .stTextArea label, .stSelectbox label, .stRadio label, .stCheckbox label {{
            font-size:calc(16px * var(--font-scale));
        }}
        .service-hero {{ background:linear-gradient(135deg,#108354,#129668); color:white; border-radius:0 0 22px 22px; padding:24px 24px 28px; box-shadow:0 18px 40px rgba(18,132,87,.22); }}
        .service-hero-top {{ display:flex; justify-content:space-between; align-items:flex-start; gap:14px; }}
        .service-title {{ font-size:calc(29px * var(--font-scale)); font-weight:900; line-height:1.2; }}
        .service-sub {{ margin-top:8px; font-size:calc(15px * var(--font-scale)); opacity:.9; font-weight:700; }}
        .call-pill,.switch-pill {{ display:inline-flex; align-items:center; gap:6px; border-radius:999px; background:#fff; color:var(--green)!important; padding:9px 13px; text-decoration:none!important; font-weight:900; white-space:nowrap; }}
        .call-pill svg,.switch-pill svg {{ width:19px; height:19px; }}
        .notice-card,.ticket-row,.list-card,.profile-card,.voice-row,.activity-card,.service-card,.record-card,.auth-card,.admin-card {{ background:white; border:1px solid var(--line); border-radius:14px; box-shadow:0 10px 24px rgba(34,40,36,.05); }}
        .notice-card {{ margin:14px 0; padding:12px 14px; display:grid; grid-template-columns:24px 1fr 14px; gap:10px; align-items:center; color:#4C5651; }}
        .notice-card svg {{ width:22px; height:22px; color:var(--green); }}
        .notice-window {{ overflow:hidden; white-space:nowrap; }}
        .notice-track {{ display:inline-flex; gap:18px; animation:notice 19s linear infinite; }}
        .notice-item {{ color:#67726C; }}
        @keyframes notice {{ from {{ transform:translateX(0); }} to {{ transform:translateX(-50%); }} }}
        .quick-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; margin:14px 0; }}
        .quick-card {{ min-height:112px; border-radius:16px; padding:16px; text-decoration:none!important; display:flex; flex-direction:column; justify-content:space-between; color:white!important; font-weight:900; box-shadow:0 14px 26px rgba(21,92,63,.13); }}
        .quick-card svg {{ width:31px; height:31px; }}
        .tone-green {{ background:#128457; }} .tone-orange {{ background:#E8752E; }} .tone-blue {{ background:#2877A8; }} .tone-gray {{ background:#5B7468; }}
        .quick-title {{ font-size:calc(20px * var(--font-scale)); }}
        .ticket-row {{ margin:14px 0; padding:17px; display:grid; grid-template-columns:34px 1fr auto 14px; gap:12px; align-items:center; text-decoration:none!important; color:var(--text)!important; }}
        .ticket-row svg {{ width:30px; height:30px; color:var(--green); }}
        .ticket-title,.list-title,.progress-title {{ font-weight:900; font-size:calc(18px * var(--font-scale)); color:var(--text); }}
        .ticket-sub,.list-sub,.progress-sub,.meta {{ color:var(--sub); font-size:calc(14px * var(--font-scale)); line-height:1.65; }}
        .ticket-count {{ color:var(--green); font-weight:900; }}
        .voice-row {{ margin:14px 0; padding:17px; display:grid; grid-template-columns:58px 1fr; gap:14px; align-items:center; }}
        .voice-round {{ width:54px; height:54px; border-radius:50%; background:#EAF4EF; color:var(--green); display:grid; place-items:center; }}
        .voice-row strong {{ display:block; font-size:calc(20px * var(--font-scale)); }}
        .voice-row small {{ display:block; color:var(--sub); margin-top:4px; }}
        .appbar {{ display:grid; grid-template-columns:42px 1fr auto; align-items:center; margin-bottom:16px; }}
        .back-link {{ width:38px; height:38px; border-radius:50%; display:grid; place-items:center; background:#fff; color:var(--green)!important; text-decoration:none!important; font-size:30px; border:1px solid var(--line); }}
        .appbar-title {{ text-align:center; font-size:calc(22px * var(--font-scale)); font-weight:900; }}
        .version {{ color:#98A09A; font-size:13px; }}
        .type-row {{ background:#fff; border:1px solid var(--line); border-radius:14px; padding:15px; display:grid; grid-template-columns:42px 1fr 14px; gap:12px; align-items:center; margin-bottom:16px; }}
        .type-row svg {{ width:34px; height:34px; color:var(--green); }}
        .type-title {{ font-weight:900; font-size:calc(20px * var(--font-scale)); }}
        .form-label,.panel-title {{ font-weight:900; margin:18px 0 8px; font-size:calc(17px * var(--font-scale)); }}
        .field-hint,.privacy {{ color:var(--sub); font-size:calc(13px * var(--font-scale)); margin:6px 0; }}
        .stButton>button {{ border-radius:13px!important; min-height:48px; font-weight:900!important; border:1px solid var(--green)!important; background:var(--green)!important; color:#fff!important; }}
        .stButton>button[kind="primary"] {{ background:var(--deep)!important; color:#fff!important; border-color:var(--deep)!important; }}
        .stButton>button:disabled {{ background:#D9DED8!important; color:#6D756F!important; border-color:#D9DED8!important; opacity:1!important; }}
        .bottom {{ position:fixed; z-index:9998; left:50%; bottom:14px; transform:translateX(-50%); width:min(408px,calc(100vw - 28px)); background:rgba(255,255,255,.96); border:1px solid var(--line); border-radius:18px; box-shadow:0 15px 36px rgba(38,48,41,.17); display:grid; grid-template-columns:repeat(3,1fr); padding:9px 6px; }}
        .bottom a {{ color:#60655F!important; text-decoration:none!important; display:flex; flex-direction:column; align-items:center; gap:4px; font-weight:900; font-size:13px; }}
        .bottom a.active {{ color:var(--green)!important; }}
        .bottom svg {{ width:25px; height:25px; }}
        .profile-card {{ padding:17px; display:grid; grid-template-columns:58px 1fr; gap:14px; align-items:center; }}
        .avatar {{ width:54px; height:54px; border-radius:50%; background:#EAF4EF; color:var(--green); display:grid; place-items:center; }}
        .avatar svg {{ width:30px; height:30px; }}
        .profile-name {{ font-weight:900; font-size:calc(21px * var(--font-scale)); }}
        .list-card {{ padding:4px 0; margin:14px 0; overflow:hidden; }}
        .list-row {{ display:grid; grid-template-columns:34px 1fr auto; gap:12px; align-items:center; padding:15px 17px; border-bottom:1px solid #F0ECE5; color:var(--text); text-decoration:none!important; }}
        .list-row:last-child {{ border-bottom:0; }}
        .list-row svg {{ width:28px; height:28px; color:var(--green); }}
        .activity-card,.service-card,.record-card,.auth-card,.admin-card {{ padding:16px; margin:12px 0; }}
        .provider-head {{ display:flex; gap:8px; flex-wrap:wrap; align-items:center; }}
        .provider-lines {{ margin-top:10px; display:grid; gap:7px; }}
        .provider-lines div {{ display:grid; grid-template-columns:52px 1fr; gap:8px; align-items:start; color:var(--sub); font-size:calc(14px * var(--font-scale)); line-height:1.55; }}
        .provider-lines strong {{ color:var(--text); }}
        .badge {{ display:inline-block; border-radius:999px; padding:4px 9px; font-weight:900; font-size:13px; background:#EAF4EF; color:var(--green); border:1px solid #CDE8D9; }}
        .badge.gray {{ background:#F0F1F0; color:#6E746F; border-color:#DFE2DF; }}
        .badge.orange {{ background:#FFF1E8; color:#C65316; border-color:#FFD0B5; }}
        .dial-card {{ background:#FFF8E9; border:1px solid #F0DFBD; border-radius:14px; padding:16px; margin:12px 0; }}
        .dial-link {{ display:block; text-align:center; background:var(--orange); color:white!important; text-decoration:none!important; border-radius:13px; padding:13px 16px; font-weight:900; margin-top:10px; }}
        .admin-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:12px; }}
        .admin-actions {{ display:flex; gap:8px; flex-wrap:wrap; margin-top:10px; }}
        .review-head {{ display:flex; justify-content:space-between; align-items:flex-start; gap:18px; }}
        .auth-code-box {{ min-width:150px; text-align:center; border-radius:16px; padding:13px 16px; background:#EAF4EF; border:2px solid #128457; color:#0E6845; box-shadow:0 8px 20px rgba(18,132,87,.13); }}
        .auth-code-label {{ font-size:13px; font-weight:900; color:#4F6F60; letter-spacing:.08em; }}
        .auth-code-value {{ display:block; margin-top:4px; font-size:calc(31px * var(--font-scale)); line-height:1; font-weight:900; color:#0E6845; letter-spacing:.08em; }}
        .home-action-buttons {{ margin-top:12px; }}
        @media(max-width:520px) {{ .block-container {{ padding-left:12px!important; padding-right:12px!important; padding-top:12px!important; }} }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_state() -> None:
    defaults = {
        "page": "home",
        "font": "标准",
        "resident": None,
        "request_type": "生活需求",
        "note": "",
        "voice_text": "",
        "voice_error": "",
        "voice_audio_bytes": b"",
        "voice_audio_name": "",
        "voice_audio_type": "",
        "last_ticket": None,
        "dial_prompt": False,
        "recognized_audio_hash_home": "",
        "recognized_audio_hash_request": "",
        "admin_authed": False,
        "register_success": "",
        "register_return_page": "login",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)
    nav = st.query_params.get("nav")
    if nav:
        st.session_state.page = nav
        st.query_params.clear()
    request_type = st.query_params.get("request")
    if request_type in REQUEST_TYPES:
        st.session_state.request_type = request_type
        st.session_state.page = "request"
        st.query_params.clear()


def go(page: str, **kwargs) -> None:
    st.session_state.page = page
    for key, value in kwargs.items():
        st.session_state[key] = value
    st.query_params.clear()
    st.rerun()


def resident() -> dict | None:
    return st.session_state.get("resident")


def fetch_resident_by_login(phone: str, auth_code: str) -> dict | None:
    rows = run_query(
        supabase_client()
        .table("residents")
        .select("*, communities(name, service_phone, duty_name, duty_phone)")
        .eq("phone", phone)
        .eq("auth_code", auth_code)
        .eq("status", "已通过")
        .limit(1)
    )
    return rows[0] if rows else None


def default_community_id() -> int:
    rows = run_query(
        supabase_client()
        .table("communities")
        .select("id")
        .eq("invite_code", COMMUNITY_INVITE_CODE)
        .limit(1)
    )
    if not rows:
        st.error("未找到安靖社区配置，请先运行 Supabase 建表 SQL。")
        st.stop()
    return int(rows[0]["id"])


def refresh_resident() -> None:
    current = resident()
    if not current:
        return
    rows = run_query(
        supabase_client()
        .table("residents")
        .select("*, communities(name, service_phone, duty_name, duty_phone)")
        .eq("id", current["id"])
        .limit(1)
    )
    if rows:
        st.session_state.resident = rows[0]


def auth_page() -> None:
    css()
    st.markdown(
        f"""
        <section class="service-hero">
          <div class="service-title">{APP_NAME}</div>
          <div class="service-sub">{COMMUNITY} · 社区养老服务台</div>
        </section>
        """,
        unsafe_allow_html=True,
    )
    if st.session_state.get("register_success"):
        st.success(st.session_state.register_success)
        st.session_state.register_success = ""
    st.markdown('<div class="auth-card"><div class="ticket-title">居民登录</div><div class="ticket-sub">请输入手机号和社区认证码。</div></div>', unsafe_allow_html=True)
    phone = st.text_input("用户名（手机号）", key="login_phone")
    code = st.text_input("六位认证码", key="login_code", max_chars=6)
    col1, col2 = st.columns(2)
    if col1.button("登录", use_container_width=True):
        row = fetch_resident_by_login(phone.strip(), code.strip())
        if row:
            st.session_state.resident = row
            go("home")
        st.error("手机号或认证码不正确，或账号尚未通过审核。")
    if col2.button("注册", use_container_width=True):
        st.session_state.register_return_page = "login"
        go("register")


def register_page() -> None:
    css()
    back_target = "home" if resident() else st.session_state.get("register_return_page", "login")
    back_label = "返回首页" if back_target == "home" else "返回登录"
    if st.button(f"‹ {back_label}", key="register_back", use_container_width=False):
        go(back_target)
    st.markdown(
        f"""<div class="appbar"><div></div><div class="appbar-title">社区认证</div><div class="version">{APP_NAME}</div></div>""",
        unsafe_allow_html=True,
    )
    name = st.text_input("姓名")
    phone = st.text_input("联系电话")
    address = st.text_input("具体住址")
    invite = st.text_input("社区邀请码", value="")
    if st.button("提交审核", type="primary", use_container_width=True):
        if not name.strip() or not phone.strip() or not address.strip() or invite.strip() != COMMUNITY_INVITE_CODE:
            st.warning("请完整填写信息，并确认社区邀请码正确。")
            return
        existing = run_query(supabase_client().table("residents").select("*").eq("phone", phone.strip()).limit(1))
        payload = {
            "community_id": default_community_id(),
            "name": name.strip(),
            "phone": phone.strip(),
            "address": address.strip(),
            "status": "待审核",
            "health_profile": {
                "blood_pressure": "待补充",
                "medical_history": "待补充",
                "allergy": "待补充",
                "medication": "待补充",
                "emergency_contact": "待补充",
            },
        }
        if existing:
            run_query(supabase_client().table("residents").update(payload).eq("phone", phone.strip()))
        else:
            run_query(supabase_client().table("residents").insert(payload))
        st.session_state.register_success = "已提交社区审核。审核通过后，管理员会告知六位认证码。"
        if resident():
            go("home")
        go("login")


def service_phone() -> str:
    row = resident() or {}
    community = row.get("communities") or {}
    return community.get("service_phone") or COMMUNITY_PHONE


def community_name() -> str:
    row = resident() or {}
    community = row.get("communities") or {}
    return community.get("name") or COMMUNITY


def duty_info() -> tuple[str, str]:
    row = resident() or {}
    community = row.get("communities") or {}
    return community.get("duty_name") or "张主任", community.get("duty_phone") or COMMUNITY_PHONE


def normalize_wav_to_pcm16k(audio_bytes: bytes) -> bytes:
    with NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name
    try:
        with wave.open(tmp_path, "rb") as wav:
            channels = wav.getnchannels()
            sample_width = wav.getsampwidth()
            frame_rate = wav.getframerate()
            frames = wav.readframes(wav.getnframes())
        if sample_width == 1:
            audio = np.frombuffer(frames, dtype=np.uint8).astype(np.float32)
            audio = (audio - 128.0) / 128.0
        elif sample_width == 2:
            audio = np.frombuffer(frames, dtype="<i2").astype(np.float32) / 32768.0
        elif sample_width == 3:
            raw = np.frombuffer(frames, dtype=np.uint8).reshape(-1, 3)
            signed = raw[:, 0].astype(np.int32) | (raw[:, 1].astype(np.int32) << 8) | (raw[:, 2].astype(np.int32) << 16)
            signed = np.where(signed & 0x800000, signed - 0x1000000, signed)
            audio = signed.astype(np.float32) / 8388608.0
        elif sample_width == 4:
            audio = np.frombuffer(frames, dtype="<i4").astype(np.float32) / 2147483648.0
        else:
            raise RuntimeError("暂不支持当前录音格式。")
        if channels > 1:
            audio = audio.reshape(-1, channels).mean(axis=1)
        if frame_rate != 16000 and len(audio) > 1:
            old_x = np.linspace(0.0, 1.0, num=len(audio), endpoint=False)
            new_len = max(1, int(len(audio) * 16000 / frame_rate))
            new_x = np.linspace(0.0, 1.0, num=new_len, endpoint=False)
            audio = np.interp(new_x, old_x, audio).astype(np.float32)
        audio = np.clip(audio, -1.0, 1.0)
        return (audio * 32767.0).astype("<i2").tobytes()
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def xfyun_auth_url() -> str:
    api_key = secret("XFYUN_API_KEY")
    api_secret = secret("XFYUN_API_SECRET")
    if not api_key or not api_secret:
        raise RuntimeError("未配置讯飞 APIKey 或 APISecret。")
    host = "iat-api.xfyun.cn"
    path = "/v2/iat"
    date = email.utils.formatdate(usegmt=True)
    origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"
    signature = base64.b64encode(hmac.new(api_secret.encode(), origin.encode(), hashlib.sha256).digest()).decode()
    auth = base64.b64encode(
        f'api_key="{api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature}"'.encode()
    ).decode()
    return f"wss://{host}{path}?" + urlencode({"authorization": auth, "date": date, "host": host})


def parse_xfyun_words(payload: dict) -> str:
    words = []
    for item in payload.get("data", {}).get("result", {}).get("ws", []):
        for candidate in item.get("cw", []):
            words.append(candidate.get("w", ""))
    return "".join(words)


def recognize_with_xfyun(audio_bytes: bytes) -> str:
    app_id = secret("XFYUN_APP_ID")
    if not app_id:
        raise RuntimeError("未配置讯飞 APPID。")
    pcm = normalize_wav_to_pcm16k(audio_bytes)
    try:
        ws = websocket.create_connection(xfyun_auth_url(), sslopt={"cert_reqs": ssl.CERT_NONE}, timeout=20)
    except Exception as exc:
        raise RuntimeError(f"讯飞连接失败：{exc}") from exc
    try:
        result_parts = []
        chunk_size = 1280
        for index in range(0, len(pcm), chunk_size):
            chunk = pcm[index : index + chunk_size]
            status = 0 if index == 0 else 2 if index + chunk_size >= len(pcm) else 1
            frame = {
                "data": {
                    "status": status,
                    "format": "audio/L16;rate=16000",
                    "audio": base64.b64encode(chunk).decode(),
                    "encoding": "raw",
                }
            }
            if status == 0:
                frame["common"] = {"app_id": app_id}
                frame["business"] = {"language": "zh_cn", "domain": "iat", "accent": "mandarin", "vad_eos": 5000}
            ws.send(json.dumps(frame))
            response = json.loads(ws.recv())
            if response.get("code") != 0:
                raise RuntimeError(response.get("message", "讯飞识别失败"))
            result_parts.append(parse_xfyun_words(response))
            if status == 2:
                break
            time.sleep(0.04)
        return "".join(result_parts).strip()
    finally:
        ws.close()


def classify_voice_navigation(text: str) -> str:
    if "社区电话" in text or "联系社区" in text or "打电话" in text:
        return "dial"
    if any(w in text for w in ["楼道", "电梯", "路灯", "路面", "坡道", "反馈", "坏了", "堆物", "通道"]):
        return "社区反馈"
    if any(w in text for w in ["上门", "水龙头", "维修", "疏通", "保洁", "理发", "家电", "助浴", "测血压"]):
        return "上门事项"
    if any(w in text for w in ["医院", "药店", "银行", "散步", "外出", "陪诊", "复查", "接送"]):
        return "外出协助"
    return "生活需求"


def classify_ticket(note: str, request_type: str) -> tuple[str, str, str]:
    text = f"{request_type} {note}"
    volunteer = ["买药", "取药", "取物", "陪", "陪诊", "复查", "散步", "照看", "买菜"]
    provider = ["维修", "水电", "家政", "理发", "助浴", "疏通", "保洁", "家电"]
    if any(w in text for w in volunteer):
        return "邻里志愿者", "邻里优先，后台确认", "待社区分流"
    if any(w in text for w in provider) or request_type == "上门事项":
        return "认证服务商", "专业服务，推荐认证服务商", "待社区分流"
    return "社区工作人员", "社区先电话确认", "待接收"


def upload_bytes(bucket: str, path: str, data: bytes, content_type: str) -> str:
    supabase_client().storage.from_(bucket).upload(path, data, file_options={"content-type": content_type, "x-upsert": "true"})
    return supabase_client().storage.from_(bucket).get_public_url(path)


def voice_component(source: str) -> None:
    if source == "home":
        st.markdown(
            """
            <div class="voice-row" style="background:#128457;color:#fff;border:0;">
              <div class="voice-round" style="background:rgba(255,255,255,.16);color:#fff;">🎙</div>
              <div><strong>说出需求，进入填写</strong><small style="color:rgba(255,255,255,.78);">例如：我要买药、楼道有杂物、社区电话</small></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="voice-row">
              <div class="voice-round">🎙</div>
              <div><strong>语音填写说明</strong><small>录音会保存原声，后台工作人员可以回听</small></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    audio_file = st.audio_input("语音输入", key=f"audio_{source}", label_visibility="collapsed")
    if audio_file is None:
        return
    st.audio(audio_file)
    audio_file.seek(0)
    audio_bytes = audio_file.read()
    audio_hash = hashlib.sha1(audio_bytes).hexdigest()
    hash_key = f"recognized_audio_hash_{source}"
    if st.session_state.get(hash_key) == audio_hash:
        return
    st.session_state[hash_key] = audio_hash
    st.session_state.voice_audio_bytes = audio_bytes
    st.session_state.voice_audio_name = audio_file.name or "voice.wav"
    st.session_state.voice_audio_type = audio_file.type or "audio/wav"
    with st.spinner("正在识别语音..."):
        try:
            text = recognize_with_xfyun(audio_bytes)
        except Exception as exc:
            st.session_state.voice_error = f"语音识别暂未成功：{exc}"
            st.warning(st.session_state.voice_error)
            return
    if not text:
        st.warning("没有识别到有效文字，请再录一次。")
        return
    st.session_state.voice_text = text
    st.session_state.note = text
    st.session_state.voice_error = ""
    if source == "home":
        target = classify_voice_navigation(text)
        if target == "dial":
            st.session_state.dial_prompt = True
            st.rerun()
        go("request", request_type=target)
    st.rerun()


def fetch_tickets(resident_id: int) -> list[dict]:
    return run_query(supabase_client().table("tickets").select("*").eq("resident_id", resident_id).order("id", desc=True))


def fetch_ticket_images(ticket_id: int) -> list[dict]:
    return run_query(supabase_client().table("ticket_images").select("*").eq("ticket_id", ticket_id).order("id"))


def fetch_ticket_audio(ticket_id: int) -> list[dict]:
    return run_query(supabase_client().table("ticket_audio").select("*").eq("ticket_id", ticket_id).order("id"))


def fetch_service_providers(community_id: int | None = None) -> list[dict]:
    table = supabase_client().table("service_providers").select("*")
    if community_id is not None:
        table = table.eq("community_id", community_id).eq("status", "启用")
    try:
        return table.order("sort_order").order("certified", desc=True).order("id").execute().data
    except Exception as exc:
        if "sort_order" not in str(exc):
            db_error(exc)
        fallback = supabase_client().table("service_providers").select("*")
        if community_id is not None:
            fallback = fallback.eq("community_id", community_id).eq("status", "启用")
        return run_query(fallback.order("certified", desc=True).order("id"))


def page_home() -> None:
    row = resident()
    tickets = fetch_tickets(row["id"])
    active_count = len([item for item in tickets if item.get("status") != "已完成"])
    notices = ["便民理发服务：周三下午 2:00 在社区活动室", "医保咨询：周五上午 9:30 社区服务台开放", "找服务页面已公开社区认证资源"]
    notice_items = "".join(f'<span class="notice-item">{esc(item)}</span>' for item in notices + notices)
    st.markdown(
        f"""
        <section class="service-hero">
          <div class="service-hero-top">
            <div><div class="service-title">{esc(community_name())} · 服务台</div><div class="service-sub">邻里有事找帮忙，社区为您解决</div></div>
            <div style="display:flex;flex-direction:column;gap:8px;">
              <a class="call-pill" href="tel:{service_phone()}">{icon("phone")}联系社区</a>
              <span class="switch-pill">认证信息</span>
            </div>
          </div>
        </section>
        <div class="notice-card">{icon("speaker")}<div class="notice-window"><div class="notice-track"><strong>社区公告</strong>{notice_items}</div></div><span>›</span></div>
        """,
        unsafe_allow_html=True,
    )
    if st.session_state.dial_prompt:
        st.markdown(
            f'<div class="dial-card"><strong>社区服务电话</strong><div class="meta">点击后手机会打开拨号盘。</div><a class="dial-link" href="tel:{service_phone()}">拨打 {service_phone()}</a></div>',
            unsafe_allow_html=True,
        )
    if st.button("切换社区 / 认证信息", key="switch_community", use_container_width=True):
        st.session_state.register_return_page = "home"
        go("register")

    st.markdown('<div class="form-label">常用服务</div>', unsafe_allow_html=True)
    quick_items = list(REQUEST_TYPES.items()) + [(PHONEBOOK_SERVICE_NAME, {"detail": "像电话簿一样查看认证服务，一键拨号自助联系"})]
    for index in range(0, len(quick_items), 2):
        cols = st.columns(2)
        for col, (name, info) in zip(cols, quick_items[index : index + 2]):
            label = f"{name}\n{info['detail']}"
            if col.button(label, key=f"quick_{name}", use_container_width=True):
                if name == PHONEBOOK_SERVICE_NAME:
                    go("services")
                else:
                    go("request", request_type=name)
    st.markdown(
        f'<div class="auth-card"><div class="ticket-title">我的工单</div><div class="ticket-sub">查看进度与处理结果 · {active_count} 个进行中</div></div>',
        unsafe_allow_html=True,
    )
    if st.button("进入我的工单", key="home_tickets", use_container_width=True):
        go("tickets")
    voice_component("home")


def page_request() -> None:
    request_type = st.session_state.request_type if st.session_state.request_type in REQUEST_TYPES else "生活需求"
    info = REQUEST_TYPES[request_type]
    if st.button("‹ 返回首页", key="back_request", use_container_width=False):
        go("home")
    st.markdown(
        f"""
        <div class="appbar"><div></div><div class="appbar-title">提交需求</div><div class="version">{APP_NAME} V6.1</div></div>
        <div class="type-row">{icon(info["icon"])}<div><div class="type-title">{esc(request_type)}</div><div class="ticket-sub">{esc(info["detail"])}</div></div><span>›</span></div>
        """,
        unsafe_allow_html=True,
    )
    if st.session_state.voice_text and not st.session_state.note:
        st.session_state.note = st.session_state.voice_text
    if st.session_state.voice_error:
        st.warning(st.session_state.voice_error)
    note = st.text_area("需求描述", key="note", placeholder=info["placeholder"], height=130)
    st.markdown('<div class="form-label">语音说明 <span class="field-hint">（可选）</span></div>', unsafe_allow_html=True)
    voice_component("request")
    st.markdown('<div class="form-label">上传照片 <span class="field-hint">（可选，多张）</span></div>', unsafe_allow_html=True)
    files = st.file_uploader("上传照片", type=["png", "jpg", "jpeg"], accept_multiple_files=True, label_visibility="collapsed")
    if files:
        for file in files:
            st.image(file, use_container_width=True)
    urgency = st.radio("紧急程度", ["不急", "今天需要", "很紧急"], horizontal=True, index=1)
    callback = st.checkbox("需要社区工作人员电话联系我", value=urgency == "很紧急")
    can_submit = bool(note.strip() or st.session_state.voice_audio_bytes or files)
    if st.button("生成工单", type="primary", use_container_width=True, disabled=not can_submit):
        ticket_id = create_ticket(request_type, note.strip(), files or [], urgency, callback)
        st.session_state.last_ticket = ticket_id
        clear_request_state()
        go("success")
    st.markdown('<div class="privacy">您的信息将严格保密，仅用于服务安排</div>', unsafe_allow_html=True)


def clear_request_state() -> None:
    st.session_state.note = ""
    st.session_state.voice_text = ""
    st.session_state.voice_error = ""
    st.session_state.voice_audio_bytes = b""
    st.session_state.voice_audio_name = ""
    st.session_state.voice_audio_type = ""
    st.session_state.recognized_audio_hash_home = ""
    st.session_state.recognized_audio_hash_request = ""


def create_ticket(request_type: str, note: str, files: list, urgency: str, callback: bool) -> int:
    route, handler, status = classify_ticket(note, request_type)
    payload = {
        "resident_id": resident()["id"],
        "community_id": resident()["community_id"],
        "request_type": request_type,
        "content": note,
        "voice_text": st.session_state.voice_text,
        "urgency": urgency,
        "needs_callback": callback,
        "status": status,
        "route_type": route,
        "handler_note": handler,
    }
    ticket = run_query(supabase_client().table("tickets").insert(payload))[0]
    ticket_id = ticket["id"]
    audio_bytes = st.session_state.voice_audio_bytes
    if audio_bytes:
        suffix = Path(st.session_state.voice_audio_name or "voice.wav").suffix or ".wav"
        storage_path = f"tickets/{ticket_id}/audio/voice_{int(time.time())}{suffix}"
        audio_url = upload_bytes("audios", storage_path, audio_bytes, st.session_state.voice_audio_type or "audio/wav")
        run_query(
            supabase_client()
            .table("ticket_audio")
            .insert({"ticket_id": ticket_id, "audio_url": audio_url, "storage_path": storage_path, "transcript": st.session_state.voice_text})
        )
        run_query(supabase_client().table("tickets").update({"voice_url": audio_url, "voice_storage_path": storage_path}).eq("id", ticket_id))
    for idx, file in enumerate(files, start=1):
        file.seek(0)
        data = file.read()
        suffix = Path(file.name).suffix or ".jpg"
        storage_path = f"tickets/{ticket_id}/images/{idx}_{int(time.time())}{suffix}"
        image_url = upload_bytes("images", storage_path, data, file.type or "image/jpeg")
        run_query(supabase_client().table("ticket_images").insert({"ticket_id": ticket_id, "image_url": image_url, "storage_path": storage_path}))
    return int(ticket_id)


def page_success() -> None:
    if st.button("‹ 返回首页", key="back_success", use_container_width=False):
        go("home")
    st.markdown(
        f"""
        <div class="appbar"><div></div><div class="appbar-title">提交成功</div><div class="version">{APP_NAME}</div></div>
        <div class="auth-card"><div class="ticket-title">工单已生成</div><div class="ticket-sub">编号 #{st.session_state.last_ticket}，社区后台将按分流规则跟进。</div></div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("查看我的工单", use_container_width=True):
        go("tickets")


def ticket_card(row: dict) -> None:
    st.markdown(
        f"""
        <div class="record-card">
          <span class="badge">{esc(row.get("status"))}</span>
          <span class="badge orange">{esc(row.get("route_type") or "社区处理")}</span>
          <div class="ticket-title" style="margin-top:8px;">#{row["id"]} · {esc(row.get("request_type"))}</div>
          <div class="ticket-sub">{esc(row.get("content") or row.get("voice_text") or "未填写文字说明")}</div>
          <div class="meta">{esc(row.get("handler_note"))} · {esc(row.get("created_at"))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_tickets() -> None:
    if st.button("‹ 返回首页", key="back_tickets", use_container_width=False):
        go("home")
    st.markdown('<div class="appbar"><div></div><div class="appbar-title">我的工单</div><div class="version">V6.1</div></div>', unsafe_allow_html=True)
    rows = fetch_tickets(resident()["id"])
    if not rows:
        st.info("暂无工单。")
    for row in rows:
        ticket_card(row)


def page_services() -> None:
    if st.button("‹ 返回首页", key="back_services", use_container_width=False):
        go("home")
    st.markdown(
        """
        <div class="appbar"><div></div><div class="appbar-title">自己选服务</div><div class="version">V6.1</div></div>
        <div class="auth-card"><div class="ticket-title">社区服务电话簿</div><div class="ticket-sub">这里展示社区认证或备案的服务资源。您可以自己联系，也可以返回首页请社区帮您安排。</div></div>
        """,
        unsafe_allow_html=True,
    )
    rows = fetch_service_providers(resident()["community_id"])
    if not rows:
        st.info("暂无服务资源。")
        return
    categories = PHONEBOOK_CATEGORIES + sorted({(row.get("category") or "其他服务") for row in rows if (row.get("category") or "其他服务") not in PHONEBOOK_CATEGORIES})
    for category in categories:
        items = [row for row in rows if (row.get("category") or "其他服务") == category]
        if not items:
            continue
        st.markdown(f'<div class="form-label">{esc(category)}</div>', unsafe_allow_html=True)
        for item in items:
            badge = '<span class="badge">社区认证</span>' if item.get("certified") else '<span class="badge gray">社区备案</span>'
            organization = item.get("organization") or item.get("address") or "请电话确认"
            work_hours = item.get("work_hours") or "请电话确认"
            eta_note = item.get("eta_note") or "请电话确认"
            fee_note = item.get("fee_note") or "费用以电话沟通为准"
            coverage_note = item.get("coverage_note") or item.get("address") or "本社区及周边"
            st.markdown(
                f"""
                <div class="service-card">
                  <div class="provider-head">{badge}<span class="badge orange">{esc(category)}</span></div>
                  <div class="ticket-title" style="margin-top:8px;">{esc(item.get("name"))}</div>
                  <div class="ticket-sub">{esc(item.get("description") or "社区认证服务资源")}</div>
                  <div class="provider-lines">
                    <div><strong>电话</strong><span>{esc(item.get("phone") or "请联系社区")}</span></div>
                    <div><strong>机构</strong><span>{esc(organization)}</span></div>
                    <div><strong>时间</strong><span>{esc(work_hours)}</span></div>
                    <div><strong>到达</strong><span>{esc(eta_note)}</span></div>
                    <div><strong>费用</strong><span>{esc(fee_note)}</span></div>
                    <div><strong>范围</strong><span>{esc(coverage_note)}</span></div>
                  </div>
                  <a class="dial-link" href="tel:{esc(item.get("phone") or service_phone())}">拨打 {esc(item.get("phone") or service_phone())}</a>
                </div>
                """,
                unsafe_allow_html=True,
            )


def page_community() -> None:
    if st.button("‹ 返回首页", key="back_community", use_container_width=False):
        go("home")
    st.markdown('<div class="appbar"><div></div><div class="appbar-title">邻里圈</div><div class="version">V6.1</div></div>', unsafe_allow_html=True)
    rows = run_query(
        supabase_client()
        .table("activities")
        .select("*")
        .eq("community_id", resident()["community_id"])
        .eq("status", "已发布")
        .order("id", desc=True)
    )
    if not rows:
        st.info("暂无已发布活动。")
    for item in rows:
        st.markdown(
            f"""
            <div class="activity-card">
              <span class="badge">{esc(item.get("category") or "社区活动")}</span>
              <div class="ticket-title" style="margin-top:8px;">{esc(item.get("title"))}</div>
              <div class="ticket-sub">{esc(item.get("description"))}</div>
              <div class="meta">时间：{esc(item.get("event_time") or "待定")}<br>地址：{esc(item.get("location") or "待定")}<br>负责人：{esc(item.get("contact_person") or "社区服务台")} · {esc(item.get("contact_phone") or service_phone())}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def page_profile() -> None:
    refresh_resident()
    row = resident()
    health = row.get("health_profile") or {}
    duty_name, duty_phone = duty_info()
    if st.button("‹ 返回首页", key="back_profile", use_container_width=False):
        go("home")
    st.markdown(
        f"""
        <div class="appbar"><div></div><div class="appbar-title">我的</div><div class="version">V6.1</div></div>
        <div class="profile-card"><div class="avatar">{icon("user")}</div><div><div class="profile-name">{esc(row.get("name"))}</div><div class="ticket-sub">{esc(row.get("address"))}<br>电话：{esc(row.get("phone"))}</div></div></div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("切换用户", use_container_width=True):
        st.session_state.resident = None
        go("login")
    st.markdown('<div class="form-label">字体大小</div>', unsafe_allow_html=True)
    levels = list(FONT_LEVELS.keys())
    selected = st.radio("字体大小", levels, index=levels.index(st.session_state.font), horizontal=True, label_visibility="collapsed")
    if selected != st.session_state.font:
        st.session_state.font = selected
        st.rerun()
    st.markdown(
        f"""
        <div class="list-card">
          <div class="list-row">{icon("phone")}<div><div class="list-title">今日值班</div><div class="list-sub">{esc(duty_name)} · 电话：{esc(duty_phone)}</div></div><span>›</span></div>
          <div class="list-row">{icon("heart")}<div><div class="list-title">健康信息</div><div class="list-sub">血压：{esc(health.get("blood_pressure", "132/82 mmHg"))}<br>病史：{esc(health.get("medical_history", "高血压，膝关节退行性疼痛"))}<br>过敏：{esc(health.get("allergy", "青霉素过敏"))}<br>长期用药：{esc(health.get("medication", "降压药，每日一次"))}</div></div><span></span></div>
          <div class="list-row">{icon("ticket")}<div><div class="list-title">服务记录</div><div class="list-sub">查看历史服务、费用与酬劳记录</div></div><span>›</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("查看服务记录", key="profile_records", use_container_width=True):
        go("records")


def page_records() -> None:
    if st.button("‹ 返回我的", key="back_records", use_container_width=False):
        go("profile")
    st.markdown('<div class="appbar"><div></div><div class="appbar-title">服务记录</div><div class="version">V6.1</div></div>', unsafe_allow_html=True)
    rows = run_query(supabase_client().table("service_records").select("*").eq("resident_id", resident()["id"]).order("id", desc=True))
    if not rows:
        st.info("暂无服务记录。")
        return
    for item in rows:
        st.markdown(
            f"""
            <div class="record-card">
              <span class="badge">{esc(item.get("service_type"))}</span>
              <div class="ticket-title" style="margin-top:8px;">{esc(item.get("service_time"))}</div>
              <div class="ticket-sub">{esc(item.get("handler_name"))} · {esc(item.get("note"))}</div>
              <div class="meta">原费用：{esc(item.get("item_cost") or 0)} 元 · 酬劳：{esc(item.get("reward") or 0)} 元</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def bottom_nav() -> None:
    current = st.session_state.page
    items = [("home", "首页", "home"), ("community", "邻里圈", "users"), ("profile", "我的", "user")]
    cols = st.columns(3)
    for col, (page, label, _icon_name) in zip(cols, items):
        prefix = "● " if current == page else ""
        if col.button(f"{prefix}{label}", key=f"bottom_{page}", use_container_width=True):
            go(page)


def main() -> None:
    st.set_page_config(page_title="邻里帮 V6.1 云端版", page_icon="邻", layout="wide")
    init_state()
    st.session_state.app_mode = "user"
    if st.session_state.page == "register":
        register_page()
        return
    if not resident():
        auth_page()
        return
    css()
    page = st.session_state.page
    if page == "home":
        page_home()
    elif page == "request":
        page_request()
    elif page == "success":
        page_success()
    elif page == "tickets":
        page_tickets()
    elif page == "services":
        page_services()
    elif page == "community":
        page_community()
    elif page == "profile":
        page_profile()
    elif page == "records":
        page_records()
    elif page == "register":
        register_page()
    else:
        page_home()
    bottom_nav()


def require_admin_password() -> None:
    if st.session_state.get("admin_authed"):
        return
    css()
    st.markdown('<div class="auth-card"><div class="ticket-title">后台管理入口</div><div class="ticket-sub">请输入后台密码。</div></div>', unsafe_allow_html=True)
    password = st.text_input("后台密码", type="password")
    if st.button("进入后台", use_container_width=True):
        if password == secret("ADMIN_PASSWORD"):
            st.session_state.admin_authed = True
            st.rerun()
        st.error("密码不正确。")
    st.stop()


def generate_auth_code() -> str:
    return f"{random.randint(0, 999999):06d}"


def admin_residents_panel() -> None:
    rows = run_query(supabase_client().table("residents").select("*, communities(name)").order("id", desc=True))
    for item in rows:
        with st.container(border=True):
            code = item.get("auth_code") or "未生成"
            st.markdown(
                f"""
                <div class="review-head">
                  <div>
                    <div class="ticket-title">{esc(item.get("name"))} · {esc(item.get("phone"))}</div>
                    <div class="meta">{esc(item.get("address"))} · 状态：{esc(item.get("status"))}</div>
                  </div>
                  <div class="auth-code-box">
                    <div class="auth-code-label">认证码</div>
                    <span class="auth-code-value">{esc(code)}</span>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            cols = st.columns(3)
            if cols[0].button("通过并生成认证码", key=f"approve_{item['id']}"):
                code = item.get("auth_code") or generate_auth_code()
                run_query(supabase_client().table("residents").update({"status": "已通过", "auth_code": code}).eq("id", item["id"]))
                st.success(f"已通过，认证码：{code}")
                st.rerun()
            if cols[1].button("拒绝", key=f"reject_{item['id']}"):
                run_query(supabase_client().table("residents").update({"status": "已拒绝"}).eq("id", item["id"]))
                st.rerun()
            if cols[2].button("重置认证码", key=f"reset_code_{item['id']}"):
                code = generate_auth_code()
                run_query(supabase_client().table("residents").update({"auth_code": code}).eq("id", item["id"]))
                st.success(f"新认证码：{code}")
                st.rerun()


def admin_create_ticket_form() -> None:
    with st.expander("全人工兜底：后台代填工单"):
        residents = run_query(supabase_client().table("residents").select("*").eq("status", "已通过").order("id"))
        options = {f"{r['name']} · {r['phone']}": r for r in residents}
        if not options:
            st.info("暂无已通过居民。")
            return
        label = st.selectbox("选择居民", list(options.keys()))
        req = st.selectbox("需求类型", list(REQUEST_TYPES.keys()))
        content = st.text_area("需求说明")
        urgency = st.selectbox("紧急程度", ["不急", "今天需要", "很紧急"], index=1)
        if st.button("创建代填工单", use_container_width=True):
            r = options[label]
            route, handler, status = classify_ticket(content, req)
            run_query(
                supabase_client().table("tickets").insert(
                    {
                        "resident_id": r["id"],
                        "community_id": r["community_id"],
                        "request_type": req,
                        "content": content,
                        "urgency": urgency,
                        "status": status,
                        "route_type": route,
                        "handler_note": f"后台代填：{handler}",
                        "needs_callback": True,
                    }
                )
            )
            st.success("代填工单已创建。")
            st.rerun()


def admin_tickets_panel() -> None:
    admin_create_ticket_form()
    rows = run_query(
        supabase_client()
        .table("tickets")
        .select("*, residents(name, phone, address)")
        .order("id", desc=True)
    )
    providers = run_query(supabase_client().table("service_providers").select("*").eq("status", "启用").order("certified", desc=True))
    volunteers = run_query(supabase_client().table("volunteers").select("*").eq("status", "启用").order("id"))
    provider_options = ["暂不指定"] + [f"服务商：{p['name']} · {p['phone']}" for p in providers]
    volunteer_options = ["暂不指定"] + [f"志愿者：{v['name']} · {v['phone']}" for v in volunteers]
    for item in rows:
        with st.container(border=True):
            resident_row = item.get("residents") or {}
            st.subheader(f"#{item['id']} · {resident_row.get('name', '未知居民')} · {item.get('request_type')}")
            st.caption(f"{item.get('content') or item.get('voice_text') or '无文字'}")
            st.caption(f"推荐：{item.get('route_type')} · {item.get('handler_note')} · 当前：{item.get('status')}")
            if item.get("voice_url"):
                st.audio(item["voice_url"])
            status = st.selectbox("状态", TICKET_STATUSES, index=TICKET_STATUSES.index(item.get("status")) if item.get("status") in TICKET_STATUSES else 0, key=f"status_{item['id']}")
            candidates = volunteer_options if item.get("route_type") == "邻里志愿者" else provider_options
            assignee = st.selectbox("指派对象", candidates, key=f"assign_{item['id']}")
            cols = st.columns(2)
            if cols[0].button("保存处理", key=f"save_ticket_{item['id']}"):
                assigned_name = "" if assignee == "暂不指定" else assignee.split("：", 1)[1].split(" · ")[0]
                assigned_phone = "" if assignee == "暂不指定" else assignee.split(" · ")[-1]
                run_query(
                    supabase_client()
                    .table("tickets")
                    .update({"status": status, "assigned_name": assigned_name, "assigned_phone": assigned_phone})
                    .eq("id", item["id"])
                )
                st.success("已保存。")
                st.rerun()
            if cols[1].button("生成服务记录", key=f"record_{item['id']}"):
                run_query(
                    supabase_client()
                    .table("service_records")
                    .insert(
                        {
                            "resident_id": item["resident_id"],
                            "ticket_id": item["id"],
                            "service_time": now_text(),
                            "service_type": item.get("request_type"),
                            "handler_name": item.get("assigned_name") or item.get("route_type") or "社区工作人员",
                            "item_cost": 0,
                            "reward": 0,
                            "note": item.get("content") or item.get("voice_text") or "",
                        }
                    )
                )
                st.success("服务记录已生成。")


def admin_providers_panel() -> None:
    with st.expander("新增服务商"):
        name = st.text_input("名称", key="provider_name")
        category = st.text_input("类别", key="provider_category")
        phone = st.text_input("电话", key="provider_phone")
        organization = st.text_input("所属机构", key="provider_organization")
        work_hours = st.text_input("工作时间段", key="provider_work_hours", placeholder="例如：周一至周六 8:30-18:00")
        eta_note = st.text_input("预计到达时间", key="provider_eta_note", placeholder="例如：约 15-30 分钟")
        fee_note = st.text_input("费用/说明", key="provider_fee_note", placeholder="例如：上门前电话确认费用")
        coverage_note = st.text_input("地址或覆盖范围", key="provider_coverage_note", placeholder="例如：安靖社区及周边 3 公里")
        sort_order = st.number_input("排序", min_value=0, value=0, step=1, key="provider_sort_order")
        desc = st.text_area("说明", key="provider_desc")
        certified = st.checkbox("社区认证", value=True, key="provider_certified")
        if st.button("保存服务商", use_container_width=True):
            run_query(
                supabase_client()
                .table("service_providers")
                .insert(
                    {
                        "community_id": default_community_id(),
                        "name": name,
                        "category": category,
                        "phone": phone,
                        "organization": organization,
                        "work_hours": work_hours,
                        "eta_note": eta_note,
                        "description": desc,
                        "fee_note": fee_note,
                        "coverage_note": coverage_note,
                        "sort_order": int(sort_order),
                        "certified": certified,
                        "status": "启用",
                    }
                )
            )
            st.rerun()
    rows = fetch_service_providers()
    for item in rows:
        st.markdown(f'<div class="admin-card"><strong>{esc(item["name"])}</strong><div class="meta">{esc(item.get("category"))} · {esc(item.get("phone"))} · {esc(item.get("organization") or "未填机构")} · {esc(item.get("work_hours") or "未填时间")} · {"社区认证" if item.get("certified") else "社区备案"}</div></div>', unsafe_allow_html=True)


def admin_volunteers_panel() -> None:
    with st.expander("新增志愿者"):
        name = st.text_input("姓名", key="vol_name")
        phone = st.text_input("电话", key="vol_phone")
        skills = st.text_input("可协助事项", key="vol_skills")
        if st.button("保存志愿者", use_container_width=True):
            run_query(supabase_client().table("volunteers").insert({"community_id": default_community_id(), "name": name, "phone": phone, "skills": skills, "status": "启用"}))
            st.rerun()
    rows = run_query(supabase_client().table("volunteers").select("*").order("id"))
    for item in rows:
        st.markdown(f'<div class="admin-card"><strong>{esc(item["name"])}</strong><div class="meta">{esc(item.get("skills"))} · {esc(item.get("phone"))}</div></div>', unsafe_allow_html=True)


def admin_activities_panel() -> None:
    with st.expander("新增邻里圈活动"):
        title = st.text_input("标题")
        category = st.selectbox("类型", ["文体活动", "健康讲座", "社区通知", "便民服务", "志愿服务"])
        description = st.text_area("简介")
        event_time = st.text_input("时间")
        location = st.text_input("地址")
        contact_person = st.text_input("负责人")
        contact_phone = st.text_input("联系方式")
        status = st.selectbox("状态", ACTIVITY_STATUSES, index=0)
        if st.button("保存活动", use_container_width=True):
            run_query(
                supabase_client()
                .table("activities")
                .insert(
                    {
                        "community_id": default_community_id(),
                        "title": title,
                        "category": category,
                        "description": description,
                        "event_time": event_time,
                        "location": location,
                        "contact_person": contact_person,
                        "contact_phone": contact_phone,
                        "status": status,
                    }
                )
            )
            st.rerun()
    rows = run_query(supabase_client().table("activities").select("*").order("id", desc=True))
    for item in rows:
        with st.container(border=True):
            st.subheader(item.get("title"))
            status = st.selectbox("状态", ACTIVITY_STATUSES, index=ACTIVITY_STATUSES.index(item.get("status")) if item.get("status") in ACTIVITY_STATUSES else 0, key=f"activity_{item['id']}")
            if st.button("保存状态", key=f"save_activity_{item['id']}"):
                run_query(supabase_client().table("activities").update({"status": status}).eq("id", item["id"]))
                st.rerun()


def admin_records_panel() -> None:
    rows = run_query(supabase_client().table("service_records").select("*, residents(name, phone)").order("id", desc=True))
    for item in rows:
        r = item.get("residents") or {}
        st.markdown(f'<div class="admin-card"><strong>{esc(item.get("service_time"))} · {esc(item.get("service_type"))}</strong><div class="meta">{esc(r.get("name"))} · {esc(item.get("handler_name"))} · 原费用 {esc(item.get("item_cost"))} 元 · 酬劳 {esc(item.get("reward"))} 元</div></div>', unsafe_allow_html=True)


def admin_main() -> None:
    st.set_page_config(page_title="邻里帮后台 V6.1 云端版", page_icon="邻", layout="wide")
    init_state()
    st.session_state.app_mode = "admin"
    require_admin_password()
    css()
    st.markdown('<div class="appbar"><div></div><div class="appbar-title">后台管理</div><div class="version">V6.1 云端版</div></div>', unsafe_allow_html=True)
    tabs = st.tabs(["居民审核", "工单分流", "服务商", "志愿者", "邻里圈", "服务记录"])
    with tabs[0]:
        admin_residents_panel()
    with tabs[1]:
        admin_tickets_panel()
    with tabs[2]:
        admin_providers_panel()
    with tabs[3]:
        admin_volunteers_panel()
    with tabs[4]:
        admin_activities_panel()
    with tabs[5]:
        admin_records_panel()


if __name__ == "__main__":
    main()
