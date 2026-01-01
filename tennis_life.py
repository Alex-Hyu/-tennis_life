"""
🎾 TENNIS LIFE - 网球人生
A stylish doubles match pairing and score tracking system
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
    initial_sidebar_state="expanded"
)

# Custom CSS for a sporty, energetic aesthetic
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;500;600;700&display=swap');
    
    /* Main background with court texture */
    .stApp {
        background: linear-gradient(135deg, #0a1628 0%, #1a3a52 50%, #0d2137 100%);
    }
    
    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Main title styling */
    .main-title {
        font-family: 'Orbitron', monospace;
        font-size: 4rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #00ff88 0%, #00d4ff 50%, #ff6b35 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 60px rgba(0, 255, 136, 0.5);
        margin-bottom: 0;
        letter-spacing: 0.1em;
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { filter: drop-shadow(0 0 20px rgba(0, 255, 136, 0.4)); }
        to { filter: drop-shadow(0 0 40px rgba(0, 212, 255, 0.6)); }
    }
    
    .subtitle {
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.5rem;
        text-align: center;
        color: #88ccff;
        margin-top: -10px;
        letter-spacing: 0.5em;
        text-transform: uppercase;
    }
    
    /* Card containers */
    .team-card {
        background: linear-gradient(145deg, rgba(0, 255, 136, 0.1), rgba(0, 212, 255, 0.05));
        border: 2px solid rgba(0, 255, 136, 0.3);
        border-radius: 20px;
        padding: 25px;
        margin: 15px 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 255, 136, 0.2),
                    inset 0 1px 0 rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
    }
    
    .team-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0, 255, 136, 0.3);
        border-color: rgba(0, 255, 136, 0.6);
    }
    
    .team-card-b {
        background: linear-gradient(145deg, rgba(255, 107, 53, 0.1), rgba(255, 193, 7, 0.05));
        border: 2px solid rgba(255, 107, 53, 0.3);
    }
    
    .team-card-b:hover {
        box-shadow: 0 15px 40px rgba(255, 107, 53, 0.3);
        border-color: rgba(255, 107, 53, 0.6);
    }
    
    /* Player name styling */
    .player-name {
        font-family: 'Orbitron', monospace;
        font-size: 1.8rem;
        font-weight: 700;
        color: #00ff88;
        text-shadow: 0 0 20px rgba(0, 255, 136, 0.5);
        margin: 10px 0;
    }
    
    .player-name-b {
        color: #ff6b35;
        text-shadow: 0 0 20px rgba(255, 107, 53, 0.5);
    }
    
    /* Group labels */
    .group-label {
        font-family: 'Orbitron', monospace;
        font-size: 2.5rem;
        font-weight: 900;
        display: inline-block;
        padding: 10px 30px;
        border-radius: 50px;
        margin-bottom: 20px;
    }
    
    .group-a {
        background: linear-gradient(135deg, #00ff88, #00d4ff);
        color: #0a1628;
        box-shadow: 0 0 30px rgba(0, 255, 136, 0.5);
    }
    
    .group-b {
        background: linear-gradient(135deg, #ff6b35, #ffc107);
        color: #0a1628;
        box-shadow: 0 0 30px rgba(255, 107, 53, 0.5);
    }
    
    /* VS badge */
    .vs-badge {
        font-family: 'Orbitron', monospace;
        font-size: 3rem;
        font-weight: 900;
        color: #fff;
        text-shadow: 0 0 30px rgba(255, 255, 255, 0.8),
                     0 0 60px rgba(255, 107, 53, 0.5);
        text-align: center;
        padding: 20px;
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }
    
    /* Score display */
    .score-display {
        font-family: 'Orbitron', monospace;
        font-size: 4rem;
        font-weight: 900;
        text-align: center;
        padding: 20px;
        background: linear-gradient(145deg, rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.3));
        border-radius: 15px;
        border: 2px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Match result card */
    .match-result {
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.02));
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        font-family: 'Rajdhani', sans-serif;
    }
    
    /* Date badge */
    .date-badge {
        font-family: 'Orbitron', monospace;
        font-size: 1.2rem;
        color: #00d4ff;
        background: rgba(0, 212, 255, 0.1);
        padding: 10px 25px;
        border-radius: 50px;
        border: 1px solid rgba(0, 212, 255, 0.3);
        display: inline-block;
        margin-bottom: 20px;
    }
    
    /* Section headers */
    .section-header {
        font-family: 'Orbitron', monospace;
        font-size: 1.8rem;
        font-weight: 700;
        color: #00d4ff;
        border-bottom: 2px solid rgba(0, 212, 255, 0.3);
        padding-bottom: 10px;
        margin: 30px 0 20px 0;
    }
    
    /* Textarea styling */
    .stTextArea textarea {
        background: rgba(0, 0, 0, 0.3) !important;
        border: 2px solid rgba(0, 212, 255, 0.3) !important;
        border-radius: 15px !important;
        color: #fff !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1.1rem !important;
    }
    
    .stTextArea textarea:focus {
        border-color: rgba(0, 255, 136, 0.6) !important;
        box-shadow: 0 0 20px rgba(0, 255, 136, 0.2) !important;
    }
    
    /* Input styling */
    .stTextInput input {
        background: rgba(0, 0, 0, 0.3) !important;
        border: 2px solid rgba(0, 212, 255, 0.3) !important;
        border-radius: 10px !important;
        color: #fff !important;
        font-family: 'Rajdhani', sans-serif !important;
    }
    
    .stSelectbox > div > div {
        background: rgba(0, 0, 0, 0.3) !important;
        border: 2px solid rgba(0, 212, 255, 0.3) !important;
        border-radius: 10px !important;
    }
    
    /* Button styling */
    .stButton > button {
        font-family: 'Orbitron', monospace !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #00ff88, #00d4ff) !important;
        color: #0a1628 !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 15px 40px !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 5px 20px rgba(0, 255, 136, 0.4) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 30px rgba(0, 255, 136, 0.6) !important;
    }
    
    /* Tennis ball decoration */
    .tennis-ball {
        font-size: 2rem;
        animation: bounce 0.6s ease-in-out infinite;
        display: inline-block;
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    /* Net difference indicator */
    .net-positive {
        color: #00ff88;
        font-weight: 700;
    }
    
    .net-negative {
        color: #ff6b35;
        font-weight: 700;
    }
    
    /* Sidebar styling */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d2137 0%, #1a3a52 100%) !important;
    }
    
    /* Divider */
    .neon-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #00ff88, #00d4ff, #ff6b35, transparent);
        margin: 30px 0;
        border-radius: 2px;
    }
    
    /* Match pairing display */
    .pairing-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 20px;
        padding: 30px;
        background: linear-gradient(145deg, rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.2));
        border-radius: 20px;
        border: 2px solid rgba(255, 255, 255, 0.1);
        margin: 20px 0;
    }
    
    .team-display {
        text-align: center;
        padding: 20px;
    }
    
    .team-label {
        font-family: 'Rajdhani', sans-serif;
        font-size: 0.9rem;
        color: #88ccff;
        text-transform: uppercase;
        letter-spacing: 0.2em;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# 📊 SESSION STATE INITIALIZATION
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
st.markdown('<p class="subtitle">网球人生 · 双打配对系统</p>', unsafe_allow_html=True)
st.markdown(f'<div style="text-align: center;"><span class="date-badge">📅 {datetime.now().strftime("%Y年%m月%d日 %A")}</span></div>', unsafe_allow_html=True)
st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# 📝 SIDEBAR - PLAYER MANAGEMENT
# ═══════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("### 🎾 球员管理")
    st.markdown("---")
    
    # Add new player
    st.markdown("#### ➕ 添加球员")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        new_player_name = st.text_input("姓名", placeholder="输入球员姓名", key="new_player")
    with col2:
        new_player_rating = st.selectbox("自评", ["4.5", "4.0", "3.5", "3.0", "2.5"], key="new_rating")
    
    if st.button("✅ 添加球员", use_container_width=True):
        if new_player_name.strip():
            player = {
                "name": new_player_name.strip(),
                "rating": float(new_player_rating),
                "group": "A" if float(new_player_rating) >= 4.0 else "B"
            }
            st.session_state.players.append(player)
            # Auto-assign to groups
            if player["group"] == "A":
                st.session_state.group_a.append(player)
            else:
                st.session_state.group_b.append(player)
            st.success(f"✅ {new_player_name} 已加入 {player['group']}组")
            st.rerun()
    
    st.markdown("---")
    
    # Quick add preset players
    st.markdown("#### ⚡ 快速添加")
    preset_names = st.text_area("批量添加 (每行: 姓名,评分)", 
                                 placeholder="张三,4.0\n李四,3.5\n王五,4.5",
                                 height=100)
    
    if st.button("📥 批量导入", use_container_width=True):
        if preset_names.strip():
            lines = preset_names.strip().split('\n')
            added = 0
            for line in lines:
                if ',' in line:
                    parts = line.split(',')
                    name = parts[0].strip()
                    try:
                        rating = float(parts[1].strip())
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
                st.success(f"✅ 成功导入 {added} 名球员")
                st.rerun()
    
    st.markdown("---")
    
    # Clear all
    if st.button("🗑️ 清空所有球员", use_container_width=True):
        st.session_state.players = []
        st.session_state.group_a = []
        st.session_state.group_b = []
        st.session_state.current_pairing = None
        st.rerun()


# ═══════════════════════════════════════════════════════════════════
# 👥 MAIN CONTENT - PLAYER GROUPS
# ═══════════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4 = st.tabs(["🏆 分组抽签", "📊 战绩记录", "📝 复盘吐槽", "📋 历史记录"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="team-card">', unsafe_allow_html=True)
        st.markdown('<span class="group-label group-a">A 组</span>', unsafe_allow_html=True)
        st.markdown("**自评 4.0+ 高手区**")
        
        if st.session_state.group_a:
            for i, player in enumerate(st.session_state.group_a):
                col_name, col_rating, col_del = st.columns([3, 1, 1])
                with col_name:
                    new_name = st.text_input(f"A{i+1}", value=player["name"], key=f"a_name_{i}", label_visibility="collapsed")
                    if new_name != player["name"]:
                        st.session_state.group_a[i]["name"] = new_name
                with col_rating:
                    st.markdown(f"<span style='color: #00ff88; font-weight: bold;'>⭐ {player['rating']}</span>", unsafe_allow_html=True)
                with col_del:
                    if st.button("❌", key=f"del_a_{i}"):
                        st.session_state.group_a.pop(i)
                        st.session_state.players = [p for p in st.session_state.players if p["name"] != player["name"]]
                        st.rerun()
        else:
            st.markdown("*暂无球员，请在左侧添加*")
        
        st.markdown(f"**共 {len(st.session_state.group_a)} 人**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="team-card team-card-b">', unsafe_allow_html=True)
        st.markdown('<span class="group-label group-b">B 组</span>', unsafe_allow_html=True)
        st.markdown("**自评 3.5+ 进阶区**")
        
        if st.session_state.group_b:
            for i, player in enumerate(st.session_state.group_b):
                col_name, col_rating, col_del = st.columns([3, 1, 1])
                with col_name:
                    new_name = st.text_input(f"B{i+1}", value=player["name"], key=f"b_name_{i}", label_visibility="collapsed")
                    if new_name != player["name"]:
                        st.session_state.group_b[i]["name"] = new_name
                with col_rating:
                    st.markdown(f"<span style='color: #ff6b35; font-weight: bold;'>⭐ {player['rating']}</span>", unsafe_allow_html=True)
                with col_del:
                    if st.button("❌", key=f"del_b_{i}"):
                        st.session_state.group_b.pop(i)
                        st.session_state.players = [p for p in st.session_state.players if p["name"] != player["name"]]
                        st.rerun()
        else:
            st.markdown("*暂无球员，请在左侧添加*")
        
        st.markdown(f"**共 {len(st.session_state.group_b)} 人**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)
    
    # ═══════════════════════════════════════════════════════════════════
    # 🎲 RANDOM PAIRING
    # ═══════════════════════════════════════════════════════════════════
    
    st.markdown('<p class="section-header">🎲 双打抽签</p>', unsafe_allow_html=True)
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    
    with col_btn2:
        if st.button("🎾 开始抽签！", use_container_width=True):
            if len(st.session_state.group_a) >= 2 and len(st.session_state.group_b) >= 2:
                # Random pair: 2 from A vs 2 from B
                team1 = random.sample(st.session_state.group_a, 2)
                team2 = random.sample(st.session_state.group_b, 2)
                
                st.session_state.current_pairing = {
                    "team1": team1,  # A组双打
                    "team2": team2,  # B组双打
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "score1": "",
                    "score2": ""
                }
                st.rerun()
            elif len(st.session_state.group_a) >= 1 and len(st.session_state.group_b) >= 1:
                # Mixed doubles: 1A + 1B vs 1A + 1B
                all_a = st.session_state.group_a.copy()
                all_b = st.session_state.group_b.copy()
                
                random.shuffle(all_a)
                random.shuffle(all_b)
                
                if len(all_a) >= 2 and len(all_b) >= 2:
                    team1 = [all_a[0], all_b[0]]
                    team2 = [all_a[1], all_b[1]]
                elif len(all_a) >= 1 and len(all_b) >= 1:
                    team1 = [all_a[0], all_b[0]]
                    remaining_a = all_a[1:] if len(all_a) > 1 else []
                    remaining_b = all_b[1:] if len(all_b) > 1 else []
                    remaining = remaining_a + remaining_b
                    if len(remaining) >= 2:
                        team2 = random.sample(remaining, 2)
                    else:
                        st.warning("⚠️ 球员不足，无法组成两队")
                        team2 = None
                
                if team2:
                    st.session_state.current_pairing = {
                        "team1": team1,
                        "team2": team2,
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "score1": "",
                        "score2": ""
                    }
                    st.rerun()
            else:
                st.warning("⚠️ 每组至少需要1名球员才能抽签")
    
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
            st.markdown('<div class="vs-badge">⚡ VS ⚡</div>', unsafe_allow_html=True)
        
        with col_t2:
            st.markdown('<div class="team-card team-card-b">', unsafe_allow_html=True)
            st.markdown('<p class="team-label">TEAM 2</p>', unsafe_allow_html=True)
            for p in pairing["team2"]:
                group_class = "" if p.get("group") == "A" else " player-name-b"
                st.markdown(f'<p class="player-name{group_class}">{p["name"]}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)


with tab2:
    st.markdown('<p class="section-header">📊 战绩记录看板</p>', unsafe_allow_html=True)
    
    if st.session_state.current_pairing:
        pairing = st.session_state.current_pairing
        
        st.markdown(f"**对阵**: {pairing['team1'][0]['name']} & {pairing['team1'][1]['name']} vs {pairing['team2'][0]['name']} & {pairing['team2'][1]['name']}")
        st.markdown(f"**时间**: {pairing['date']}")
        
        st.markdown("---")
        st.markdown("#### 📝 输入比分")
        
        col_s1, col_colon, col_s2 = st.columns([2, 1, 2])
        
        with col_s1:
            score1 = st.text_input("Team 1 得分", placeholder="例如: 7", key="score1_input")
        
        with col_colon:
            st.markdown("<div style='text-align: center; font-size: 3rem; color: #fff; padding-top: 25px;'>:</div>", unsafe_allow_html=True)
        
        with col_s2:
            score2 = st.text_input("Team 2 得分", placeholder="例如: 6", key="score2_input")
        
        # Calculate net difference
        if score1 and score2:
            try:
                s1 = int(score1)
                s2 = int(score2)
                net_diff = s1 - s2
                
                st.markdown("---")
                st.markdown("#### 🎯 比分分析")
                
                col_res1, col_res2, col_res3 = st.columns(3)
                
                with col_res1:
                    winner = "Team 1" if s1 > s2 else ("Team 2" if s2 > s1 else "平局")
                    winner_names = pairing['team1'] if s1 > s2 else (pairing['team2'] if s2 > s1 else None)
                    if winner_names:
                        st.markdown(f"**🏆 获胜方**: {winner_names[0]['name']} & {winner_names[1]['name']}")
                    else:
                        st.markdown("**🏆 结果**: 平局")
                
                with col_res2:
                    st.markdown(f"**📊 比分**: {s1} : {s2}")
                
                with col_res3:
                    net_class = "net-positive" if net_diff > 0 else ("net-negative" if net_diff < 0 else "")
                    sign = "+" if net_diff > 0 else ""
                    st.markdown(f"**净胜分**: <span class='{net_class}'>{sign}{net_diff}</span>", unsafe_allow_html=True)
                
                # Save match record
                if st.button("💾 保存战绩", use_container_width=True):
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
                st.warning("⚠️ 请输入有效的数字比分")
    else:
        st.info("💡 请先在「分组抽签」页面进行抽签，生成对阵")


with tab3:
    st.markdown('<p class="section-header">📝 球后复盘 & 吐槽专区</p>', unsafe_allow_html=True)
    
    st.markdown("#### 🎾 球后复盘")
    review_match = st.text_area(
        "今天的比赛表现如何？有什么战术心得？",
        placeholder="今天发挥不错，正手进攻质量很高...",
        height=120,
        key="review_match"
    )
    
    st.markdown("---")
    
    st.markdown("#### 😤 吐槽搭档")
    roast_partner = st.text_area(
        "搭档今天表现怎么样？（仅供娱乐，请友善交流）",
        placeholder="搭档今天网前太保守了，该上的球不上...",
        height=120,
        key="roast_partner"
    )
    
    st.markdown("---")
    
    st.markdown("#### 🤦 吐槽自己")
    roast_self = st.text_area(
        "反省一下自己今天的表现...",
        placeholder="今天二发太菜了，关键分心态崩了...",
        height=120,
        key="roast_self"
    )
    
    col_save, col_clear = st.columns(2)
    
    with col_save:
        if st.button("💾 保存复盘", use_container_width=True):
            if review_match or roast_partner or roast_self:
                review = {
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "match_review": review_match,
                    "partner_roast": roast_partner,
                    "self_roast": roast_self
                }
                st.session_state.reviews.append(review)
                st.success("✅ 复盘已保存！")
            else:
                st.warning("⚠️ 请至少填写一项内容")
    
    with col_clear:
        if st.button("🗑️ 清空输入", use_container_width=True):
            st.rerun()


with tab4:
    st.markdown('<p class="section-header">📋 历史记录</p>', unsafe_allow_html=True)
    
    # Match records
    st.markdown("#### 🏆 战绩历史")
    
    if st.session_state.match_records:
        for i, record in enumerate(reversed(st.session_state.match_records)):
            with st.expander(f"📅 {record['date']} - {record['score1']}:{record['score2']}", expanded=(i==0)):
                col_r1, col_r2 = st.columns(2)
                with col_r1:
                    st.markdown(f"**Team 1**: {' & '.join(record['team1'])}")
                    st.markdown(f"**得分**: {record['score1']}")
                with col_r2:
                    st.markdown(f"**Team 2**: {' & '.join(record['team2'])}")
                    st.markdown(f"**得分**: {record['score2']}")
                
                net_class = "net-positive" if record['net_diff'] > 0 else ("net-negative" if record['net_diff'] < 0 else "")
                sign = "+" if record['net_diff'] > 0 else ""
                st.markdown(f"**净胜分 (Team1视角)**: <span class='{net_class}'>{sign}{record['net_diff']}</span>", unsafe_allow_html=True)
                
                winner_text = "Team 1 获胜" if record['winner'] == 'team1' else ("Team 2 获胜" if record['winner'] == 'team2' else "平局")
                st.markdown(f"**结果**: 🏆 {winner_text}")
    else:
        st.info("💡 暂无战绩记录")
    
    st.markdown("---")
    
    # Review records
    st.markdown("#### 📝 复盘历史")
    
    if st.session_state.reviews:
        for i, review in enumerate(reversed(st.session_state.reviews)):
            with st.expander(f"📅 {review['date']}", expanded=(i==0)):
                if review.get('match_review'):
                    st.markdown("**🎾 比赛复盘**")
                    st.markdown(review['match_review'])
                if review.get('partner_roast'):
                    st.markdown("**😤 吐槽搭档**")
                    st.markdown(review['partner_roast'])
                if review.get('self_roast'):
                    st.markdown("**🤦 吐槽自己**")
                    st.markdown(review['self_roast'])
    else:
        st.info("💡 暂无复盘记录")
    
    st.markdown("---")
    
    # Export/Clear options
    col_export, col_clear_all = st.columns(2)
    
    with col_export:
        if st.session_state.match_records or st.session_state.reviews:
            export_data = {
                "match_records": st.session_state.match_records,
                "reviews": st.session_state.reviews,
                "export_date": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            st.download_button(
                "📥 导出所有记录 (JSON)",
                data=json.dumps(export_data, ensure_ascii=False, indent=2),
                file_name=f"tennis_life_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                use_container_width=True
            )
    
    with col_clear_all:
        if st.button("🗑️ 清空所有历史", use_container_width=True):
            st.session_state.match_records = []
            st.session_state.reviews = []
            st.success("✅ 历史记录已清空")
            st.rerun()


# ═══════════════════════════════════════════════════════════════════
# 🎾 FOOTER
# ═══════════════════════════════════════════════════════════════════

st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; padding: 20px; color: #88ccff; font-family: 'Rajdhani', sans-serif;">
    <span class="tennis-ball">🎾</span>
    <span style="margin: 0 20px;">TENNIS LIFE v1.0</span>
    <span class="tennis-ball">🎾</span>
    <br><br>
    <span style="font-size: 0.9rem; color: #668899;">Made with ❤️ for tennis lovers</span>
</div>
""", unsafe_allow_html=True)
