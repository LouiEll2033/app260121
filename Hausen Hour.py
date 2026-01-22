import streamlit as st
import requests
import json
import uuid
from datetime import datetime, timedelta

# --- 페이지 설정 ---
st.set_page_config(page_title="아이젠하워 매트릭스", layout="wide", initial_sidebar_state="collapsed")

# --- 고급 스타일 커스텀 (겹침 방지 및 모바일 최적화) ---
st.markdown("""
    <style>
    /* 기본 배경 및 여백 설정 */
    .main { background-color: #f8fafc; }
    .block-container { 
        padding: 0.75rem !important; 
    }
    
    /* [강력 권장] 모바일 세로 모드에서도 절대 깨지지 않는 2x2 그리드 */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        width: 100% !important;
        gap: 12px !important;
        margin-bottom: 12px !important;
    }
    
    [data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        width: 50% !important;
        min-width: 0px !important;
        flex-basis: 50% !important;
        flex-grow: 1 !important;
        flex-shrink: 0 !important;
        padding: 0 !important;
    }

    /* 사분면 헤더 (세련된 그라데이션 및 그림자) */
    .q-header {
        font-weight: 800;
        padding: 10px 4px;
        font-size: 0.7rem;
        text-align: center;
        color: #1e293b;
        border-radius: 12px 12px 0 0;
        box-shadow: inset 0 -2px 4px rgba(0,0,0,0.02);
    }

    /* 할 일 목록 영역 (글씨 잘림 및 버튼 겹침 방지) */
    .quadrant-container {
        padding: 8px;
        background-color: #ffffff;
        min-height: 160px;
        max-height: 40vh;
        overflow-y: auto;
        border: 1px solid #e2e8f0;
        border-radius: 0 0 12px 12px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }

    /* 할 일 텍스트 가독성 (긴 문장 자동 줄바꿈) */
    .task-text { 
        font-size: 0.75rem !important; 
        line-height: 1.4 !important; 
        margin: 0 !important;
        word-wrap: break-word !important;
        overflow-wrap: anywhere !important;
        white-space: normal !important;
        color: #334155;
    }
    
    /* 체크박스와 삭제 버튼 겹침 방지 */
    .task-row {
        display: flex;
        align-items: flex-start;
        padding: 4px 0;
        border-bottom: 1px solid #f1f5f9;
    }
    
    /* ➕ 추가 버튼 (팝오버) 스타일 최적화 - 겹침 방지 핵심 */
    div[data-testid="stPopover"] {
        margin: 4px 0 !important;
        width: 100% !important;
    }
    
    div[data-testid="stPopover"] > button {
        padding: 4px 0 !important;
        font-size: 0.65rem !important;
        font-weight: 700 !important;
        min-height: 30px !important;
        border-radius: 8px !important;
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        color: #64748b !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
        width: 100% !important;
    }
    
    /* 체크박스 크기 조절 */
    div[data-testid="stCheckbox"] { 
        padding-top: 2px !important;
    }
    div[data-testid="stCheckbox"] label { display: none !important; }
    
    /* 스크롤바 세련된 디자인 */
    ::-webkit-scrollbar { width: 3px; }
    ::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 10px; }
    
    /* 불필요한 기본 UI 제거 */
    #MainMenu, footer, header { visibility: hidden; }

    /* 상단 영역 슬림화 */
    .stDateInput {
        margin-top: -10px !important;
    }
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
c_title, c_date = st.columns([1.1, 0.9])
with c_title: 
    st.markdown("<h3 style='margin:0; color:#0f172a; font-size:1.3rem; letter-spacing:-0.5px;'>Focus Matrix</h3>", unsafe_allow_html=True)
with c_date: 
    selected_date = st.date_input("날짜", datetime.now(), label_visibility="collapsed")

# --- 매트릭스 사분면 설정 ---
quadrants = [
    {"num": 1, "title": "중요 & 긴급", "sub": "즉시 처리", "color": "#fee2e2", "icon": "🔥"},
    {"num": 2, "title": "중요 & 비긴급", "sub": "계획 수립", "color": "#dcfce7", "icon": "📅"},
    {"num": 3, "title": "긴급 & 비중요", "sub": "위임/거절", "color": "#dbeafe", "icon": "👤"},
    {"num": 4, "title": "비중요 & 비긴급", "sub": "삭제/보류", "color": "#f1f5f9", "icon": "🗑️"}
]

visible_tasks = [t for t in st.session_state.tasks if t['date'] == str(selected_date) or (t['date'] < str(selected_date) and not t['completed'])]

# --- 2x2 그리드 렌더링 ---
row1 = st.columns(2)
row2 = st.columns(2)
grid = [row1[0], row1[1], row2[0], row2[1]]

for i, q in enumerate(quadrants):
    with grid[i]:
        # 헤더 섹션
        st.markdown(f'''
            <div class="q-header" style="background-color: {q["color"]};">
                <div style="font-size:0.8rem;">{q["icon"]} {q["title"]}</div>
                <div style="font-size:0.5rem; opacity:0.6; font-weight:400;">{q["sub"]}</div>
            </div>
        ''', unsafe_allow_html=True)
        
        # ➕ 추가 버튼 (헤더와 겹치지 않도록 별도 공간 확보)
        with st.popover("➕ 할 일", use_container_width=True):
            in_val = st.text_input("할 일 입력", key=f"in_{q['num']}", label_visibility="collapsed", placeholder="무엇을 할까요?")
            if st.button("저장", key=f"btn_{q['num']}", use_container_width=True):
                add_task(in_val, q['num'], selected_date)
                st.rerun()
        
        # 목록 리스트 영역
        q_tasks = [t for t in visible_tasks if t['quadrant'] == q['num']]
        
        st.markdown('<div class="quadrant-container">', unsafe_allow_html=True)
        if not q_tasks:
            st.markdown("<div style='text-align:center; padding-top:40px; color:#94a3b8; font-size:0.6rem; font-style:italic;'>내용 없음</div>", unsafe_allow_html=True)
        
        for task in q_tasks:
            # 체크박스 | 텍스트 | 삭제 버튼 레이아웃
            t_col1, t_col2, t_col3 = st.columns([0.2, 0.65, 0.15])
            
            with t_col1:
                new_status = st.checkbox("", value=task['completed'], key=f"chk_{task['id']}")
                if new_status != task['completed']:
                    task['completed'] = new_status
                    st.rerun()
            
            with t_col2:
                txt = task['text']
                style = "color:#cbd5e1; text-decoration:line-through;" if task['completed'] else "color:#334155; font-weight:500;"
                prefix = "<span style='color:#f59e0b;'>⏳ </span>" if task['date'] < str(selected_date) else ""
                st.markdown(f"<div class='task-text' style='{style}'>{prefix}{txt}</div>", unsafe_allow_html=True)
            
            with t_col3:
                if st.button("×", key=f"del_{task['id']}", help="삭제"):
                    st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.caption("Focus Matrix Pro v3.5 | Clean 2x2 Layout")
