"""
🎾 TENNIS LIFE - 网球人生 v8.0
- 优化 API 调用：缓存 + 限流，避免配额超限
- 密码保护
- 数据可靠性
"""

import streamlit as st
import random
from datetime import datetime, date
import json
import hashlib
import time

# ═══════════════════════════════════════════════════════════════════
# 🔐 PASSWORD UTILS
# ═══════════════════════════════════════════════════════════════════

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()[:16]

def verify_password(password, hashed):
    return hash_password(password) == hashed


# ═══════════════════════════════════════════════════════════════════
# 📊 GOOGLE SHEETS SETUP WITH CACHING
# ═══════════════════════════════════════════════════════════════════

try:
    from google.oauth2.service_account import Credentials
    import gspread
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

GROUP_A_LIMIT = 10
GROUP_B_LIMIT = 10

# 缓存时间（秒）
CACHE_TTL = 60  # 1分钟内不重复请求

@st.cache_resource
def get_google_sheet():
    """连接 Google Sheets（带缓存）"""
    if not GSPREAD_AVAILABLE:
        return None
    try:
        creds_dict = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        client = gspread.authorize(creds)
        sheet_url = st.secrets["sheet_url"]
        spreadsheet = client.open_by_url(sheet_url)
        return spreadsheet
    except Exception as e:
        return None

@st.cache_resource
def get_worksheets(_spreadsheet):
    """获取所有工作表（带缓存）"""
    if not _spreadsheet:
        return None, None, None, None
    try:
        worksheet_names = [ws.title for ws in _spreadsheet.worksheets()]
        
        # Users
        if "users" not in worksheet_names:
            users_ws = _spreadsheet.add_worksheet(title="users", rows=1000, cols=10)
            users_ws.append_row(["name", "rating", "password_hash", "created_at"])
        else:
            users_ws = _spreadsheet.worksheet("users")
        
        # Groups
        if "groups" not in worksheet_names:
            groups_ws = _spreadsheet.add_worksheet(title="groups", rows=100, cols=10)
            groups_ws.append_row(["name", "rating", "group", "date"])
        else:
            groups_ws = _spreadsheet.worksheet("groups")
        
        # Matches
        if "matches" not in worksheet_names:
            matches_ws = _spreadsheet.add_worksheet(title="matches", rows=1000, cols=15)
            matches_ws.append_row(["id", "date", "team1", "team2", "score1", "score2", "net_diff", "winner", "created_at"])
        else:
            matches_ws = _spreadsheet.worksheet("matches")
        
        # Reviews
        if "reviews" not in worksheet_names:
            reviews_ws = _spreadsheet.add_worksheet(title="reviews", rows=1000, cols=10)
            reviews_ws.append_row(["id", "date", "author", "is_anonymous", "type", "target", "content"])
        else:
            reviews_ws = _spreadsheet.worksheet("reviews")
        
        return users_ws, groups_ws, matches_ws, reviews_ws
    except:
        return None, None, None, None


# ═══════════════════════════════════════════════════════════════════
# 📊 CACHED DATA LOADING - 关键优化！
# ═══════════════════════════════════════════════════════════════════

@st.cache_data(ttl=CACHE_TTL)
def load_users_cached(_ws_id):
    """加载用户（带缓存）"""
    spreadsheet = get_google_sheet()
    if not spreadsheet:
        return []
    try:
        ws = spreadsheet.worksheet("users")
        records = ws.get_all_records()
        return [{
            "name": str(r['name']),  # 强制转字符串
            "rating": float(r['rating']) if r.get('rating') else 3.0,
            "password_hash": str(r.get('password_hash', ''))
        } for r in records if r.get('name')]
    except:
        return []

@st.cache_data(ttl=CACHE_TTL)
def load_today_groups_cached(_ws_id, _today):
    """加载今日分组（带缓存）"""
    spreadsheet = get_google_sheet()
    if not spreadsheet:
        return [], []
    try:
        ws = spreadsheet.worksheet("groups")
        records = ws.get_all_records()
        group_a, group_b = [], []
        for r in records:
            if str(r.get('date', '')) == _today and r.get('name'):
                player = {"name": str(r['name']), "rating": float(r['rating']) if r.get('rating') else 3.0, "group": str(r.get('group', 'B'))}
                if player['group'] == 'A':
                    group_a.append(player)
                else:
                    group_b.append(player)
        return group_a, group_b
    except:
        return [], []

