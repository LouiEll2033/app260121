# [설치 방법] 터미널(Terminal)에 입력:
# pip install streamlit

# [실행 방법] 'streamlit' 명령어가 인식되지 않을 때 아래 명령어를 입력하세요:
# python -m streamlit run eisenhower_streamlit.py

import streamlit as st
import requests
import json
import uuid
from datetime import datetime, timedelta

# --- 페이지 설정 ---
st.set_page_config(
    page_title="아이젠하워 매트릭스 Pro", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- 다크모드 토글 초기화 ---
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# --- 스타일 커스텀 ---
def get_theme_colors():
    if st.session_state.dark_mode:
        return {
            'bg': '#0f172a',
            'card': '#1e293b',
            'text': '#e2e8f0',
            'text_muted': '#94a3b8',
            'border': '#334155',
            'q1': '#7f1d1d',
            'q2': '#14532d',
            'q3': '#164e63',
            'q4': '#334155'
        }
    else:
        return {
            'bg': '#fcfcfc',
            'card': '#ffffff',
            'text': '#1e293b',
            'text_muted': '#64748b',
            'border': '#e2e8f0',
            'q1': '#fee2e2',
            'q2': '#dcfce7',
            'q3': '#e0f2fe',
            'q4': '#f1f5f9'
        }

colors = get_theme_colors()

st.markdown(f"""
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap" rel="stylesheet">
    <style>
    html, body, [class*="st-"] {{
        font-family: 'Noto Sans KR', sans-serif !important;
    }}

    .main {{ background-color: {colors['bg']}; }}
    
    .block-container {{ 
        padding-top: 1rem !important; 
        padding-bottom: 1rem !important;
        padding-left: 0.6rem !important;
        padding-right: 0.6rem !important;
    }}
    
    .app-title {{
        font-size: 1.8rem !important;
        font-weight: 900 !important;
        color: {colors['text']};
        margin-bottom: 10px !important;
        letter-spacing: -1px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}

    .stats-card {{
        background: {colors['card']};
        border-radius: 12px;
        padding: 16px;
        border: 1px solid {colors['border']};
        margin-bottom: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }}

    .stat-number {{
        font-size: 2rem;
        font-weight: 900;
        color: {colors['text']};
    }}

    .stat-label {{
        font-size: 0.85rem;
        color: {colors['text_muted']};
        margin-top: 4px;
    }}

    div[data-testid="stHorizontalBlock"]:nth-of-type(n+2) {{
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        width: 100% !important;
        gap: 8px !important;
        margin-bottom: 8px !important;
    }}
    
    div[data-testid="stHorizontalBlock"]:nth-of-type(n+2) > div[data-testid="column"] {{
        width: 50% !important;
        flex: 1 1 50% !important;
        min-width: 0px !important;
        max-width: 50% !important;
        padding: 0 !important;
    }}

    .q-header {{
        font-weight: 900 !important;
        padding: 14px 8px;
        border-radius: 12px 12px 0 0;
        font-size: 1.05rem !important; 
        text-align: center;
        color: {colors['text']};
        margin-bottom: 0px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        word-break: keep-all; 
        line-height: 1.3;
    }}

    .task-text-container {{
        font-size: 1rem !important; 
        line-height: 1.4 !important;
        font-weight: 600;
        color: {colors['text']};
        word-wrap: break-word !important;
        overflow-wrap: anywhere !important; 
        white-space: normal !important;
        padding: 4px 0;
    }}
    
    .quadrant-content {{
        border: 1px solid {colors['border']};
        border-radius: 0 0 12px 12px;
        padding: 10px 6px;
        background-color: {colors['card']};
        min-height: 200px;
        max-height: 45vh;
        overflow-y: auto;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.03);
    }}

    div[data-testid="stCheckbox"] {{ 
        margin-top: 4px !important;
        margin-bottom: -10px !important; 
    }}
    div[data-testid="stCheckbox"] label {{ display: none !important; }}
    
    div[data-testid="stPopover"] > button {{
        padding: 6px 10px !important;
        font-size: 0.85rem !important;
        font-weight: 800 !important;
        min-height: 36px !important;
        border-radius: 8px !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        width: 100% !important;
        color: white !important;
        margin-top: 4px;
        transition: transform 0.2s;
    }}
    
    div[data-testid="stPopover"] > button:hover {{
        transform: translateY(-2px);
    }}
    
    button[key*="del_"] {{
        font-size: 1.2rem !important;
        color: #f87171 !important;
    }}

    .ai-suggestion {{
        background: linear-gradient(135deg, #667eea22 0%, #764ba222 100%);
        border-left: 3px solid #667eea;
        padding: 8px 12px;
        border-radius: 6px;
        margin: 8px 0;
        font-size: 0.9rem;
        color: {colors['text']};
    }}

    .priority-badge {{
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 700;
        margin-left: 6px;
    }}

    .note-text {{
        font-size: 0.85rem;
        color: {colors['text_muted']};
        font-style: italic;
        margin-top: 4px;
        padding-left: 8px;
        border-left: 2px solid {colors['border']};
    }}
    
    #MainMenu, footer, header {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)

# --- 데이터 관리 로직 ---
if 'tasks' not in st.session_state:
    st.session_state.tasks = []

if 'show_stats' not in st.session_state:
    st.session_state.show_stats = True

if 'view_mode' not in st.session_state:
    st.session_state.view_mode = "일간"

def add_task(text, quadrant_num, date, priority=1, note=""):
    if not text.strip(): return
    config = {
        1: {"urgent": True, "important": True},
        2: {"urgent": False, "important": True},
        3: {"urgent": True, "important": False},
        4: {"urgent": False, "important": False}
    }[quadrant_num]
    
    st.session_state.tasks.append({
        "id": str(uuid.uuid4()), 
        "text": text,
        "urgent": config["urgent"],
        "important": config["important"],
        "completed": False,
        "date": str(date),
        "quadrant": quadrant_num,
        "priority": priority,
        "note": note,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    })

def get_ai_suggestions(quadrant_num):
    suggestions = {
        1: ["🚨 긴급 회의 준비", "📞 중요 클라이언트 연락", "🔥 마감 임박 프로젝트"],
        2: ["📚 새로운 기술 학습", "🎯 장기 목표 계획", "💪 운동 루틴 설정"],
        3: ["📧 이메일 확인 및 답장", "📞 간단한 전화 통화", "🗂️ 서류 정리"],
        4: ["☕ 휴식 시간 갖기", "📱 SNS 둘러보기", "🎮 가벼운 게임"]
    }
    return suggestions.get(quadrant_num, [])

def calculate_stats(tasks, date):
    date_tasks = [t for t in tasks if t['date'] == str(date)]
    if not date_tasks:
        return {"total": 0, "completed": 0, "rate": 0, "urgent": 0}
    
    total = len(date_tasks)
    completed = len([t for t in date_tasks if t['completed']])
    urgent = len([t for t in date_tasks if t['urgent']])
    
    return {
        "total": total,
        "completed": completed,
        "rate": round((completed / total * 100) if total > 0 else 0, 1),
        "urgent": urgent
    }

# --- 사이드바 ---
with st.sidebar:
    st.markdown("### ⚙️ 설정")
    
    # 다크모드 토글
    if st.toggle("🌙 다크모드", value=st.session_state.dark_mode):
        st.session_state.dark_mode = True
        st.rerun()
    else:
        st.session_state.dark_mode = False
        st.rerun()
    
    st.markdown("---")
    
    # 뷰 모드 선택
    st.session_state.view_mode = st.radio("📅 보기 모드", ["일간", "주간"], horizontal=True)
    
    st.markdown("---")
    
    # 통계 토글
    st.session_state.show_stats = st.checkbox("📊 통계 표시", value=st.session_state.show_stats)
    
    st.markdown("---")
    
    # 데이터 관리
    st.markdown("### 🗂️ 데이터 관리")
    if st.button("🗑️ 완료된 할 일 삭제", use_container_width=True):
        st.session_state.tasks = [t for t in st.session_state.tasks if not t['completed']]
        st.success("완료된 할 일이 삭제되었습니다!")
        st.rerun()
    
    if st.button("⚠️ 모든 데이터 초기화", use_container_width=True):
        st.session_state.tasks = []
        st.success("모든 데이터가 초기화되었습니다!")
        st.rerun()

# --- 상단 헤더 ---
c_title, c_date = st.columns([1.2, 0.8])
with c_title: 
    st.markdown("<div class='app-title'>📋 아이젠하워 매트릭스 Pro</div>", unsafe_allow_html=True)
with c_date: 
    selected_date = st.date_input("날짜", datetime.now(), label_visibility="collapsed")

# --- 통계 대시보드 ---
if st.session_state.show_stats:
    stats = calculate_stats(st.session_state.tasks, selected_date)
    
    stat_cols = st.columns(4)
    with stat_cols[0]:
        st.markdown(f"""
        <div class='stats-card'>
            <div class='stat-number'>{stats['total']}</div>
            <div class='stat-label'>전체 할 일</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_cols[1]:
        st.markdown(f"""
        <div class='stats-card'>
            <div class='stat-number'>{stats['completed']}</div>
            <div class='stat-label'>완료된 할 일</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_cols[2]:
        st.markdown(f"""
        <div class='stats-card'>
            <div class='stat-number'>{stats['rate']}%</div>
            <div class='stat-label'>완료율</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_cols[3]:
        st.markdown(f"""
        <div class='stats-card'>
            <div class='stat-number'>{stats['urgent']}</div>
            <div class='stat-label'>긴급 할 일</div>
        </div>
        """, unsafe_allow_html=True)

# --- 주간 뷰 ---
if st.session_state.view_mode == "주간":
    st.markdown("### 📅 주간 뷰")
    week_cols = st.columns(7)
    
    for i in range(7):
        day = selected_date - timedelta(days=selected_date.weekday()) + timedelta(days=i)
        day_tasks = [t for t in st.session_state.tasks if t['date'] == str(day)]
        completed = len([t for t in day_tasks if t['completed']])
        
        with week_cols[i]:
            is_today = day == selected_date
            border = "3px solid #667eea" if is_today else f"1px solid {colors['border']}"
            st.markdown(f"""
            <div style='border: {border}; border-radius: 8px; padding: 12px; background: {colors['card']}; text-align: center;'>
                <div style='font-weight: 700; color: {colors['text']};'>{day.strftime('%m/%d')}</div>
                <div style='font-size: 0.8rem; color: {colors['text_muted']};'>{day.strftime('%a')}</div>
                <div style='font-size: 1.2rem; font-weight: 700; margin-top: 8px; color: #667eea;'>{completed}/{len(day_tasks)}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")

# --- 매트릭스 사분면 설정 ---
quadrants = [
    {"num": 1, "title": "중요하고 긴급한 일", "color": colors['q1'], "icon": "🔥"},
    {"num": 2, "title": "중요하지만 비긴급", "color": colors['q2'], "icon": "🌱"},
    {"num": 3, "title": "긴급하지만 비중요", "color": colors['q3'], "icon": "📢"},
    {"num": 4, "title": "비중요 & 비긴급", "color": colors['q4'], "icon": "☕"}
]

visible_tasks = [t for t in st.session_state.tasks if t['date'] == str(selected_date) or (t['date'] < str(selected_date) and not t['completed'])]

# --- 2x2 그리드 배치 ---
row1 = st.columns(2)
row2 = st.columns(2)
grid = [row1[0], row1[1], row2[0], row2[1]]

for i, q in enumerate(quadrants):
    with grid[i]:
        # 헤더
        st.markdown(f'<div class="q-header" style="background-color: {q["color"]};">{q["icon"]} {q["title"]}</div>', unsafe_allow_html=True)
        
        # ➕ 할 일 추가
        with st.popover("➕ 새 할 일 추가", use_container_width=True):
            in_val = st.text_input("할 일", key=f"in_{q['num']}", label_visibility="collapsed", placeholder="할 일을 입력하세요...")
            in_note = st.text_area("메모 (선택)", key=f"note_{q['num']}", label_visibility="collapsed", placeholder="상세 메모...", height=80)
            in_priority = st.select_slider("우선순위", options=[1, 2, 3, 4, 5], value=3, key=f"priority_{q['num']}")
            
            col_save, col_ai = st.columns([1, 1])
            with col_save:
                if st.button("💾 저장", key=f"btn_{q['num']}", use_container_width=True):
                    add_task(in_val, q['num'], selected_date, in_priority, in_note)
                    st.rerun()
            
            with col_ai:
                if st.button("🤖 AI 추천", key=f"ai_{q['num']}", use_container_width=True):
                    suggestions = get_ai_suggestions(q['num'])
                    for suggestion in suggestions:
                        st.markdown(f'<div class="ai-suggestion">💡 {suggestion}</div>', unsafe_allow_html=True)
        
        # 목록 영역
        q_tasks = sorted([t for t in visible_tasks if t['quadrant'] == q['num']], 
                        key=lambda x: (x['completed'], -x.get('priority', 1)))
        
        st.markdown('<div class="quadrant-content">', unsafe_allow_html=True)
        if not q_tasks:
            st.markdown(f"<div style='text-align:center; padding-top:50px; color:{colors['text_muted']}; font-size:0.9rem;'>할 일이 없습니다</div>", unsafe_allow_html=True)
        
        for task in q_tasks:
            t_col1, t_col2, t_col3 = st.columns([0.12, 0.76, 0.12])
            
            with t_col1:
                new_status = st.checkbox("", value=task['completed'], key=f"chk_{task['id']}")
                if new_status != task['completed']:
                    task['completed'] = new_status
                    st.rerun()
            
            with t_col2:
                txt = task['text']
                style = f"color:{colors['text_muted']}; text-decoration:line-through;" if task['completed'] else f"color:{colors['text']};"
                if task['date'] < str(selected_date): 
                    txt = f"⏳ {txt}"
                
                priority_color = ["#ef4444", "#f97316", "#eab308", "#84cc16", "#22c55e"][task.get('priority', 3) - 1]
                priority_badge = f'<span class="priority-badge" style="background: {priority_color}22; color: {priority_color};">P{task.get("priority", 3)}</span>'
                
                st.markdown(f"<div class='task-text-container' style='{style}'>{txt}{priority_badge}</div>", unsafe_allow_html=True)
                
                if task.get('note'):
                    st.markdown(f"<div class='note-text'>📝 {task['note']}</div>", unsafe_allow_html=True)
            
            with t_col3:
                if st.button("×", key=f"del_{task['id']}"):
                    st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.caption("아이젠하워 매트릭스 Pro v5.0 | Enhanced with AI & Analytics")
