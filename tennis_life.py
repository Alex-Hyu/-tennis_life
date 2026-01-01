"""
🎾 TENNIS LIFE - 网球人生 v3.0
球友自助入组 + 匿名/实名吐槽
Mobile-optimized version
"""

import streamlit as st
import random
from datetime import datetime
import json

# ═══════════════════════════════════════════════════════════════════
# 🎨 PAGE CONFIG & CUSTOM STYLING
# ═══════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="🎾 Tennis Life",
    page_icon="🎾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;500;600;700&display=swap');
    
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0a1628 0%, #1a3a52 50%, #0d2137 100%);
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* ═══════════════════════════════════════════════════════════════
       TYPOGRAPHY
    ═══════════════════════════════════════════════════════════════ */
    
    .main-title {
        font-family: 'Orbitron', monospace;
        font-size: clamp(2rem, 8vw, 4rem);
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #00ff88 0%, #00d4ff 50%, #ff6b35 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0;
        letter-spacing: 0.05em;
        filter: drop-shadow(0 0 20px rgba(0, 255, 136, 0.4));
    }
    
    .subtitle {
        font-family: 'Rajdhani', sans-serif;
        font-size: clamp(1rem, 4vw, 1.5rem);
        text-align: center;
        color: #88ccff;
        margin-top: 5px;
        letter-spacing: 0.3em;
        text-transform: uppercase;
    }
    
    /* ═══════════════════════════════════════════════════════════════
       TAB STYLING - HIGH VISIBILITY
    ═══════════════════════════════════════════════════════════════ */
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        background: rgba(0, 0, 0, 0.3);
        border-radius: 15px;
        padding: 5px;
        flex-wrap: wrap;
        justify-content: center;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-family: 'Rajdhani', sans-serif !important;
        font-size: clamp(0.8rem, 2.8vw, 1rem) !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        background: transparent !important;
        border-radius: 10px !important;
        padding: 10px 12px !important;
        margin: 3px !important;
        white-space: nowrap;
        border: none !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.3), rgba(0, 255, 136, 0.2)) !important;
        color: #00ffcc !important;
        border: 1px solid rgba(0, 255, 136, 0.5) !important;
        text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(0, 212, 255, 0.15) !important;
        color: #00d4ff !important;
    }
    
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 20px;
    }
    
    /* ═══════════════════════════════════════════════════════════════
       CARDS
    ═══════════════════════════════════════════════════════════════ */
    
    .team-card {
        background: linear-gradient(145deg, rgba(0, 255, 136, 0.1), rgba(0, 212, 255, 0.05));
        border: 2px solid rgba(0, 255, 136, 0.3);
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 255, 136, 0.2);
    }
    
    .team-card-b {
        background: linear-gradient(145deg, rgba(255, 107, 53, 0.1), rgba(255, 193, 7, 0.05));
        border: 2px solid rgba(255, 107, 53, 0.3);
        box-shadow: 0 8px 32px rgba(255, 107, 53, 0.2);
    }
    
    /* Registration card - special highlight */
    .register-card {
        background: linear-gradient(145deg, rgba(0, 212, 255, 0.15), rgba(138, 43, 226, 0.1));
        border: 2px solid rgba(0, 212, 255, 0.5);
        border-radius: 20px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 10px 40px rgba(0, 212, 255, 0.3);
    }
    
    /* ═══════════════════════════════════════════════════════════════
       PLAYER NAMES
    ═══════════════════════════════════════════════════════════════ */
    
    .player-name {
        font-family: 'Orbitron', monospace;
        font-size: clamp(1.1rem, 4.5vw, 1.6rem);
        font-weight: 700;
        color: #00ff88;
        text-shadow: 0 0 15px rgba(0, 255, 136, 0.5);
        margin: 8px 0;
    }
    
    .player-name-b {
        color: #ff6b35;
        text-shadow: 0 0 15px rgba(255, 107, 53, 0.5);
    }
    
    .player-item {
        background: rgba(0, 0, 0, 0.2);
        border-radius: 10px;
        padding: 10px 15px;
        margin: 8px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-left: 4px solid #00ff88;
    }
    
    .player-item-b {
        border-left-color: #ff6b35;
    }
    
    .player-item-name {
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.2rem;
        font-weight: 600;
        color: #ffffff;
    }
    
    .player-item-rating {
        font-family: 'Orbitron', monospace;
        font-size: 0.9rem;
        color: #00d4ff;
        background: rgba(0, 212, 255, 0.2);
        padding: 4px 12px;
        border-radius: 20px;
    }
    
    /* Group labels */
    .group-label {
        font-family: 'Orbitron', monospace;
        font-size: clamp(1.5rem, 6vw, 2.5rem);
        font-weight: 900;
        display: inline-block;
        padding: 8px 20px;
        border-radius: 50px;
        margin-bottom: 15px;
    }
    
    .group-a {
        background: linear-gradient(135deg, #00ff88, #00d4ff);
        color: #0a1628;
        box-shadow: 0 0 25px rgba(0, 255, 136, 0.5);
    }
    
    .group-b {
        background: linear-gradient(135deg, #ff6b35, #ffc107);
        color: #0a1628;
        box-shadow: 0 0 25px rgba(255, 107, 53, 0.5);
    }
    
    /* ═══════════════════════════════════════════════════════════════
       VS BADGE
    ═══════════════════════════════════════════════════════════════ */
    
    .vs-badge {
        font-family: 'Orbitron', monospace;
        font-size: clamp(1.5rem, 6vw, 3rem);
        font-weight: 900;
        color: #fff;
        text-shadow: 0 0 30px rgba(255, 255, 255, 0.8);
        text-align: center;
        padding: 15px;
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }
    
    .team-label {
        font-family: 'Rajdhani', sans-serif;
        font-size: 0.9rem;
        color: #88ccff;
        text-transform: uppercase;
        letter-spacing: 0.2em;
        margin-bottom: 8px;
        text-align: center;
    }
    
    /* ═══════════════════════════════════════════════════════════════
       DATE & SECTION HEADERS
    ═══════════════════════════════════════════════════════════════ */
    
    .date-badge {
        font-family: 'Orbitron', monospace;
        font-size: clamp(0.9rem, 3vw, 1.2rem);
        color: #00d4ff;
        background: rgba(0, 212, 255, 0.1);
        padding: 8px 20px;
        border-radius: 50px;
        border: 1px solid rgba(0, 212, 255, 0.3);
        display: inline-block;
        margin-bottom: 15px;
    }
    
    .section-header {
        font-family: 'Orbitron', monospace;
        font-size: clamp(1.2rem, 5vw, 1.8rem);
        font-weight: 700;
        color: #00ffcc;
        border-bottom: 2px solid rgba(0, 255, 136, 0.4);
        padding-bottom: 10px;
        margin: 25px 0 15px 0;
        text-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
    }
    
    .sub-header {
        font-family: 'Rajdhani', sans-serif;
        font-size: clamp(1rem, 4vw, 1.3rem);
        font-weight: 600;
        color: #88ccff;
        margin: 15px 0 10px 0;
    }
    
    /* ═══════════════════════════════════════════════════════════════
       FORM ELEMENTS
    ═══════════════════════════════════════════════════════════════ */
    
    .stTextInput input {
        background: rgba(0, 0, 0, 0.4) !important;
        border: 2px solid rgba(0, 212, 255, 0.4) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1.1rem !important;
        padding: 12px !important;
        min-height: 50px !important;
    }
    
    .stTextInput input:focus {
        border-color: #00ff88 !important;
        box-shadow: 0 0 15px rgba(0, 255, 136, 0.3) !important;
    }
    
    .stTextInput input::placeholder {
        color: rgba(255, 255, 255, 0.5) !important;
    }
    
    .stTextArea textarea {
        background: rgba(0, 0, 0, 0.4) !important;
        border: 2px solid rgba(0, 212, 255, 0.4) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1.1rem !important;
        padding: 12px !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #00ff88 !important;
        box-shadow: 0 0 15px rgba(0, 255, 136, 0.3) !important;
    }
    
    .stSelectbox > div > div {
        background: rgba(0, 0, 0, 0.4) !important;
        border: 2px solid rgba(0, 212, 255, 0.4) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        min-height: 50px !important;
    }
    
    .stRadio > div {
        background: rgba(0, 0, 0, 0.2) !important;
        border-radius: 12px !important;
        padding: 10px !important;
    }
    
    .stRadio label {
        color: #ffffff !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 600 !important;
    }
    
    .stCheckbox label {
        color: #ffffff !important;
        font-family: 'Rajdhani', sans-serif !important;
    }
    
    .stTextInput label, .stTextArea label, .stSelectbox label {
        color: #ffffff !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════
       BUTTONS
    ═══════════════════════════════════════════════════════════════ */
    
    .stButton > button {
        font-family: 'Orbitron', monospace !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #00ff88, #00d4ff) !important;
        color: #0a1628 !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 15px 30px !important;
        font-size: clamp(0.9rem, 3.5vw, 1.1rem) !important;
        min-height: 55px !important;
        box-shadow: 0 5px 20px rgba(0, 255, 136, 0.4) !important;
        transition: all 0.3s ease !important;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0, 255, 136, 0.6) !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════
       EXPANDER
    ═══════════════════════════════════════════════════════════════ */
    
    .streamlit-expanderHeader {
        background: rgba(0, 0, 0, 0.3) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 600 !important;
    }
    
    .streamlit-expanderContent {
        background: rgba(0, 0, 0, 0.2) !important;
        border-radius: 0 0 10px 10px !important;
        color: #ffffff !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════
       ROAST CARDS
    ═══════════════════════════════════════════════════════════════ */
    
    .roast-card {
        background: linear-gradient(145deg, rgba(255, 107, 53, 0.1), rgba(255, 193, 7, 0.05));
        border: 1px solid rgba(255, 107, 53, 0.3);
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .roast-author {
        font-family: 'Orbitron', monospace;
        font-size: 0.9rem;
        color: #ff6b35;
        margin-bottom: 8px;
    }
    
    .roast-content {
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.1rem;
        color: #ffffff;
        line-height: 1.5;
    }
    
    .roast-time {
        font-family: 'Rajdhani', sans-serif;
        font-size: 0.8rem;
        color: #888;
        margin-top: 8px;
    }
    
    /* Anonymous badge */
    .anon-badge {
        background: rgba(138, 43, 226, 0.3);
        color: #da70d6;
        padding: 2px 10px;
        border-radius: 10px;
        font-size: 0.8rem;
        margin-left: 10px;
    }
    
    /* ═══════════════════════════════════════════════════════════════
       GENERAL TEXT
    ═══════════════════════════════════════════════════════════════ */
    
    p, span, div {
        color: #e0e0e0;
    }
    
    strong, b {
        color: #ffffff;
    }
    
    .stMarkdown {
        color: #e0e0e0 !important;
    }
    
    .stMarkdown p {
        color: #e0e0e0 !important;
    }
    
    .stMarkdown strong {
        color: #ffffff !important;
    }
    
    .net-positive {
        color: #00ff88 !important;
        font-weight: 700;
        text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
    }
    
    .net-negative {
        color: #ff6b35 !important;
        font-weight: 700;
        text-shadow: 0 0 10px rgba(255, 107, 53, 0.5);
    }
    
    .neon-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #00ff88, #00d4ff, #ff6b35, transparent);
        margin: 20px 0;
        border-radius: 2px;
    }
    
    /* ═══════════════════════════════════════════════════════════════
       SIDEBAR
    ═══════════════════════════════════════════════════════════════ */
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d2137 0%, #1a3a52 100%) !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4 {
        color: #00ffcc !important;
    }
    
    .stAlert {
        background: rgba(0, 0, 0, 0.3) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
    }
    
    .stDownloadButton > button {
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 600 !important;
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.3), rgba(0, 255, 136, 0.2)) !important;
        color: #ffffff !important;
        border: 2px solid rgba(0, 212, 255, 0.5) !important;
        border-radius: 12px !important;
        min-height: 50px !important;
    }
    
    .tennis-ball {
        font-size: 1.5rem;
        animation: bounce 0.6s ease-in-out infinite;
        display: inline-block;
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }
    
    /* ═══════════════════════════════════════════════════════════════
       MOBILE ADJUSTMENTS
    ═══════════════════════════════════════════════════════════════ */
    
    @media (max-width: 768px) {
        .stTabs [data-baseweb="tab-list"] {
            flex-direction: row;
            flex-wrap: wrap;
        }
        
        .stTabs [data-baseweb="tab"] {
            flex: 1 1 30%;
            text-align: center;
            padding: 10px 6px !important;
            font-size: 0.75rem !important;
        }
        
        .team-card, .register-card {
            padding: 12px;
        }
        
        .stButton > button {
            padding: 12px 20px !important;
        }
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# 📊 SESSION STATE
# ═══════════════════════════════════════════════════════════════════

if 'players' not in st.session_state:
    st.session_state.players = []

if 'group_a' not in st.session_state:
    st.session_state.group_a = []

if 'group_b' not in st.session_state:
    st.session_state.group_b = []

if 'current_pairing' not in st.session_state:
    st.session_state.current_pairing = None

if 'match_records' not in st.session_state:
    st.session_state.match_records = []

if 'reviews' not in st.session_state:
    st.session_state.reviews = []


# ═══════════════════════════════════════════════════════════════════
# 🎾 HEADER
# ═══════════════════════════════════════════════════════════════════

st.markdown('<h1 class="main-title">🎾 TENNIS LIFE</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">网球人生 · 双打配对</p>', unsafe_allow_html=True)
st.markdown(f'<div style="text-align: center;"><span class="date-badge">📅 {datetime.now().strftime("%Y年%m月%d日")}</span></div>', unsafe_allow_html=True)
st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# 📝 SIDEBAR - ADMIN FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("### ⚙️ 管理员功能")
    st.markdown("---")
    
    st.markdown("#### 📊 当前统计")
    st.markdown(f"**A组**: {len(st.session_state.group_a)} 人")
    st.markdown(f"**B组**: {len(st.session_state.group_b)} 人")
    st.markdown(f"**战绩**: {len(st.session_state.match_records)} 场")
    st.markdown(f"**吐槽**: {len(st.session_state.reviews)} 条")
    
    st.markdown("---")
    
    st.markdown("#### ⚡ 批量导入球员")
    preset_names = st.text_area("每行: 姓名,评分", 
                                 placeholder="张三,4.0\n李四,3.5",
                                 height=100,
                                 key="admin_batch")
    
    if st.button("📥 批量导入", use_container_width=True, key="admin_import"):
        if preset_names.strip():
            lines = preset_names.strip().split('\n')
            added = 0
            for line in lines:
                if ',' in line:
                    parts = line.split(',')
                    name = parts[0].strip()
                    try:
                        rating = float(parts[1].strip())
                        # Check duplicate
                        existing = [p["name"] for p in st.session_state.players]
                        if name not in existing:
                            player = {
                                "name": name,
                                "rating": rating,
                                "group": "A" if rating >= 4.0 else "B"
                            }
                            st.session_state.players.append(player)
                            if player["group"] == "A":
                                st.session_state.group_a.append(player)
                            else:
                                st.session_state.group_b.append(player)
                            added += 1
                    except:
                        pass
            if added > 0:
                st.success(f"✅ 导入 {added} 人")
                st.rerun()
    
    st.markdown("---")
    
    if st.button("🗑️ 清空所有球员", use_container_width=True):
        st.session_state.players = []
        st.session_state.group_a = []
        st.session_state.group_b = []
        st.session_state.current_pairing = None
        st.rerun()
    
    if st.button("🗑️ 清空所有记录", use_container_width=True):
        st.session_state.match_records = []
        st.session_state.reviews = []
        st.success("✅ 已清空")
        st.rerun()


# ═══════════════════════════════════════════════════════════════════
# 👥 MAIN CONTENT TABS
# ═══════════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4, tab5 = st.tabs(["✍️ 自评入组", "🏆 分组抽签", "📊 战绩记录", "😤 复盘吐槽", "📋 历史记录"])


# ═══════════════════════════════════════════════════════════════════
# TAB 1: 球友自评入组
# ═══════════════════════════════════════════════════════════════════

with tab1:
    st.markdown('<p class="section-header">✍️ 球友自评入组</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="register-card">
        <p style="color: #00ffcc; font-size: 1.1rem; margin-bottom: 15px;">
            👋 欢迎加入今日网球活动！请填写你的信息：
        </p>
        <p style="color: #88ccff; font-size: 0.95rem;">
            • <strong>A组</strong>：自评 4.0 及以上 → 高手区<br>
            • <strong>B组</strong>：自评 3.5+ → 进阶区
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col_reg1, col_reg2 = st.columns([2, 1])
    
    with col_reg1:
        register_name = st.text_input("📝 你的名字", placeholder="输入你的名字或昵称", key="reg_name")
    
    with col_reg2:
        register_rating = st.selectbox("⭐ 自评水平", 
                                        ["4.5 (高手)", "4.0 (高手)", "3.5 (进阶)", "3.0 (进阶)", "2.5 (入门)"], 
                                        key="reg_rating")
    
    if st.button("🎾 加入今日活动", use_container_width=True, key="reg_submit"):
        if register_name.strip():
            # Extract rating number
            rating = float(register_rating.split()[0])
            
            # Check duplicate
            existing_names = [p["name"].lower() for p in st.session_state.players]
            if register_name.strip().lower() in existing_names:
                st.warning(f"⚠️ '{register_name}' 已经报名了！")
            else:
                player = {
                    "name": register_name.strip(),
                    "rating": rating,
                    "group": "A" if rating >= 4.0 else "B"
                }
                st.session_state.players.append(player)
                if player["group"] == "A":
                    st.session_state.group_a.append(player)
                else:
                    st.session_state.group_b.append(player)
                
                group_name = "A组 (高手区)" if player["group"] == "A" else "B组 (进阶区)"
                st.success(f"✅ {register_name} 已加入 {group_name}！")
                st.balloons()
                st.rerun()
        else:
            st.warning("⚠️ 请输入你的名字")
    
    st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)
    
    # Show current groups
    st.markdown('<p class="sub-header">📋 今日报名名单</p>', unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown('<div class="team-card">', unsafe_allow_html=True)
        st.markdown('<span class="group-label group-a">A组</span>', unsafe_allow_html=True)
        st.markdown("**⭐ 4.0+ 高手区**")
        
        if st.session_state.group_a:
            for player in st.session_state.group_a:
                st.markdown(f"""
                <div class="player-item">
                    <span class="player-item-name">{player['name']}</span>
                    <span class="player-item-rating">⭐ {player['rating']}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("*暂无球员*")
        
        st.markdown(f"**共 {len(st.session_state.group_a)} 人**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_b:
        st.markdown('<div class="team-card team-card-b">', unsafe_allow_html=True)
        st.markdown('<span class="group-label group-b">B组</span>', unsafe_allow_html=True)
        st.markdown("**⭐ 3.5+ 进阶区**")
        
        if st.session_state.group_b:
            for player in st.session_state.group_b:
                st.markdown(f"""
                <div class="player-item player-item-b">
                    <span class="player-item-name">{player['name']}</span>
                    <span class="player-item-rating">⭐ {player['rating']}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("*暂无球员*")
        
        st.markdown(f"**共 {len(st.session_state.group_b)} 人**")
        st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# TAB 2: 分组抽签
# ═══════════════════════════════════════════════════════════════════

with tab2:
    st.markdown('<p class="section-header">🎲 双打抽签</p>', unsafe_allow_html=True)
    
    # Show group counts
    col_count_a, col_count_b = st.columns(2)
    with col_count_a:
        st.markdown(f"**A组**: {len(st.session_state.group_a)} 人")
    with col_count_b:
        st.markdown(f"**B组**: {len(st.session_state.group_b)} 人")
    
    st.markdown("---")
    
    if st.button("🎾 开始抽签！", use_container_width=True, key="draw_btn"):
        total_players = len(st.session_state.group_a) + len(st.session_state.group_b)
        
        if total_players >= 4:
            all_players = st.session_state.group_a + st.session_state.group_b
            random.shuffle(all_players)
            
            # Try to mix A and B players
            if len(st.session_state.group_a) >= 2 and len(st.session_state.group_b) >= 2:
                # Mix: 1A+1B vs 1A+1B
                a_players = st.session_state.group_a.copy()
                b_players = st.session_state.group_b.copy()
                random.shuffle(a_players)
                random.shuffle(b_players)
                
                team1 = [a_players[0], b_players[0]]
                team2 = [a_players[1], b_players[1]]
            else:
                # Just random pairs
                team1 = all_players[:2]
                team2 = all_players[2:4]
            
            st.session_state.current_pairing = {
                "team1": team1,
                "team2": team2,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
            st.rerun()
        else:
            st.warning("⚠️ 至少需要4名球员才能抽签")
    
    # Display current pairing
    if st.session_state.current_pairing:
        pairing = st.session_state.current_pairing
        
        st.markdown("---")
        st.markdown("### 🏆 本轮对阵")
        
        col_t1, col_vs, col_t2 = st.columns([2, 1, 2])
        
        with col_t1:
            st.markdown('<div class="team-card">', unsafe_allow_html=True)
            st.markdown('<p class="team-label">TEAM 1</p>', unsafe_allow_html=True)
            for p in pairing["team1"]:
                group_class = "" if p.get("group") == "A" else " player-name-b"
                st.markdown(f'<p class="player-name{group_class}">{p["name"]}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_vs:
            st.markdown('<div class="vs-badge">⚡VS⚡</div>', unsafe_allow_html=True)
        
        with col_t2:
            st.markdown('<div class="team-card team-card-b">', unsafe_allow_html=True)
            st.markdown('<p class="team-label">TEAM 2</p>', unsafe_allow_html=True)
            for p in pairing["team2"]:
                group_class = "" if p.get("group") == "A" else " player-name-b"
                st.markdown(f'<p class="player-name{group_class}">{p["name"]}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Re-draw button
        if st.button("🔄 重新抽签", use_container_width=True, key="redraw_btn"):
            st.session_state.current_pairing = None
            st.rerun()


# ═══════════════════════════════════════════════════════════════════
# TAB 3: 战绩记录
# ═══════════════════════════════════════════════════════════════════

with tab3:
    st.markdown('<p class="section-header">📊 战绩记录</p>', unsafe_allow_html=True)
    
    if st.session_state.current_pairing:
        pairing = st.session_state.current_pairing
        
        st.markdown(f"**🆚 对阵**: {pairing['team1'][0]['name']} & {pairing['team1'][1]['name']} vs {pairing['team2'][0]['name']} & {pairing['team2'][1]['name']}")
        
        st.markdown("---")
        st.markdown("#### 📝 输入比分")
        
        col_s1, col_colon, col_s2 = st.columns([2, 1, 2])
        
        with col_s1:
            score1 = st.text_input("Team 1 得分", placeholder="7", key="score1_input")
        
        with col_colon:
            st.markdown("<div style='text-align: center; font-size: 2.5rem; color: #fff; padding-top: 25px;'>:</div>", unsafe_allow_html=True)
        
        with col_s2:
            score2 = st.text_input("Team 2 得分", placeholder="6", key="score2_input")
        
        if score1 and score2:
            try:
                s1 = int(score1)
                s2 = int(score2)
                net_diff = s1 - s2
                
                st.markdown("---")
                
                winner_names = pairing['team1'] if s1 > s2 else (pairing['team2'] if s2 > s1 else None)
                
                if winner_names:
                    st.markdown(f"**🏆 获胜**: {winner_names[0]['name']} & {winner_names[1]['name']}")
                else:
                    st.markdown("**🏆 结果**: 平局")
                
                st.markdown(f"**📊 比分**: {s1} : {s2}")
                
                net_class = "net-positive" if net_diff > 0 else ("net-negative" if net_diff < 0 else "")
                sign = "+" if net_diff > 0 else ""
                st.markdown(f"**净胜分 (T1)**: <span class='{net_class}'>{sign}{net_diff}</span>", unsafe_allow_html=True)
                
                if st.button("💾 保存战绩", use_container_width=True, key="save_score"):
                    record = {
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "team1": [p["name"] for p in pairing["team1"]],
                        "team2": [p["name"] for p in pairing["team2"]],
                        "score1": s1,
                        "score2": s2,
                        "net_diff": net_diff,
                        "winner": "team1" if s1 > s2 else ("team2" if s2 > s1 else "tie")
                    }
                    st.session_state.match_records.append(record)
                    st.success("✅ 战绩已保存！")
                    st.balloons()
                    
            except ValueError:
                st.warning("⚠️ 请输入有效数字")
    else:
        st.info("💡 请先在「分组抽签」进行抽签")


# ═══════════════════════════════════════════════════════════════════
# TAB 4: 复盘吐槽 (实名/匿名)
# ═══════════════════════════════════════════════════════════════════

with tab4:
    st.markdown('<p class="section-header">😤 复盘吐槽</p>', unsafe_allow_html=True)
    
    # Get list of registered players for selection
    all_player_names = [p["name"] for p in st.session_state.players]
    
    st.markdown("#### 👤 你是谁？")
    
    col_author, col_anon = st.columns([3, 1])
    
    with col_author:
        if all_player_names:
            author_options = ["选择你的名字..."] + all_player_names + ["其他 (手动输入)"]
            selected_author = st.selectbox("选择身份", author_options, key="roast_author_select", label_visibility="collapsed")
            
            if selected_author == "其他 (手动输入)":
                author_name = st.text_input("输入你的名字", placeholder="你的名字", key="roast_author_input")
            elif selected_author == "选择你的名字...":
                author_name = ""
            else:
                author_name = selected_author
        else:
            author_name = st.text_input("输入你的名字", placeholder="你的名字", key="roast_author_input_only")
    
    with col_anon:
        is_anonymous = st.checkbox("🎭 匿名", key="is_anon")
    
    st.markdown("---")
    
    # Roast type selection
    roast_type = st.radio(
        "选择吐槽类型",
        ["🎾 比赛复盘", "😤 吐槽搭档", "🤦 吐槽自己"],
        horizontal=True,
        key="roast_type"
    )
    
    # Target selection for partner roast
    target_name = ""
    if roast_type == "😤 吐槽搭档":
        st.markdown("#### 🎯 吐槽谁？")
        if all_player_names:
            target_options = ["选择要吐槽的搭档..."] + all_player_names
            target_name = st.selectbox("选择搭档", target_options, key="roast_target", label_visibility="collapsed")
            if target_name == "选择要吐槽的搭档...":
                target_name = ""
        else:
            target_name = st.text_input("搭档名字", placeholder="输入搭档名字", key="roast_target_input")
    
    # Content
    st.markdown("#### 💬 内容")
    
    if roast_type == "🎾 比赛复盘":
        placeholder_text = "今天比赛发挥得怎么样？有什么战术心得？"
    elif roast_type == "😤 吐槽搭档":
        placeholder_text = "搭档今天网前太保守了，该上的球不上..."
    else:
        placeholder_text = "今天二发太菜了，关键分心态崩了..."
    
    roast_content = st.text_area(
        "写下你的想法",
        placeholder=placeholder_text,
        height=120,
        key="roast_content",
        label_visibility="collapsed"
    )
    
    if st.button("📤 发布", use_container_width=True, key="submit_roast"):
        if not roast_content.strip():
            st.warning("⚠️ 请填写内容")
        elif not is_anonymous and not author_name:
            st.warning("⚠️ 请选择你的名字或勾选匿名")
        elif roast_type == "😤 吐槽搭档" and not target_name:
            st.warning("⚠️ 请选择要吐槽的搭档")
        else:
            review = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "author": "匿名球友" if is_anonymous else author_name,
                "is_anonymous": is_anonymous,
                "type": roast_type,
                "target": target_name if roast_type == "😤 吐槽搭档" else "",
                "content": roast_content
            }
            st.session_state.reviews.append(review)
            st.success("✅ 发布成功！")
            st.rerun()
    
    st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)
    
    # Display recent roasts
    st.markdown("#### 📜 最新吐槽")
    
    if st.session_state.reviews:
        for review in reversed(st.session_state.reviews[-10:]):  # Show last 10
            type_emoji = "🎾" if review["type"] == "🎾 比赛复盘" else ("😤" if review["type"] == "😤 吐槽搭档" else "🤦")
            anon_badge = '<span class="anon-badge">匿名</span>' if review.get("is_anonymous") else ""
            
            target_text = f" → <strong>{review['target']}</strong>" if review.get("target") else ""
            
            st.markdown(f"""
            <div class="roast-card">
                <div class="roast-author">
                    {type_emoji} {review['author']}{anon_badge}{target_text}
                </div>
                <div class="roast-content">{review['content']}</div>
                <div class="roast-time">🕐 {review['date']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("💡 暂无吐槽，来发第一条吧！")


# ═══════════════════════════════════════════════════════════════════
# TAB 5: 历史记录
# ═══════════════════════════════════════════════════════════════════

with tab5:
    st.markdown('<p class="section-header">📋 历史记录</p>', unsafe_allow_html=True)
    
    # Match records
    st.markdown("#### 🏆 战绩历史")
    
    if st.session_state.match_records:
        for i, record in enumerate(reversed(st.session_state.match_records)):
            with st.expander(f"📅 {record['date']} | {record['score1']}:{record['score2']}", expanded=(i==0)):
                st.markdown(f"**Team 1**: {' & '.join(record['team1'])} → {record['score1']}分")
                st.markdown(f"**Team 2**: {' & '.join(record['team2'])} → {record['score2']}分")
                
                net_class = "net-positive" if record['net_diff'] > 0 else ("net-negative" if record['net_diff'] < 0 else "")
                sign = "+" if record['net_diff'] > 0 else ""
                st.markdown(f"**净胜分**: <span class='{net_class}'>{sign}{record['net_diff']}</span>", unsafe_allow_html=True)
                
                winner_text = "Team 1 🏆" if record['winner'] == 'team1' else ("Team 2 🏆" if record['winner'] == 'team2' else "平局")
                st.markdown(f"**结果**: {winner_text}")
    else:
        st.info("💡 暂无战绩")
    
    st.markdown("---")
    
    # All reviews
    st.markdown("#### 📝 吐槽历史")
    
    if st.session_state.reviews:
        for i, review in enumerate(reversed(st.session_state.reviews)):
            with st.expander(f"📅 {review['date']} - {review['type']}", expanded=(i==0)):
                st.markdown(f"**作者**: {review['author']}")
                if review.get("target"):
                    st.markdown(f"**吐槽对象**: {review['target']}")
                st.markdown(f"**内容**: {review['content']}")
    else:
        st.info("💡 暂无复盘")
    
    st.markdown("---")
    
    # Export
    if st.session_state.match_records or st.session_state.reviews:
        export_data = {
            "players": st.session_state.players,
            "match_records": st.session_state.match_records,
            "reviews": st.session_state.reviews,
            "export_date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        st.download_button(
            "📥 导出所有数据",
            data=json.dumps(export_data, ensure_ascii=False, indent=2),
            file_name=f"tennis_life_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )


# ═══════════════════════════════════════════════════════════════════
# 🎾 FOOTER
# ═══════════════════════════════════════════════════════════════════

st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; padding: 15px; color: #88ccff; font-family: 'Rajdhani', sans-serif;">
    <span class="tennis-ball">🎾</span>
    <span style="margin: 0 15px; color: #ffffff;">TENNIS LIFE v3.0</span>
    <span class="tennis-ball">🎾</span>
</div>
""", unsafe_allow_html=True)