@st.cache_data(ttl=CACHE_TTL)
def load_matches_cached(_ws_id):
    """加载战绩（带缓存）"""
    spreadsheet = get_google_sheet()
    if not spreadsheet:
        return []
    try:
        ws = spreadsheet.worksheet("matches")
        records = ws.get_all_records()
        matches = []
        for r in records:
            if r.get('team1') or r.get('date'):
                matches.append({
                    "id": r.get('id', ''),
                    "date": str(r.get('date', '')),
                    "team1": str(r.get('team1', '')).split(',') if r.get('team1') else [],
                    "team2": str(r.get('team2', '')).split(',') if r.get('team2') else [],
                    "score1": int(r['score1']) if r.get('score1') and str(r['score1']).lstrip('-').isdigit() else 0,
                    "score2": int(r['score2']) if r.get('score2') and str(r['score2']).lstrip('-').isdigit() else 0,
                    "net_diff": int(r['net_diff']) if r.get('net_diff') else 0,
                    "winner": r.get('winner', 'tie')
                })
        return [m for m in matches if m['team1'] and m['team2']]
    except:
        return []

@st.cache_data(ttl=CACHE_TTL)
def load_reviews_cached(_ws_id):
    """加载吐槽（带缓存）"""
    spreadsheet = get_google_sheet()
    if not spreadsheet:
        return []
    try:
        ws = spreadsheet.worksheet("reviews")
        records = ws.get_all_records()
        return [{
            "id": r.get('id', ''),
            "date": r.get('date', ''),
            "author": r.get('author', '匿名'),
            "is_anonymous": str(r.get('is_anonymous', 'FALSE')).upper() == 'TRUE',
            "type": r.get('type', ''),
            "target": r.get('target', ''),
            "content": r.get('content', '')
        } for r in records if r.get('content')]
    except:
        return []


# ═══════════════════════════════════════════════════════════════════
# 📝 WRITE OPERATIONS (不缓存，但有错误处理)
# ═══════════════════════════════════════════════════════════════════

def add_user_to_sheet(user):
    """添加用户"""
    spreadsheet = get_google_sheet()
    if not spreadsheet:
        return False
    try:
        ws = spreadsheet.worksheet("users")
        ws.append_row([
            user['name'],
            user['rating'],
            user['password_hash'],
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ])
        # 清除缓存
        load_users_cached.clear()
        return True
    except Exception as e:
        st.error(f"保存失败: {e}")
        return False

def add_to_group_sheet(player, group):
    """添加到分组"""
    spreadsheet = get_google_sheet()
    if not spreadsheet:
        return False
    try:
        ws = spreadsheet.worksheet("groups")
        today = date.today().strftime("%Y-%m-%d")
        ws.append_row([player['name'], player['rating'], group, today])
        # 清除缓存
        load_today_groups_cached.clear()
        return True
    except Exception as e:
        st.error(f"加入失败: {e}")
        return False

def add_match_to_sheet(match):
    """添加战绩"""
    spreadsheet = get_google_sheet()
    if not spreadsheet:
        return False
    try:
        ws = spreadsheet.worksheet("matches")
        match_id = datetime.now().strftime("%Y%m%d%H%M%S") + str(random.randint(1000, 9999))
        ws.append_row([
            match_id,
            match['date'],
            ','.join(match['team1']),
            ','.join(match['team2']),
            str(match['score1']),
            str(match['score2']),
            str(match['net_diff']),
            match['winner'],
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ])
        match['id'] = match_id
        # 清除缓存
        load_matches_cached.clear()
        return True
    except Exception as e:
        st.error(f"保存失败: {e}")
        return False

