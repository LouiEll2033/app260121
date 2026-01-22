import streamlit as st
import requests
import json
import uuid
from datetime import datetime, timedelta

# --- 페이지 설정 ---
st.set_page_config(page_title="아이젠하워 기록장", layout="wide", initial_sidebar_state="collapsed")

# --- 스타일 커스텀 (모바일 2x2 그리드 강제 고정 및 공간 극대화) ---
st.markdown("""
    <style>
    /* 전체 배경 및 여백 최적화 */
    .main { background-color: #ffffff; }
    .block-container { 
        padding-top: 0.5rem !important; 
        padding-bottom: 0.5rem !important; 
        padding-left: 0.5rem !important; 
        padding-right: 0.5rem !important; 
    }
    
    /* [핵심 해결책] 모든 가로 블록(columns)에 대해 2열 강제 고정 */
    /* Streamlit 내부의 flex 컨테이너가 줄바꿈(wrap)을 하지 못하도록 강력하게 제어 */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important; /* 절대 줄바꿈 금지 */
        width: 100% !important;
        gap: 8px !important;
        margin-bottom: 8px !important;
    }
    
    /* 각 컬럼이 정확히 너비의 50%를 차지하도록 박제 (최소 너비 제한 해제) */
    [data-testid="stHorizontalBlock"] [data-testid="column"] {
        width: 50% !important;
        flex: 1 1 50% !important;
        min-width: 0px !important;      /* 스트림릿의 기본 300px 제한 해제 */
        max-width: 50% !important;
        padding: 0 !important;
    }

    /* 사분면 헤더 디자인 */
    .q-header {
        font-weight: 800;
        padding: 4px 2px;
        border-radius: 8px 8px 0 0;
        font-size: 0.7rem;
        text-align: center;
        color: #333;
        margin-bottom: 0px;
    }

    /* 박스 내용 영역 디자인 */
    .quadrant-container {
        border: 1px solid #f1f5f9;
        border-radius: 0 0 8px 8px;
        padding: 4px;
        background-color: #fafafa;
        min-height: 120px;
        max-height: 35vh; /* 화면의 1/3 정도를 차지하여 4개가 한눈에 들어오게 함 */
        overflow-y: auto;
    }

    /* 텍스트 크기 및 체크박스 모바일 최적화 */
    .stMarkdown div p { 
        font-size: 0.65rem !important; 
        line-height: 1.1 !important; 
        margin-bottom: 2px !important;
    }
    
    /* 위젯 간의 수직 간격 제거 */
    .stVerticalBlock { gap: 0rem !important; }
    
    /* 체크박스 영역 높이 극소화 */
    div[data-testid="stCheckbox"] { 
        margin-top: -5px !important;
        margin-bottom: -10px !important; 
    }

    /* 팝오버 버튼 스타일 */
    div[data-testid="stPopover"] > button {
        padding: 1px 4px !important;
        font-size: 0.55rem !important;
        min-height: 22px !important;
        height: 22px !important;
        border-radius: 4px !important;
        background-color: #f8fafc !important;
        width: 100% !important;
        border: 1px solid #e2e8f0 !important;
    }
    
    /* 체크박스 레이블 숨기기 */
    div[data-testid="stCheckbox"] label { display: none !important; }
    
    /* 불필요한 기본 요소 제거 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 데이터 관리 로직 ---
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
with c_title: st.markdown("##### 📋 하우젠 매트릭스")
with c_date: selected_date = st.date_input("날짜", datetime.now(), label_visibility="collapsed")

# --- 빠른 입력창 ---
with st.expander("🚀 빠른 기록", expanded=False):
    q_input = st.text_input("내용", key="q_in", placeholder="할 일 입력...", label_visibility="collapsed")
    b_row1 = st.columns(2)
    b_row2 = st.columns(2)
    b_grid = [b_row1[0], b_row1[1], b_row2[0], b_row2[1]]
    for i in range(4):
        if b_grid[i].button(f"{i+1}번 저장", use_container_width=True, key=f"q_btn_{i}"):
            add_task(q_input, i+1, selected_date)
            st.rerun()

# --- 매트릭스 설정 ---
quadrants = [
    {"num": 1, "title": "중요/긴급", "color": "#FFD6D6", "icon": "🔥"},
    {"num": 2, "title": "중요/비긴급", "color": "#D6FFDA", "icon": "🌱"},
    {"num": 3, "title": "긴급/비중요", "color": "#D6E9FF", "icon": "📢"},
    {"num": 4, "title": "비중요/비긴급", "color": "#E9D6FF", "icon": "☕"}
]

visible_tasks = [t for t in st.session_state.tasks if t['date'] == str(selected_date) or (t['date'] < str(selected_date) and not t['completed'])]

# --- 2x2 그리드 강제 배치 시작 ---
# 첫 번째 줄 (1, 2번 박스)
row1 = st.columns(2)
# 두 번째 줄 (3, 4번 박스)
row2 = st.columns(2)
grid = [row1[0], row1[1], row2[0], row2[1]]

for i, q in enumerate(quadrants):
    with grid[i]:
        # Header
        st.markdown(f'<div class="q-header" style="background-color: {q["color"]};">{q["icon"]} {q["title"]}</div>', unsafe_allow_html=True)
        
        # Add Button (Popover)
        with st.popover("➕", use_container_width=True):
            in_val = st.text_input("할 일", key=f"in_{q['num']}", label_visibility="collapsed", placeholder="내용...")
            if st.button("저장", key=f"btn_{q['num']}", use_container_width=True):
                add_task(in_val, q['num'], selected_date)
                st.rerun()
        
        # Task List Area
        q_tasks = [t for t in visible_tasks if t['quadrant'] == q['num']]
        
        st.markdown('<div class="quadrant-container">', unsafe_allow_html=True)
        if not q_tasks:
            st.markdown("<div style='text-align:center; padding:10px; color:#cbd5e1; font-size:0.6rem;'>-</div>", unsafe_allow_html=True)
        
        for task in q_tasks:
            t_col1, t_col2, t_col3 = st.columns([0.2, 0.65, 0.15])
            
            with t_col1:
                new_status = st.checkbox("", value=task['completed'], key=f"chk_{task['id']}")
                if new_status != task['completed']:
                    task['completed'] = new_status
                    st.rerun()
            
            with t_col2:
                txt = task['text']
                if task['completed']: txt = f"~~{txt}~~"
                if task['date'] < str(selected_date): txt = f"⏳{txt}"
                st.markdown(f"<div style='font-size:0.65rem; padding-top:2px;'>{txt}</div>", unsafe_allow_html=True)
            
            with t_col3:
                if st.button("×", key=f"del_{task['id']}"):
                    st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.caption("Focus Matrix 2x2 Portrait Fixed Layout")
