"""
🎾 TENNIS LIFE - 网球人生 v5.0
Google Sheets 持久化存储版本
Mobile-optimized
"""

import streamlit as st
import random
from datetime import datetime, date
import json

# ═══════════════════════════════════════════════════════════════════
# 📊 GOOGLE SHEETS SETUP
# ═══════════════════════════════════════════════════════════════════

try:
    from google.oauth2.service_account import Credentials
    import gspread
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

# Google Sheets 配置
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

@st.cache_resource
def get_google_sheet():
    """连接 Google Sheets"""
    if not GSPREAD_AVAILABLE:
        return None
    
    try:
        # 从 Streamlit Secrets 读取凭证
        creds_dict = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        client = gspread.authorize(creds)
        
        # 打开指定的 Google Sheet
        sheet_url = st.secrets["sheet_url"]
        spreadsheet = client.open_by_url(sheet_url)
        return spreadsheet
    except Exception as e:
        st.error(f"连接 Google Sheets 失败: {e}")
        return None

def init_worksheets(spreadsheet):
    """初始化工作表"""
    if not spreadsheet:
        return None, None, None
    
    try:
        # 获取或创建工作表
        worksheet_names = [ws.title for ws in spreadsheet.worksheets()]
        
        # Players 表
        if "players" not in worksheet_names:
            players_ws = spreadsheet.add_worksheet(title="players", rows=1000, cols=10)
            players_ws.append_row(["name", "rating", "group", "created_at"])
        else:
            players_ws = spreadsheet.worksheet("players")
        
        # Match Records 表
        if "matches" not in worksheet_names:
            matches_ws = spreadsheet.add_worksheet(title="matches", rows=1000, cols=15)
            matches_ws.append_row(["date", "team1", "team2", "score1", "score2", "net_diff", "winner", "created_at"])
        else:
            matches_ws = spreadsheet.worksheet("matches")
        
        # Reviews 表
        if "reviews" not in worksheet_names:
            reviews_ws = spreadsheet.add_worksheet(title="reviews", rows=1000, cols=10)
            reviews_ws.append_row(["date", "author", "is_anonymous", "type", "target", "content"])
        else:
            reviews_ws = spreadsheet.worksheet("reviews")
        
        return players_ws, matches_ws, reviews_ws
    except Exception as e:
        st.error(f"初始化工作表失败: {e}")
        return None, None, None

def load_players(ws):
    """从 Google Sheets 加载球员"""
    if not ws:
        return [], [], []
    try:
        records = ws.get_all_records()
        players = []
        group_a = []
        group_b = []
        for r in records:
            if r.get('name'):
                player = {
                    "name": r['name'],
                    "rating": float(r['rating']) if r.get('rating') else 3.5,
                    "group": r.get('group', 'B')
                }
                players.append(player)
                if player['group'] == 'A':
                    group_a.append(player)
                else:
                    group_b.append(player)
        return players, group_a, group_b
    except:
        return [], [], []

def add_player(ws, player):
    """添加球员到 Google Sheets"""
    if not ws:
        return False
    try:
        ws.append_row([
            player['name'],
            player['rating'],
            player['group'],
            datetime.now().strftime("%Y-%m-%d %H:%M")
        ])
        return True
    except:
        return False

def load_matches(ws):
    """从 Google Sheets 加载战绩"""
    if not ws:
        return []
    try:
        records = ws.get_all_records()
        matches = []
        for r in records:
            if r.get('date'):
                match = {
                    "date": r['date'],
                    "team1": r['team1'].split(',') if r.get('team1') else [],
                    "team2": r['team2'].split(',') if r.get('team2') else [],
                    "score1": int(r['score1']) if r.get('score1') else 0,
                    "score2": int(r['score2']) if r.get('score2') else 0,
                    "net_diff": int(r['net_diff']) if r.get('net_diff') else 0,
                    "winner": r.get('winner', 'tie')
                }
                matches.append(match)
        return matches
    except:
        return []

def add_match(ws, match):
    """添加战绩到 Google Sheets"""
    if not ws:
        return False
    try:
        ws.append_row([
            match['date'],
            ','.join(match['team1']),
            ','.join(match['team2']),
            match['score1'],
            match['score2'],
            match['net_diff'],
            match['winner'],
            datetime.now().strftime("%Y-%m-%d %H:%M")
        ])
        return True
    except:
        return False