def add_review_to_sheet(review):
    """添加吐槽"""
    spreadsheet = get_google_sheet()
    if not spreadsheet:
        return False
    try:
        ws = spreadsheet.worksheet("reviews")
        review_id = datetime.now().strftime("%Y%m%d%H%M%S") + str(random.randint(1000, 9999))
        ws.append_row([
            review_id,
            review['date'],
            review['author'],
            'TRUE' if review['is_anonymous'] else 'FALSE',
            review['type'],
            review['target'],
            review['content']
        ])
        review['id'] = review_id
        # 清除缓存
        load_reviews_cached.clear()
        return True
    except Exception as e:
        st.error(f"发布失败: {e}")
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
    
    .stApp { background: linear-gradient(135deg, #0a1628 0%, #1a3a52 50%, #0d2137 100%); }
    #MainMenu, footer, header {visibility: hidden;}
    
    .main-title {
        font-family: 'Orbitron', monospace;
        font-size: clamp(1.8rem, 7vw, 3.5rem);
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
        font-size: clamp(0.9rem, 3.5vw, 1.3rem);
        text-align: center;
        color: #88ccff;
        margin-top: 5px;
        letter-spacing: 0.3em;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 0; background: rgba(0, 0, 0, 0.3); border-radius: 15px;
        padding: 5px; flex-wrap: wrap; justify-content: center;
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
    
    .team-card {
        background: linear-gradient(145deg, rgba(0, 255, 136, 0.1), rgba(0, 212, 255, 0.05));
        border: 2px solid rgba(0, 255, 136, 0.3);
        border-radius: 15px; padding: 15px; margin: 10px 0;
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
        border-radius: 20px; padding: 20px; margin: 15px 0;
        box-shadow: 0 10px 40px rgba(0, 212, 255, 0.3);
    }
    
    .welcome-card {
        background: linear-gradient(145deg, rgba(0, 255, 136, 0.15), rgba(0, 212, 255, 0.1));
        border: 2px solid rgba(0, 255, 136, 0.5);
        border-radius: 20px; padding: 20px; margin: 15px 0; text-align: center;
    }
    
    .player-name {
        font-family: 'Orbitron', monospace;
        font-size: clamp(1rem, 4vw, 1.5rem);
        font-weight: 700; color: #00ff88;
        text-shadow: 0 0 15px rgba(0, 255, 136, 0.5);
        margin: 8px 0;
    }
    
    .player-name-b { color: #ff6b35; text-shadow: 0 0 15px rgba(255, 107, 53, 0.5); }
    
    .player-item {
        background: rgba(0, 0, 0, 0.2); border-radius: 10px;
        padding: 10px 15px; margin: 8px 0;
        display: flex; justify-content: space-between; align-items: center;
        border-left: 4px solid #00ff88;
    }
    
    .player-item-b { border-left-color: #ff6b35; }
    
    .player-item-name { font-family: 'Rajdhani', sans-serif; font-size: 1.1rem; font-weight: 600; color: #ffffff; }
    
    .player-item-rating {
        font-family: 'Orbitron', monospace; font-size: 0.85rem; color: #00d4ff;
        background: rgba(0, 212, 255, 0.2); padding: 4px 10px; border-radius: 20px;
    }
    
    .group-label {
        font-family: 'Orbitron', monospace;
        font-size: clamp(1.3rem, 5vw, 2rem);
        font-weight: 900; display: inline-block;
        padding: 6px 16px; border-radius: 50px; margin-bottom: 10px;
    }
    
    .group-a { background: linear-gradient(135deg, #00ff88, #00d4ff); color: #0a1628; box-shadow: 0 0 20px rgba(0, 255, 136, 0.5); }
    .group-b { background: linear-gradient(135deg, #ff6b35, #ffc107); color: #0a1628; box-shadow: 0 0 20px rgba(255, 107, 53, 0.5); }
    .group-full { background: rgba(255, 0, 0, 0.2); color: #ff6b6b; padding: 5px 15px; border-radius: 20px; font-size: 0.9rem; margin-left: 10px; }
    
    .vs-badge {
        font-family: 'Orbitron', monospace;
        font-size: clamp(1.5rem, 6vw, 2.5rem);
        font-weight: 900; color: #fff;
        text-shadow: 0 0 30px rgba(255, 255, 255, 0.8);
        text-align: center; padding: 10px;
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    @keyframes pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.1); } }
    
    .team-label { font-family: 'Rajdhani', sans-serif; font-size: 0.85rem; color: #88ccff; text-transform: uppercase; letter-spacing: 0.2em; margin-bottom: 8px; text-align: center; }
    
    .date-badge {
        font-family: 'Orbitron', monospace; font-size: clamp(0.8rem, 2.5vw, 1rem);
        color: #00d4ff; background: rgba(0, 212, 255, 0.1);
        padding: 6px 16px; border-radius: 50px;
        border: 1px solid rgba(0, 212, 255, 0.3);
        display: inline-block; margin-bottom: 15px;
    }
    
    .section-header {
        font-family: 'Orbitron', monospace;
        font-size: clamp(1.1rem, 4.5vw, 1.6rem);
        font-weight: 700; color: #00ffcc;
        border-bottom: 2px solid rgba(0, 255, 136, 0.4);
        padding-bottom: 8px; margin: 20px 0 12px 0;
        text-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
    }
    
    .user-badge {
        font-family: 'Orbitron', monospace; font-size: 1rem; color: #00ff88;
        background: rgba(0, 255, 136, 0.1);
        border: 1px solid rgba(0, 255, 136, 0.3);
        padding: 8px 20px; border-radius: 50px;
        display: inline-block; margin: 10px 0;
    }
    
    .stTextInput input, .stTextArea textarea {
        background: rgba(0, 0, 0, 0.4) !important;
        border: 2px solid rgba(0, 212, 255, 0.4) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1rem !important;
        padding: 10px !important;
        min-height: 45px !important;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #00ff88 !important;
        box-shadow: 0 0 15px rgba(0, 255, 136, 0.3) !important;
    }
    
    .stSelectbox > div > div, .stDateInput > div > div {
        background: rgba(0, 0, 0, 0.4) !important;
        border: 2px solid rgba(0, 212, 255, 0.4) !important;
        border-radius: 12px !important;
        min-height: 45px !important;
    }
    
    .stRadio > div { background: rgba(0, 0, 0, 0.2) !important; border-radius: 12px !important; padding: 8px !important; }
    .stRadio label, .stCheckbox label { color: #ffffff !important; font-family: 'Rajdhani', sans-serif !important; font-weight: 600 !important; }
    .stTextInput label, .stTextArea label, .stSelectbox label, .stDateInput label { color: #ffffff !important; font-family: 'Rajdhani', sans-serif !important; font-weight: 600 !important; }
    
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
    
    .stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 25px rgba(0, 255, 136, 0.6) !important; }
    
    .streamlit-expanderHeader { background: rgba(0, 0, 0, 0.3) !important; border-radius: 10px !important; color: #ffffff !important; }
    .streamlit-expanderContent { background: rgba(0, 0, 0, 0.2) !important; border-radius: 0 0 10px 10px !important; }
    
    .roast-card {
        background: linear-gradient(145deg, rgba(255, 107, 53, 0.1), rgba(255, 193, 7, 0.05));
        border: 1px solid rgba(255, 107, 53, 0.3);
        border-radius: 15px; padding: 12px; margin: 8px 0;
    }
    
    .roast-author { font-family: 'Orbitron', monospace; font-size: 0.85rem; color: #ff6b35; margin-bottom: 6px; }
    .roast-content { font-family: 'Rajdhani', sans-serif; font-size: 1rem; color: #ffffff; line-height: 1.4; }
    .roast-time { font-family: 'Rajdhani', sans-serif; font-size: 0.75rem; color: #888; margin-top: 6px; }
    .anon-badge { background: rgba(138, 43, 226, 0.3); color: #da70d6; padding: 2px 8px; border-radius: 10px; font-size: 0.75rem; margin-left: 8px; }
    
    .match-card {
        background: linear-gradient(145deg, rgba(0, 212, 255, 0.1), rgba(0, 255, 136, 0.05));
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 15px; padding: 12px; margin: 8px 0;
    }
    
    .match-date { font-family: 'Orbitron', monospace; font-size: 0.8rem; color: #00d4ff; margin-bottom: 8px; }
    .match-teams { font-family: 'Rajdhani', sans-serif; font-size: 1rem; color: #ffffff; margin: 4px 0; }
    .match-score { font-family: 'Orbitron', monospace; font-size: 1.3rem; font-weight: 700; color: #00ff88; text-align: center; margin: 8px 0; }
    
    p, span, div { color: #e0e0e0; }
    strong, b { color: #ffffff; }
    .stMarkdown, .stMarkdown p { color: #e0e0e0 !important; }
    .stMarkdown strong { color: #ffffff !important; }
    
    .neon-divider { height: 2px; background: linear-gradient(90deg, transparent, #00ff88, #00d4ff, #ff6b35, transparent); margin: 15px 0; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0d2137 0%, #1a3a52 100%) !important; }
    .stAlert { background: rgba(0, 0, 0, 0.3) !important; border-radius: 12px !important; }
    
    .tennis-ball { font-size: 1.3rem; animation: bounce 0.6s ease-in-out infinite; display: inline-block; }
    @keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-6px); } }
    
    @media (max-width: 768px) {
        .stTabs [data-baseweb="tab"] { flex: 1 1 30%; padding: 6px 4px !important; font-size: 0.65rem !important; }
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# 🔌 CONNECT & LOAD DATA (优化版)
# ═══════════════════════════════════════════════════════════════════

spreadsheet = get_google_sheet()
CONNECTED = spreadsheet is not None

# 使用唯一标识符作为缓存key
CACHE_KEY = "tennis_v8"
TODAY = date.today().strftime("%Y-%m-%d")

# Initialize session state
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'current_pairing' not in st.session_state:
    st.session_state.current_pairing = None

# 加载数据（使用缓存）
if CONNECTED:
    users = load_users_cached(CACHE_KEY)
    group_a, group_b = load_today_groups_cached(CACHE_KEY, TODAY)
    matches = load_matches_cached(CACHE_KEY)
    reviews = load_reviews_cached(CACHE_KEY)
else:
    users, group_a, group_b, matches, reviews = [], [], [], [], []


# ═══════════════════════════════════════════════════════════════════
# 🎾 HEADER
# ═══════════════════════════════════════════════════════════════════

st.markdown('<h1 class="main-title">🎾 TENNIS LIFE</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">网球人生 · 双打配对</p>', unsafe_allow_html=True)
st.markdown(f'<div style="text-align: center;"><span class="date-badge">📅 {datetime.now().strftime("%Y年%m月%d日")}</span></div>', unsafe_allow_html=True)

if CONNECTED:
    st.markdown('<div style="text-align:center;color:#00ff88;font-size:0.75rem;">✅ 已连接</div>', unsafe_allow_html=True)
else:
    st.markdown('<div style="text-align:center;color:#ff6b35;font-size:0.75rem;">⚠️ 演示模式</div>', unsafe_allow_html=True)

st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# 📝 SIDEBAR
# ═══════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("### ⚙️ 状态")
    st.markdown("---")
    
    if st.session_state.current_user:
        st.markdown(f"**用户**: {st.session_state.current_user['name']}")
        st.markdown(f"**水平**: {st.session_state.current_user['rating']}")
        if st.button("🚪 退出", use_container_width=True):
            st.session_state.current_user = None
            st.rerun()
    else:
        st.markdown("*未登录*")
    
    st.markdown("---")
    st.markdown(f"**A组**: {len(group_a)}/{GROUP_A_LIMIT}")
    st.markdown(f"**B组**: {len(group_b)}/{GROUP_B_LIMIT}")
    st.markdown(f"**战绩**: {len(matches)} 场")
    st.markdown(f"**吐槽**: {len(reviews)} 条")
    
    st.markdown("---")
    if st.button("🔄 刷新", use_container_width=True):
        # 清除所有缓存
        load_users_cached.clear()
        load_today_groups_cached.clear()
        load_matches_cached.clear()
        load_reviews_cached.clear()
        st.rerun()


# ═══════════════════════════════════════════════════════════════════
# 🔐 LOGIN / REGISTER
# ═══════════════════════════════════════════════════════════════════

if st.session_state.current_user is None:
    st.markdown('<p class="section-header">🔐 登录 / 注册</p>', unsafe_allow_html=True)
    
    login_tab, register_tab = st.tabs(["🔑 登录", "✍️ 注册"])
    
    with login_tab:
        st.markdown('<div class="register-card"><p style="color: #00ffcc;">👋 输入名字和密码登录</p></div>', unsafe_allow_html=True)
        
        login_name = st.text_input("📝 名字", key="login_name")
        login_pwd = st.text_input("🔒 密码", type="password", key="login_pwd")
        
        if st.button("🚀 登录", key="login_btn"):
            if login_name.strip() and login_pwd:
                user = next((u for u in users if u['name'].lower() == login_name.strip().lower()), None)
                if user:
                    if verify_password(login_pwd, user.get('password_hash', '')):
                        st.session_state.current_user = user
                        st.success(f"✅ 欢迎 {user['name']}！")
                        st.rerun()
                    else:
                        st.error("❌ 密码错误")
                else:
                    st.error("❌ 用户不存在")
            else:
                st.warning("⚠️ 请输入名字和密码")
    
    with register_tab:
        st.markdown('<div class="register-card"><p style="color: #00ffcc;">🆕 新用户注册</p></div>', unsafe_allow_html=True)
        
        reg_name = st.text_input("📝 名字", key="reg_name")
        col1, col2 = st.columns(2)
        with col1:
            reg_pwd = st.text_input("🔒 密码", type="password", key="reg_pwd")
        with col2:
            reg_pwd2 = st.text_input("🔒 确认", type="password", key="reg_pwd2")
        
        rating_options = [f"{i/2:.1f}" for i in range(2, 11)]
        reg_rating = st.selectbox("⭐ 水平", rating_options, index=4, key="reg_rating")
        
        if st.button("🎾 注册", key="reg_btn"):
            if not reg_name.strip():
                st.warning("⚠️ 请输入名字")
            elif len(reg_pwd) < 4:
                st.warning("⚠️ 密码至少4位")
            elif reg_pwd != reg_pwd2:
                st.error("❌ 密码不一致")
            elif any(u['name'].lower() == reg_name.strip().lower() for u in users):
                st.error("❌ 名字已存在")
            else:
                user = {
                    "name": reg_name.strip(),
                    "rating": float(reg_rating),
                    "password_hash": hash_password(reg_pwd)
                }
                if CONNECTED:
                    if add_user_to_sheet(user):
                        st.session_state.current_user = user
                        st.success("✅ 注册成功！")
                        st.balloons()
                        st.rerun()
                else:
                    st.session_state.current_user = user
                    st.success("✅ 注册成功 (演示)")
                    st.rerun()

else:
    # ═══════════════════════════════════════════════════════════════
    # 🎮 MAIN APP
    # ═══════════════════════════════════════════════════════════════
    
    st.markdown(f'''
    <div class="welcome-card">
        <p style="color: #00ff88; font-size: 1.2rem; margin: 0;">👋 {st.session_state.current_user['name']}</p>
        <span class="user-badge">⭐ {st.session_state.current_user['rating']}</span>
    </div>
    ''', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🏆 分组抽签", "📊 战绩", "😤 吐槽", "📋 历史"])
    
    # ═══════════════════════════════════════════════════════════════
    # TAB 1: 分组抽签
    # ═══════════════════════════════════════════════════════════════
    
    with tab1:
        st.markdown('<p class="section-header">🏆 分组抽签</p>', unsafe_allow_html=True)
        
        current_name = st.session_state.current_user['name']
        in_a = any(p['name'] == current_name for p in group_a)
        in_b = any(p['name'] == current_name for p in group_b)
        
        st.markdown("#### 🎯 加入活动")
        
        if in_a or in_b:
            st.success(f"✅ 已加入 {'A组' if in_a else 'B组'}")
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                if len(group_a) >= GROUP_A_LIMIT:
                    st.markdown('<div style="text-align:center;color:#ff6b6b;">A组已满</div>', unsafe_allow_html=True)
                elif st.button(f"🅰️ A组 ({len(group_a)}/{GROUP_A_LIMIT})", key="join_a"):
                    player = {"name": current_name, "rating": st.session_state.current_user['rating'], "group": "A"}
                    if CONNECTED:
                        add_to_group_sheet(player, "A")
                    st.success("✅ 已加入A组")
                    st.rerun()
            
            with col_b:
                if len(group_b) >= GROUP_B_LIMIT:
                    st.markdown('<div style="text-align:center;color:#ff6b6b;">B组已满</div>', unsafe_allow_html=True)
                elif st.button(f"🅱️ B组 ({len(group_b)}/{GROUP_B_LIMIT})", key="join_b"):
                    player = {"name": current_name, "rating": st.session_state.current_user['rating'], "group": "B"}
                    if CONNECTED:
                        add_to_group_sheet(player, "B")
                    st.success("✅ 已加入B组")
                    st.rerun()
        
        st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)
        
        # Show groups
        col_ga, col_gb = st.columns(2)
        with col_ga:
            st.markdown('<div class="team-card">', unsafe_allow_html=True)
            st.markdown(f'<span class="group-label group-a">A组</span> <small>{len(group_a)}/{GROUP_A_LIMIT}</small>', unsafe_allow_html=True)
            for p in group_a:
                hl = "border:2px solid #00ff88;" if p['name'] == current_name else ""
                st.markdown(f'<div class="player-item" style="{hl}"><span class="player-item-name">{p["name"]}</span><span class="player-item-rating">⭐{p["rating"]}</span></div>', unsafe_allow_html=True)
            if not group_a:
                st.markdown("*暂无*")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_gb:
            st.markdown('<div class="team-card team-card-b">', unsafe_allow_html=True)
            st.markdown(f'<span class="group-label group-b">B组</span> <small>{len(group_b)}/{GROUP_B_LIMIT}</small>', unsafe_allow_html=True)
            for p in group_b:
                hl = "border:2px solid #ff6b35;" if p['name'] == current_name else ""
                st.markdown(f'<div class="player-item player-item-b" style="{hl}"><span class="player-item-name">{p["name"]}</span><span class="player-item-rating">⭐{p["rating"]}</span></div>', unsafe_allow_html=True)
            if not group_b:
                st.markdown("*暂无*")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)
        st.markdown("#### 🎲 抽签 (1A+1B=一队)")
        
        if st.button("🎾 抽签", key="draw"):
            if len(group_a) >= 2 and len(group_b) >= 2:
                a, b = group_a.copy(), group_b.copy()
                random.shuffle(a)
                random.shuffle(b)
                st.session_state.current_pairing = {"team1": [a[0], b[0]], "team2": [a[1], b[1]]}
                st.rerun()
            else:
                st.warning("⚠️ A组B组各需至少2人")
        
        if st.session_state.current_pairing:
            p = st.session_state.current_pairing
            st.markdown("---")
            c1, cv, c2 = st.columns([2, 1, 2])
            with c1:
                st.markdown('<div class="team-card"><p class="team-label">TEAM 1</p>', unsafe_allow_html=True)
                for x in p["team1"]:
                    st.markdown(f'<p class="player-name{"" if x.get("group")=="A" else "-b"}">{x["name"]}</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with cv:
                st.markdown('<div class="vs-badge">⚡VS⚡</div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="team-card team-card-b"><p class="team-label">TEAM 2</p>', unsafe_allow_html=True)
                for x in p["team2"]:
                    st.markdown(f'<p class="player-name{"" if x.get("group")=="A" else "-b"}">{x["name"]}</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            if st.button("🔄 重抽", key="redraw"):
                st.session_state.current_pairing = None
                st.rerun()
    
    # ═══════════════════════════════════════════════════════════════
    # TAB 2: 战绩
    # ═══════════════════════════════════════════════════════════════
    
    with tab2:
        st.markdown('<p class="section-header">📊 战绩记录</p>', unsafe_allow_html=True)
        
        match_date = st.date_input("📅 日期", value=date.today(), key="m_date")
        
        st.markdown("**Team 1**")
        c1, c2 = st.columns(2)
        with c1:
            t1p1 = st.text_input("球员1", key="t1p1")
        with c2:
            t1p2 = st.text_input("球员2", key="t1p2")
        
        st.markdown("**Team 2**")
        c3, c4 = st.columns(2)
        with c3:
            t2p1 = st.text_input("球员1", key="t2p1")
        with c4:
            t2p2 = st.text_input("球员2", key="t2p2")
        
        st.markdown("**比分**")
        sc1, scc, sc2 = st.columns([2, 1, 2])
        with sc1:
            s1 = st.text_input("T1", key="s1")
        with scc:
            st.markdown("<div style='text-align:center;font-size:2rem;color:#fff;padding-top:20px;'>:</div>", unsafe_allow_html=True)
        with sc2:
            s2 = st.text_input("T2", key="s2")
        
        if st.button("💾 保存", key="save_m"):
            t1 = [x.strip() for x in [t1p1, t1p2] if x.strip()]
            t2 = [x.strip() for x in [t2p1, t2p2] if x.strip()]
            
            if not t1 or not t2:
                st.warning("⚠️ 每队至少1人")
            elif not s1 or not s2:
                st.warning("⚠️ 填写比分")
            else:
                try:
                    score1, score2 = int(s1), int(s2)
                    match = {
                        "date": match_date.strftime("%Y-%m-%d"),
                        "team1": t1, "team2": t2,
                        "score1": score1, "score2": score2,
                        "net_diff": score1 - score2,
                        "winner": "team1" if score1 > score2 else ("team2" if score2 > score1 else "tie")
                    }
                    if CONNECTED:
                        if add_match_to_sheet(match):
                            st.success("✅ 已保存")
                            st.balloons()
                    else:
                        st.success("✅ 已保存 (演示)")
                except:
                    st.warning("⚠️ 比分须为数字")
        
        st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)
        st.markdown("#### 📋 最近战绩")
        
        for m in reversed(matches[-10:]):
            w1 = "🏆" if m.get('winner') == 'team1' else ""
            w2 = "🏆" if m.get('winner') == 'team2' else ""
            st.markdown(f'''
            <div class="match-card">
                <div class="match-date">📅 {m.get('date', '')}</div>
                <div class="match-teams">{w1} {" & ".join(m.get('team1', []))}</div>
                <div class="match-score">{m.get('score1', 0)} : {m.get('score2', 0)}</div>
                <div class="match-teams">{w2} {" & ".join(m.get('team2', []))}</div>
            </div>
            ''', unsafe_allow_html=True)
        
        if not matches:
            st.info("💡 暂无")
    
    # ═══════════════════════════════════════════════════════════════
    # TAB 3: 吐槽
    # ═══════════════════════════════════════════════════════════════
    
    with tab3:
        st.markdown('<p class="section-header">😤 复盘吐槽</p>', unsafe_allow_html=True)
        
        col_au, col_an = st.columns([3, 1])
        with col_au:
            st.markdown(f"**发布者**: {st.session_state.current_user['name']}")
        with col_an:
            anon = st.checkbox("🎭匿名", key="anon")
        
        rtype = st.radio("类型", ["🎾 复盘", "😤 吐槽搭档", "🤦 吐槽自己"], horizontal=True, key="rtype")
        
        target = ""
        if rtype == "😤 吐槽搭档":
            all_names = [u['name'] for u in users]
            target = st.selectbox("🎯 吐槽谁", ["选择..."] + all_names, key="r_tgt")
            if target == "选择...":
                target = ""
        
        content = st.text_area("💬 内容", height=100, key="r_cnt")
        
        if st.button("📤 发布", key="r_sub"):
            if not content.strip():
                st.warning("⚠️ 填写内容")
            elif rtype == "😤 吐槽搭档" and not target:
                st.warning("⚠️ 选择对象")
            else:
                review = {
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "author": "匿名球友" if anon else st.session_state.current_user['name'],
                    "is_anonymous": anon,
                    "type": rtype,
                    "target": target if rtype == "😤 吐槽搭档" else "",
                    "content": content
                }
                if CONNECTED:
                    if add_review_to_sheet(review):
                        st.success("✅ 已发布")
                        st.rerun()
                else:
                    st.success("✅ 已发布 (演示)")
                    st.rerun()
        
        st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)
        st.markdown("#### 📜 吐槽墙")
        
        for r in reversed(reviews):
            emoji = r.get("type", "💬").split()[0] if r.get("type") else "💬"
            badge = '<span class="anon-badge">匿名</span>' if r.get("is_anonymous") else ""
            tgt = f" → <strong>{r['target']}</strong>" if r.get("target") else ""
            st.markdown(f'''
            <div class="roast-card">
                <div class="roast-author">{emoji} {r.get('author', '')}{badge}{tgt}</div>
                <div class="roast-content">{r.get('content', '')}</div>
                <div class="roast-time">🕐 {r.get('date', '')}</div>
            </div>
            ''', unsafe_allow_html=True)
        
        if not reviews:
            st.info("💡 暂无")
    
    # ═══════════════════════════════════════════════════════════════
    # TAB 4: 历史
    # ═══════════════════════════════════════════════════════════════
    
    with tab4:
        st.markdown('<p class="section-header">📋 历史记录</p>', unsafe_allow_html=True)
        
        st.markdown("#### 🏆 战绩")
        for i, m in enumerate(reversed(matches)):
            with st.expander(f"📅 {m.get('date', '')} | {m.get('score1', 0)}:{m.get('score2', 0)}", expanded=(i < 3)):
                st.markdown(f"**T1**: {' & '.join(m.get('team1', []))} → {m.get('score1', 0)}")
                st.markdown(f"**T2**: {' & '.join(m.get('team2', []))} → {m.get('score2', 0)}")
        
        if not matches:
            st.info("💡 暂无")
        
        st.markdown("---")
        st.markdown("#### 📝 吐槽")
        for i, r in enumerate(reversed(reviews)):
            with st.expander(f"📅 {r.get('date', '')} - {r.get('type', '')}", expanded=(i < 3)):
                st.markdown(f"**作者**: {r.get('author', '')}")
                st.markdown(f"**内容**: {r.get('content', '')}")
        
        if not reviews:
            st.info("💡 暂无")


# ═══════════════════════════════════════════════════════════════════
# 🎾 FOOTER
# ═══════════════════════════════════════════════════════════════════

st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center;padding:10px;color:#88ccff;"><span class="tennis-ball">🎾</span> <span style="color:#fff;">TENNIS LIFE v8.0</span> <span class="tennis-ball">🎾</span></div>', unsafe_allow_html=True)
