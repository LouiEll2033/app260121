import streamlit as st
import requests
import json
import uuid
from datetime import datetime, timedelta

# --- 페이지 설정 ---
st.set_page_config(page_title="아이젠하워 매트릭스", layout="wide", initial_sidebar_state="collapsed")

# --- 고급 스타일 커스텀 ---
st.markdown("""
    <style>
    /* 기본 배경 및 여백 제거 */
    .main { background-color: #fcfcfc; }
    .block-container { 
        padding-top: 0.8rem !important; 
        padding-bottom: 0.5rem !important; 
        padding-left: 0.5rem !important; 
        padding-right: 0.5rem !important; 
    }
    
    /* 2x2 그리드 강제 유지 (가장 강력한 CSS 규칙) */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important; /* 줄바꿈 절대 차단 */
        width: 100% !important;
        gap: 8px !important;
        margin-bottom: 8px !important;
    }
    
    [data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        width: 50% !important;
        min-width: 0px !important;
        flex-basis: 50% !important;
        flex-grow: 1 !important;
        flex-shrink: 0 !important;
        padding: 0 !important;
    }

    /* 사분면 카드 디자인 */
    .q-card {
        border-radius: 12px;
        padding: 0px;
        margin-bottom: 4px;
        border: 1px solid rgba(0,0,0,0.05);
        overflow: hidden;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }

    .q-header {
        font-weight: 800;
        padding: 8px 4px;
        font-size: 0.75rem;
        text-align: center;
        color: #334155;
        border-bottom: 1px solid rgba(0,0,0,0.05);
    }

    /* 할 일 목록 영역 (글씨 잘림 방지 설정) */
    .quadrant-container {
        padding: 6px;
        background-color: #ffffff;
        min-height: 140px;
        max-height: 40vh;
        overflow-y: auto;
    }

    /* 할 일 텍스트 줄바꿈 및 가독성 */
    .task-text { 
        font-size: 0.72rem !important; 
        line-height: 1.3 !important; 
        margin-bottom: 0px !important;
        word-wrap: break-word !important;
        overflow-wrap: anywhere !important; /* 긴 단어도 강제 줄바꿈 */
        white-space: normal !important;
        color: #475569;
    }
    
    /* 위젯 간격 최적화 */
    .stVerticalBlock { gap: 0rem !important; }
    div[data-testid="stCheckbox"] { 
        margin-bottom: -12px !important; 
        transform: scale(0.9);
    }

    /* ➕ 추가 팝오버 버튼 세련된 스타일 */
    div[data-testid="stPopover"] > button {
        padding: 2px 8px !important;
        font-size: 0.65rem !important;
        font-weight: 700 !important;
        min-height: 28px !important;
        border-radius: 8px !important;
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        color: #64748b !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
        width: 100% !important;
    }
    
    /* 체크박스 레이블 숨기기 */
    div[data-testid="stCheckbox"] label { display: none !important; }
    
    /* 스크롤바 세련된 디자인 */
    ::-webkit-scrollbar { width: 3px; }
    ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
    
    /* 상단 메뉴 등 제거 */
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 데이터 관리 ---
if 'tasks' not in st.session_state:
    st.session_state.tasks = []

def add_task(text, quadrant_num, date):
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
        "quadrant": quadrant_num
    })

# --- 상단 헤더 ---
c_title, c_date = st.columns([1, 1])
with c_title: st.markdown("<h5 style='margin-bottom:0; color:#1e293b;'>Focus Matrix</h5>", unsafe_allow_html=True)
with c_date: selected_date = st.date_input("날짜", datetime.now(), label_visibility="collapsed")

# --- 매트릭스 사분면 설정 ---
quadrants = [
    {"num": 1, "title": "중요 & 긴급", "subtitle": "DO FIRST", "color": "#fee2e2", "icon": "🔥"},
    {"num": 2, "title": "중요 & 비긴급", "subtitle": "SCHEDULE", "color": "#ecfdf5", "icon": "📅"},
    {"num": 3, "title": "긴급 & 비중요", "subtitle": "DELEGATE", "color": "#eff6ff", "icon": "👤"},
    {"num": 4, "title": "비중요 & 비긴급", "subtitle": "DELETE", "color": "#f8fafc", "icon": "🗑️"}
]

visible_tasks = [t for t in st.session_state.tasks if t['date'] == str(selected_date) or (t['date'] < str(selected_date) and not t['completed'])]

# --- 2x2 그리드 렌더링 ---
row1 = st.columns(2)
row2 = st.columns(2)
grid = [row1[0], row1[1], row2[0], row2[1]]

for i, q in enumerate(quadrants):
    with grid[i]:
        # 카드 컨테이너 시작
        st.markdown(f'''
            <div class="q-header" style="background-color: {q["color"]};">
                <span style="font-size:0.8rem;">{q["icon"]}</span> {q["title"]}
                <div style="font-size:0.5rem; opacity:0.6; margin-top:1px;">{q["subtitle"]}</div>
            </div>
        ''', unsafe_allow_html=True)
        
        # 직접 추가 버튼
        with st.popover("➕ 할 일 기록", use_container_width=True):
            in_val = st.text_input("내용", key=f"in_{q['num']}", label_visibility="collapsed", placeholder="할 일을 입력하세요...")
            if st.button("저장", key=f"btn_{q['num']}", use_container_width=True):
                add_task(in_val, q['num'], selected_date)
                st.rerun()
        
        # 목록 영역
        q_tasks = [t for t in visible_tasks if t['quadrant'] == q['num']]
        
        st.markdown('<div class="quadrant-container">', unsafe_allow_html=True)
        if not q_tasks:
            st.markdown("<div style='text-align:center; padding:20px; color:#cbd5e1; font-size:0.6rem;'>기록 없음</div>", unsafe_allow_html=True)
        
        for task in q_tasks:
            t_col1, t_col2, t_col3 = st.columns([0.18, 0.67, 0.15])
            
            with t_col1:
                new_status = st.checkbox("", value=task['completed'], key=f"chk_{task['id']}")
                if new_status != task['completed']:
                    task['completed'] = new_status
                    st.rerun()
            
            with t_col2:
                txt = task['text']
                style = "color:#94a3b8; text-decoration:line-through;" if task['completed'] else "color:#475569; font-weight:500;"
                prefix = "<span style='color:#f59e0b;'>⏳ </span>" if task['date'] < str(selected_date) else ""
                st.markdown(f"<div class='task-text' style='{style}'>{prefix}{txt}</div>", unsafe_allow_html=True)
            
            with t_col3:
                if st.button("×", key=f"del_{task['id']}", help="삭제"):
                    st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.caption("Focus Matrix Pro v3.0 | 2x2 Mobile Optimized")