def load_reviews(ws):
    """从 Google Sheets 加载吐槽"""
    if not ws:
        return []
    try:
        records = ws.get_all_records()
        reviews = []
        for r in records:
            if r.get('content'):
                review = {
                    "date": r.get('date', ''),
                    "author": r.get('author', '匿名'),
                    "is_anonymous": r.get('is_anonymous', 'FALSE') == 'TRUE',
                    "type": r.get('type', ''),
                    "target": r.get('target', ''),
                    "content": r.get('content', '')
                }
                reviews.append(review)
        return reviews
    except:
        return []

def add_review(ws, review):
    """添加吐槽到 Google Sheets"""
    if not ws:
        return False
    try:
        ws.append_row([
            review['date'],
            review['author'],
            'TRUE' if review['is_anonymous'] else 'FALSE',
            review['type'],
            review['target'],
            review['content']
        ])
        return True
    except:
        return False


# ═══════════════════════════════════════════════════════════════════
# 🎨 PAGE CONFIG & STYLING
# ═══════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="🎾 Tennis Life",
    page_icon="🎾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0a1628 0%, #1a3a52 50%, #0d2137 100%);
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
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
        filter: drop-shadow(0 0 20px rgba(0, 255, 136, 0.4));
    }
    
    .subtitle {
        font-family: 'Rajdhani', sans-serif;
        font-size: clamp(1rem, 4vw, 1.5rem);
        text-align: center;
        color: #88ccff;
        margin-top: 5px;
        letter-spacing: 0.3em;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: rgba(0, 0, 0, 0.3);
        border-radius: 15px;
        padding: 5px;
        flex-wrap: wrap;
        justify-content: center;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-family: 'Rajdhani', sans-serif !important;
        font-size: clamp(0.7rem, 2.5vw, 0.9rem) !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        background: transparent !important;
        border-radius: 10px !important;
        padding: 8px 8px !important;
        margin: 2px !important;
        border: none !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.3), rgba(0, 255, 136, 0.2)) !important;
        color: #00ffcc !important;
        border: 1px solid rgba(0, 255, 136, 0.5) !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(0, 212, 255, 0.15) !important;
    }
    
    .team-card {
        background: linear-gradient(145deg, rgba(0, 255, 136, 0.1), rgba(0, 212, 255, 0.05));
        border: 2px solid rgba(0, 255, 136, 0.3);
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 8px 32px rgba(0, 255, 136, 0.2);
    }
    
    .team-card-b {
        background: linear-gradient(145deg, rgba(255, 107, 53, 0.1), rgba(255, 193, 7, 0.05));
        border: 2px solid rgba(255, 107, 53, 0.3);
        box-shadow: 0 8px 32px rgba(255, 107, 53, 0.2);
    }
    
    .register-card {
        background: linear-gradient(145deg, rgba(0, 212, 255, 0.15), rgba(138, 43, 226, 0.1));
        border: 2px solid rgba(0, 212, 255, 0.5);
        border-radius: 20px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 10px 40px rgba(0, 212, 255, 0.3);
    }
    
    .player-name {
        font-family: 'Orbitron', monospace;
        font-size: clamp(1rem, 4vw, 1.5rem);
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
    
    .player-item-b { border-left-color: #ff6b35; }
    
    .player-item-name {
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.1rem;
        font-weight: 600;
        color: #ffffff;
    }
    
    .player-item-rating {
        font-family: 'Orbitron', monospace;
        font-size: 0.85rem;
        color: #00d4ff;
        background: rgba(0, 212, 255, 0.2);
        padding: 4px 10px;
        border-radius: 20px;
    }
    
    .group-label {
        font-family: 'Orbitron', monospace;
        font-size: clamp(1.3rem, 5vw, 2rem);
        font-weight: 900;
        display: inline-block;
        padding: 6px 16px;
        border-radius: 50px;
        margin-bottom: 10px;
    }
    
    .group-a {
        background: linear-gradient(135deg, #00ff88, #00d4ff);
        color: #0a1628;
        box-shadow: 0 0 20px rgba(0, 255, 136, 0.5);
    }
    
    .group-b {
        background: linear-gradient(135deg, #ff6b35, #ffc107);
        color: #0a1628;
        box-shadow: 0 0 20px rgba(255, 107, 53, 0.5);
    }
    
    .vs-badge {
        font-family: 'Orbitron', monospace;
        font-size: clamp(1.5rem, 6vw, 2.5rem);
        font-weight: 900;
        color: #fff;
        text-shadow: 0 0 30px rgba(255, 255, 255, 0.8);
        text-align: center;
        padding: 10px;
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }
    
    .team-label {
        font-family: 'Rajdhani', sans-serif;
        font-size: 0.85rem;
        color: #88ccff;
        text-transform: uppercase;
        letter-spacing: 0.2em;
        margin-bottom: 8px;
        text-align: center;
    }
    
    .date-badge {
        font-family: 'Orbitron', monospace;
        font-size: clamp(0.8rem, 2.5vw, 1rem);
        color: #00d4ff;
        background: rgba(0, 212, 255, 0.1);
        padding: 6px 16px;
        border-radius: 50px;
        border: 1px solid rgba(0, 212, 255, 0.3);
        display: inline-block;
        margin-bottom: 15px;
    }
    
    .section-header {
        font-family: 'Orbitron', monospace;
        font-size: clamp(1.1rem, 4.5vw, 1.6rem);
        font-weight: 700;
        color: #00ffcc;
        border-bottom: 2px solid rgba(0, 255, 136, 0.4);
        padding-bottom: 8px;
        margin: 20px 0 12px 0;
        text-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
    }
    
    .sub-header {
        font-family: 'Rajdhani', sans-serif;
        font-size: clamp(0.95rem, 3.5vw, 1.2rem);
        font-weight: 600;
        color: #88ccff;
        margin: 12px 0 8px 0;
    }
    
    .stTextInput input {
        background: rgba(0, 0, 0, 0.4) !important;
        border: 2px solid rgba(0, 212, 255, 0.4) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1rem !important;
        padding: 10px !important;
        min-height: 45px !important;
    }
    
    .stTextInput input:focus {
        border-color: #00ff88 !important;
        box-shadow: 0 0 15px rgba(0, 255, 136, 0.3) !important;
    }
    
    .stTextArea textarea {
        background: rgba(0, 0, 0, 0.4) !important;
        border: 2px solid rgba(0, 212, 255, 0.4) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1rem !important;
        padding: 10px !important;
    }
    
    .stSelectbox > div > div {
        background: rgba(0, 0, 0, 0.4) !important;
        border: 2px solid rgba(0, 212, 255, 0.4) !important;
        border-radius: 12px !important;
        min-height: 45px !important;
    }
    
    .stDateInput > div > div {
        background: rgba(0, 0, 0, 0.4) !important;
        border: 2px solid rgba(0, 212, 255, 0.4) !important;
        border-radius: 12px !important;
    }
    
    .stRadio > div {
        background: rgba(0, 0, 0, 0.2) !important;
        border-radius: 12px !important;
        padding: 8px !important;
    }
    
    .stRadio label, .stCheckbox label {
        color: #ffffff !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 600 !important;
    }
    
    .stTextInput label, .stTextArea label, .stSelectbox label, .stDateInput label {
        color: #ffffff !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 600 !important;
    }
    
    .stButton > button {
        font-family: 'Orbitron', monospace !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #00ff88, #00d4ff) !important;
        color: #0a1628 !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 12px 25px !important;
        font-size: clamp(0.85rem, 3vw, 1rem) !important;
        min-height: 50px !important;
        box-shadow: 0 5px 20px rgba(0, 255, 136, 0.4) !important;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0, 255, 136, 0.6) !important;
    }
    
    .streamlit-expanderHeader {
        background: rgba(0, 0, 0, 0.3) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        font-family: 'Rajdhani', sans-serif !important;
    }
    
    .streamlit-expanderContent {
        background: rgba(0, 0, 0, 0.2) !important;
        border-radius: 0 0 10px 10px !important;
    }
    
    .roast-card {
        background: linear-gradient(145deg, rgba(255, 107, 53, 0.1), rgba(255, 193, 7, 0.05));
        border: 1px solid rgba(255, 107, 53, 0.3);
        border-radius: 15px;
        padding: 12px;
        margin: 8px 0;
    }
    
    .roast-author {
        font-family: 'Orbitron', monospace;
        font-size: 0.85rem;
        color: #ff6b35;
        margin-bottom: 6px;
    }
    
    .roast-content {
        font-family: 'Rajdhani', sans-serif;
        font-size: 1rem;
        color: #ffffff;
        line-height: 1.4;
    }
    
    .roast-time {
        font-family: 'Rajdhani', sans-serif;
        font-size: 0.75rem;
        color: #888;
        margin-top: 6px;
    }
    
    .anon-badge {
        background: rgba(138, 43, 226, 0.3);
        color: #da70d6;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.75rem;
        margin-left: 8px;
    }
    
    .match-card {
        background: linear-gradient(145deg, rgba(0, 212, 255, 0.1), rgba(0, 255, 136, 0.05));
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 15px;
        padding: 12px;
        margin: 8px 0;
    }
    
    .match-date {
        font-family: 'Orbitron', monospace;
        font-size: 0.8rem;
        color: #00d4ff;
        margin-bottom: 8px;
    }
    
    .match-teams {
        font-family: 'Rajdhani', sans-serif;
        font-size: 1rem;
        color: #ffffff;
        margin: 4px 0;
    }
    
    .match-score {
        font-family: 'Orbitron', monospace;
        font-size: 1.3rem;
        font-weight: 700;
        color: #00ff88;
        text-align: center;
        margin: 8px 0;
    }
    
    p, span, div { color: #e0e0e0; }
    strong, b { color: #ffffff; }
    .stMarkdown { color: #e0e0e0 !important; }
    .stMarkdown p { color: #e0e0e0 !important; }
    .stMarkdown strong { color: #ffffff !important; }
    
    .net-positive {
        color: #00ff88 !important;
        font-weight: 700;
    }
    
    .net-negative {
        color: #ff6b35 !important;
        font-weight: 700;
    }
    
    .neon-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #00ff88, #00d4ff, #ff6b35, transparent);
        margin: 15px 0;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d2137 0%, #1a3a52 100%) !important;
    }
    
    .stAlert {
        background: rgba(0, 0, 0, 0.3) !important;
        border-radius: 12px !important;
    }
    
    .tennis-ball {
        font-size: 1.3rem;
        animation: bounce 0.6s ease-in-out infinite;
        display: inline-block;
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-6px); }
    }
    
    .setup-box {
        background: rgba(255, 193, 7, 0.1);
        border: 2px solid rgba(255, 193, 7, 0.5);
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
    }
    
    .setup-box code {
        background: rgba(0, 0, 0, 0.3);
        padding: 2px 6px;
        border-radius: 4px;
        color: #00ff88;
    }
    
    @media (max-width: 768px) {
        .stTabs [data-baseweb="tab"] {
            flex: 1 1 30%;
            padding: 6px 4px !important;
            font-size: 0.65rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# 🔌 CONNECT TO GOOGLE SHEETS
# ═══════════════════════════════════════════════════════════════════

spreadsheet = get_google_sheet()
players_ws, matches_ws, reviews_ws = init_worksheets(spreadsheet)

# 检查连接状态
CONNECTED = spreadsheet is not None and players_ws is not None


# ═══════════════════════════════════════════════════════════════════
# 📊 LOAD DATA
# ═══════════════════════════════════════════════════════════════════

if 'data_loaded' not in st.session_state:
    if CONNECTED:
        players, group_a, group_b = load_players(players_ws)
        matches = load_matches(matches_ws)
        reviews = load_reviews(reviews_ws)
    else:
        players, group_a, group_b = [], [], []
        matches = []
        reviews = []
    
    st.session_state.players = players
    st.session_state.group_a = group_a
    st.session_state.group_b = group_b
    st.session_state.matches = matches
    st.session_state.reviews = reviews
    st.session_state.current_pairing = None
    st.session_state.data_loaded = True


# ═══════════════════════════════════════════════════════════════════
# 🎾 HEADER
# ═══════════════════════════════════════════════════════════════════

st.markdown('<h1 class="main-title">🎾 TENNIS LIFE</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">网球人生 · 双打配对</p>', unsafe_allow_html=True)
st.markdown(f'<div style="text-align: center;"><span class="date-badge">📅 {datetime.now().strftime("%Y年%m月%d日")}</span></div>', unsafe_allow_html=True)

# 连接状态提示
if CONNECTED:
    st.markdown('<div style="text-align:center;color:#00ff88;font-size:0.8rem;">✅ 已连接 Google Sheets</div>', unsafe_allow_html=True)
else:
    st.markdown('<div style="text-align:center;color:#ff6b35;font-size:0.8rem;">⚠️ 未连接数据库 (演示模式)</div>', unsafe_allow_html=True)

st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# 📝 SIDEBAR
# ═══════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("### ⚙️ 状态")
    st.markdown("---")
    
    if CONNECTED:
        st.success("✅ Google Sheets 已连接")
    else:
        st.warning("⚠️ 演示模式")
    
    st.markdown(f"**A组**: {len(st.session_state.group_a)} 人")
    st.markdown(f"**B组**: {len(st.session_state.group_b)} 人")
    st.markdown(f"**战绩**: {len(st.session_state.matches)} 场")
    st.markdown(f"**吐槽**: {len(st.session_state.reviews)} 条")
    
    st.markdown("---")
    
    if st.button("🔄 刷新数据", use_container_width=True):
        st.session_state.data_loaded = False
        st.rerun()


# ═══════════════════════════════════════════════════════════════════
# 👥 MAIN TABS
# ═══════════════════════════════════════════════════════════════════

# 如果未连接，显示配置指南
if not CONNECTED:
    st.markdown("""
    <div class="setup-box">
        <h3 style="color: #ffc107;">📋 配置 Google Sheets 存储</h3>
        <p style="color: #e0e0e0;">按以下步骤配置持久化存储：</p>
        <ol style="color: #e0e0e0;">
            <li>创建 Google Cloud 项目并启用 Google Sheets API</li>
            <li>创建服务账号并下载 JSON 密钥</li>
            <li>创建一个新的 Google Sheet 并分享给服务账号邮箱</li>
            <li>在 Streamlit Cloud 的 Secrets 中添加配置</li>
        </ol>
        <p style="color: #88ccff;">Secrets 格式：</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.code('''
# .streamlit/secrets.toml

sheet_url = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"

[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "xxx"
private_key = "-----BEGIN PRIVATE KEY-----\\nXXX\\n-----END PRIVATE KEY-----\\n"
client_email = "your-service@your-project.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
    ''', language='toml')
    
    st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)
    st.markdown("### 👇 以下为演示模式 (数据不会保存)")
    st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)


tab1, tab2, tab3, tab4, tab5 = st.tabs(["✍️ 自评入组", "🏆 分组抽签", "📊 战绩记录", "😤 复盘吐槽", "📋 历史记录"])


# ═══════════════════════════════════════════════════════════════════
# TAB 1: 自评入组
# ═══════════════════════════════════════════════════════════════════

with tab1:
    st.markdown('<p class="section-header">✍️ 球友自评入组</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="register-card">
        <p style="color: #00ffcc; font-size: 1rem;">👋 欢迎加入！</p>
        <p style="color: #88ccff; font-size: 0.9rem;">
            <strong>A组</strong>：4.0+ 高手 | <strong>B组</strong>：3.5及以下
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col_reg1, col_reg2 = st.columns([2, 1])
    
    with col_reg1:
        register_name = st.text_input("📝 名字", placeholder="输入名字", key="reg_name")
    
    with col_reg2:
        register_rating = st.selectbox("⭐ 水平", ["4.5", "4.0", "3.5", "3.0", "2.5"], key="reg_rating")
    
    if st.button("🎾 加入活动", use_container_width=True, key="reg_submit"):
        if register_name.strip():
            rating = float(register_rating)
            existing = [p["name"].lower() for p in st.session_state.players]
            
            if register_name.strip().lower() in existing:
                st.warning(f"⚠️ '{register_name}' 已报名")
            else:
                player = {
                    "name": register_name.strip(),
                    "rating": rating,
                    "group": "A" if rating >= 4.0 else "B"
                }
                
                # 保存到 Google Sheets
                if CONNECTED:
                    if add_player(players_ws, player):
                        st.session_state.players.append(player)
                        if player["group"] == "A":
                            st.session_state.group_a.append(player)
                        else:
                            st.session_state.group_b.append(player)
                        st.success(f"✅ {register_name} → {'A组' if player['group']=='A' else 'B组'}")
                        st.balloons()
                    else:
                        st.error("保存失败")
                else:
                    st.session_state.players.append(player)
                    if player["group"] == "A":
                        st.session_state.group_a.append(player)
                    else:
                        st.session_state.group_b.append(player)
                    st.success(f"✅ {register_name} → {'A组' if player['group']=='A' else 'B组'} (演示)")
                    st.balloons()
        else:
            st.warning("⚠️ 请输入名字")
    
    st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown('<div class="team-card">', unsafe_allow_html=True)
        st.markdown('<span class="group-label group-a">A组</span>', unsafe_allow_html=True)
        if st.session_state.group_a:
            for p in st.session_state.group_a:
                st.markdown(f'<div class="player-item"><span class="player-item-name">{p["name"]}</span><span class="player-item-rating">⭐{p["rating"]}</span></div>', unsafe_allow_html=True)
        else:
            st.markdown("*暂无*")
        st.markdown(f"**共 {len(st.session_state.group_a)} 人**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_b:
        st.markdown('<div class="team-card team-card-b">', unsafe_allow_html=True)
        st.markdown('<span class="group-label group-b">B组</span>', unsafe_allow_html=True)
        if st.session_state.group_b:
            for p in st.session_state.group_b:
                st.markdown(f'<div class="player-item player-item-b"><span class="player-item-name">{p["name"]}</span><span class="player-item-rating">⭐{p["rating"]}</span></div>', unsafe_allow_html=True)
        else:
            st.markdown("*暂无*")
        st.markdown(f"**共 {len(st.session_state.group_b)} 人**")
        st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# TAB 2: 分组抽签
# ═══════════════════════════════════════════════════════════════════

with tab2:
    st.markdown('<p class="section-header">🎲 双打抽签</p>', unsafe_allow_html=True)
    
    st.markdown(f"**A组**: {len(st.session_state.group_a)} | **B组**: {len(st.session_state.group_b)}")
    
    if st.button("🎾 开始抽签", use_container_width=True, key="draw"):
        total = len(st.session_state.group_a) + len(st.session_state.group_b)
        if total >= 4:
            if len(st.session_state.group_a) >= 2 and len(st.session_state.group_b) >= 2:
                a = st.session_state.group_a.copy()
                b = st.session_state.group_b.copy()
                random.shuffle(a)
                random.shuffle(b)
                team1 = [a[0], b[0]]
                team2 = [a[1], b[1]]
            else:
                all_p = st.session_state.group_a + st.session_state.group_b
                random.shuffle(all_p)
                team1 = all_p[:2]
                team2 = all_p[2:4]
            st.session_state.current_pairing = {"team1": team1, "team2": team2}
            st.rerun()
        else:
            st.warning("⚠️ 至少需要4人")
    
    if st.session_state.current_pairing:
        p = st.session_state.current_pairing
        st.markdown("---")
        col_t1, col_vs, col_t2 = st.columns([2, 1, 2])
        with col_t1:
            st.markdown('<div class="team-card"><p class="team-label">TEAM 1</p>', unsafe_allow_html=True)
            for x in p["team1"]:
                c = "" if x.get("group")=="A" else " player-name-b"
                st.markdown(f'<p class="player-name{c}">{x["name"]}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with col_vs:
            st.markdown('<div class="vs-badge">⚡VS⚡</div>', unsafe_allow_html=True)
        with col_t2:
            st.markdown('<div class="team-card team-card-b"><p class="team-label">TEAM 2</p>', unsafe_allow_html=True)
            for x in p["team2"]:
                c = "" if x.get("group")=="A" else " player-name-b"
                st.markdown(f'<p class="player-name{c}">{x["name"]}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("🔄 重抽", use_container_width=True):
            st.session_state.current_pairing = None
            st.rerun()


# ═══════════════════════════════════════════════════════════════════
# TAB 3: 战绩记录
# ═══════════════════════════════════════════════════════════════════

with tab3:
    st.markdown('<p class="section-header">📊 战绩记录</p>', unsafe_allow_html=True)
    
    names = [p["name"] for p in st.session_state.players]
    
    st.markdown("#### ➕ 新增战绩")
    
    match_date = st.date_input("📅 日期", value=date.today(), key="m_date")
    
    st.markdown("**Team 1**")
    c1, c2 = st.columns(2)
    with c1:
        t1p1 = st.selectbox("球员1", ["选择..."]+names, key="t1p1") if names else st.text_input("球员1", key="t1p1i")
    with c2:
        t1p2 = st.selectbox("球员2", ["选择..."]+names, key="t1p2") if names else st.text_input("球员2", key="t1p2i")
    
    st.markdown("**Team 2**")
    c3, c4 = st.columns(2)
    with c3:
        t2p1 = st.selectbox("球员1", ["选择..."]+names, key="t2p1") if names else st.text_input("球员1", key="t2p1i")
    with c4:
        t2p2 = st.selectbox("球员2", ["选择..."]+names, key="t2p2") if names else st.text_input("球员2", key="t2p2i")
    
    st.markdown("**比分**")
    sc1, scc, sc2 = st.columns([2,1,2])
    with sc1:
        s1 = st.text_input("T1", placeholder="7", key="s1")
    with scc:
        st.markdown("<div style='text-align:center;font-size:2rem;color:#fff;padding-top:20px;'>:</div>", unsafe_allow_html=True)
    with sc2:
        s2 = st.text_input("T2", placeholder="6", key="s2")
    
    if st.button("💾 保存战绩", use_container_width=True, key="save_m"):
        team1_n = [x for x in [t1p1 if isinstance(t1p1,str) and t1p1!="选择..." else None, t1p2 if isinstance(t1p2,str) and t1p2!="选择..." else None] if x]
        team2_n = [x for x in [t2p1 if isinstance(t2p1,str) and t2p1!="选择..." else None, t2p2 if isinstance(t2p2,str) and t2p2!="选择..." else None] if x]
        
        if not team1_n or not team2_n:
            st.warning("⚠️ 每队至少1人")
        elif not s1 or not s2:
            st.warning("⚠️ 填写比分")
        else:
            try:
                score1, score2 = int(s1), int(s2)
                match = {
                    "date": match_date.strftime("%Y-%m-%d"),
                    "team1": team1_n,
                    "team2": team2_n,
                    "score1": score1,
                    "score2": score2,
                    "net_diff": score1 - score2,
                    "winner": "team1" if score1>score2 else ("team2" if score2>score1 else "tie")
                }
                if CONNECTED:
                    if add_match(matches_ws, match):
                        st.session_state.matches.append(match)
                        st.success("✅ 已保存")
                        st.balloons()
                    else:
                        st.error("保存失败")
                else:
                    st.session_state.matches.append(match)
                    st.success("✅ 已保存 (演示)")
            except:
                st.warning("⚠️ 比分须为数字")
    
    st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)
    st.markdown("#### 📋 最近战绩")
    
    if st.session_state.matches:
        for m in reversed(st.session_state.matches[-10:]):
            w1 = "🏆" if m['winner']=='team1' else ""
            w2 = "🏆" if m['winner']=='team2' else ""
            st.markdown(f'''
            <div class="match-card">
                <div class="match-date">📅 {m['date']}</div>
                <div class="match-teams">{w1} {" & ".join(m['team1'])}</div>
                <div class="match-score">{m['score1']} : {m['score2']}</div>
                <div class="match-teams">{w2} {" & ".join(m['team2'])}</div>
            </div>
            ''', unsafe_allow_html=True)
    else:
        st.info("💡 暂无战绩")


# ═══════════════════════════════════════════════════════════════════
# TAB 4: 复盘吐槽
# ═══════════════════════════════════════════════════════════════════

with tab4:
    st.markdown('<p class="section-header">😤 复盘吐槽</p>', unsafe_allow_html=True)
    
    names = [p["name"] for p in st.session_state.players]
    
    col_au, col_an = st.columns([3,1])
    with col_au:
        if names:
            sel = st.selectbox("👤 身份", ["选择..."]+names+["其他"], key="r_au")
            author = st.text_input("名字", key="r_au_o") if sel=="其他" else ("" if sel=="选择..." else sel)
        else:
            author = st.text_input("👤 名字", key="r_au_only")
    with col_an:
        anon = st.checkbox("🎭匿名", key="anon")
    
    rtype = st.radio("类型", ["🎾 复盘", "😤 吐槽搭档", "🤦 吐槽自己"], horizontal=True, key="rtype")
    
    target = ""
    if rtype == "😤 吐槽搭档":
        target = st.selectbox("🎯 吐槽谁", ["选择..."]+names, key="r_tgt") if names else st.text_input("🎯 吐槽谁", key="r_tgt_i")
        if target == "选择...": target = ""
    
    content = st.text_area("💬 内容", placeholder="写下你的想法...", height=100, key="r_cnt")
    
    if st.button("📤 发布", use_container_width=True, key="r_sub"):
        if not content.strip():
            st.warning("⚠️ 填写内容")
        elif not anon and not author:
            st.warning("⚠️ 选择身份或匿名")
        elif rtype=="😤 吐槽搭档" and not target:
            st.warning("⚠️ 选择吐槽对象")
        else:
            review = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "author": "匿名球友" if anon else author,
                "is_anonymous": anon,
                "type": rtype,
                "target": target if rtype=="😤 吐槽搭档" else "",
                "content": content
            }
            if CONNECTED:
                if add_review(reviews_ws, review):
                    st.session_state.reviews.append(review)
                    st.success("✅ 已发布")
                    st.rerun()
                else:
                    st.error("发布失败")
            else:
                st.session_state.reviews.append(review)
                st.success("✅ 已发布 (演示)")
                st.rerun()
    
    st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)
    st.markdown("#### 📜 吐槽墙")
    
    if st.session_state.reviews:
        for r in reversed(st.session_state.reviews):
            emoji = r["type"].split()[0] if r["type"] else "💬"
            badge = '<span class="anon-badge">匿名</span>' if r.get("is_anonymous") else ""
            tgt = f" → <strong>{r['target']}</strong>" if r.get("target") else ""
            st.markdown(f'''
            <div class="roast-card">
                <div class="roast-author">{emoji} {r['author']}{badge}{tgt}</div>
                <div class="roast-content">{r['content']}</div>
                <div class="roast-time">🕐 {r['date']}</div>
            </div>
            ''', unsafe_allow_html=True)
    else:
        st.info("💡 暂无吐槽")


# ═══════════════════════════════════════════════════════════════════
# TAB 5: 历史记录
# ═══════════════════════════════════════════════════════════════════

with tab5:
    st.markdown('<p class="section-header">📋 完整历史</p>', unsafe_allow_html=True)
    
    st.markdown("#### 🏆 全部战绩")
    if st.session_state.matches:
        for i, m in enumerate(reversed(st.session_state.matches)):
            with st.expander(f"📅 {m['date']} | {m['score1']}:{m['score2']}", expanded=(i<3)):
                st.markdown(f"**T1**: {' & '.join(m['team1'])} → {m['score1']}")
                st.markdown(f"**T2**: {' & '.join(m['team2'])} → {m['score2']}")
                w = "T1🏆" if m['winner']=='team1' else ("T2🏆" if m['winner']=='team2' else "平局")
                st.markdown(f"**结果**: {w}")
    else:
        st.info("💡 暂无")
    
    st.markdown("---")
    st.markdown("#### 📝 全部吐槽")
    if st.session_state.reviews:
        for i, r in enumerate(reversed(st.session_state.reviews)):
            with st.expander(f"📅 {r['date']} - {r['type']}", expanded=(i<3)):
                st.markdown(f"**作者**: {r['author']}")
                if r.get("target"): st.markdown(f"**对象**: {r['target']}")
                st.markdown(f"**内容**: {r['content']}")
    else:
        st.info("💡 暂无")
    
    st.markdown("---")
    if st.session_state.matches or st.session_state.reviews:
        exp = {
            "players": st.session_state.players,
            "matches": st.session_state.matches,
            "reviews": st.session_state.reviews
        }
        st.download_button("📥 导出数据", json.dumps(exp, ensure_ascii=False, indent=2), f"tennis_{datetime.now().strftime('%Y%m%d')}.json", "application/json", use_container_width=True)


# ═══════════════════════════════════════════════════════════════════
# 🎾 FOOTER
# ═══════════════════════════════════════════════════════════════════

st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)
st.markdown('''
<div style="text-align:center;padding:10px;color:#88ccff;font-family:'Rajdhani',sans-serif;">
    <span class="tennis-ball">🎾</span>
    <span style="margin:0 10px;color:#fff;">TENNIS LIFE v5.0</span>
    <span class="tennis-ball">🎾</span>
</div>
''', unsafe_allow_html=True)
