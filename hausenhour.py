import streamlit as st
from datetime import datetime
import uuid

# --- 페이지 설정 ---
st.set_page_config(page_title="하우젠 매트릭스", layout="wide", initial_sidebar_state="collapsed")

# --- 스타일 커스텀 (이미지 느낌의 2x2 그리드 고정) ---
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .block-container { padding: 1rem !important; }
    
    /* 2x2 그리드 강제 고정 */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 10px !important;
    }
    [data-testid="stHorizontalBlock"] [data-testid="column"] {
        width: 50% !important;
        flex: 1 1 50% !important;
        min-width: 0px !important;
    }

    /* 사분면 헤더 스타일 */
    .q-header {
        font-weight: 800;
        padding: 8px;
        border-radius: 12px 12px 0 0;
        font-size: 0.8rem;
        text-align: center;
        color: #333;
        margin-bottom: 0px;
        border: 1px solid rgba(0,0,0,0.05);
    }

    /* 컨테이너 스타일 */
    .quadrant-container {
        border: 1px solid #f1f5f9;
        border-radius: 0 0 12px 12px;
        padding: 8px;
        background-color: #ffffff;
        min-height: 250px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }

    /* 할 일 아이템 스타일 */
    .task-item {
        background-color: #f8fafc;
        border-radius: 8px;
        padding: 6px 10px;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        border: 1px solid #f1f5f9;
    }
    
    /* 버튼 스타일 최적화 */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        padding: 0px;
        font-size: 0.7rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 데이터 관리 ---
if 'tasks' not in st.session_state:
    st.session_state.tasks = []

def add_task(text, q_num, date):
    if not text.strip(): return
    st.session_state.tasks.append({
        "id": str(uuid.uuid4()),
        "text": text,
        "quadrant": q_num,
        "completed": False,
        "date": str(date)
    })

# --- 상단 헤더 ---
col_t, col_d = st.columns([2, 1])
with col_t:
    st.markdown("### 📋 하우젠 매트릭스")
with col_d:
    selected_date = st.date_input("날짜", datetime.now(), label_visibility="collapsed")

# --- 매트릭스 설정 ---
quadrants = [
    {"num": 1, "title": "중요 / 긴급", "color": "#FFD6D6", "icon": "🔥"},
    {"num": 2, "title": "중요 / 비긴급", "color": "#D6FFDA", "icon": "🌱"},
    {"num": 3, "title": "긴급 / 비중요", "color": "#D6E9FF", "icon": "📢"},
    {"num": 4, "title": "비중요 / 비긴급", "color": "#E9D6FF", "icon": "☕"}
]

# 필터링된 태스크 (오늘 날짜 혹은 과거 미완료 건)
visible_tasks = [t for t in st.session_state.tasks if t['date'] == str(selected_date) or (t['date'] < str(selected_date) and not t['completed'])]

# --- 2x2 그리드 레이아웃 ---
row1 = st.columns(2)
row2 = st.columns(2)
grid = [row1[0], row1[1], row2[0], row2[1]]

for i, q in enumerate(quadrants):
    with grid[i]:
        # Header
        st.markdown(f'<div class="q-header" style="background-color: {q["color"]};">{q["icon"]} {q["title"]}</div>', unsafe_allow_html=True)
        
        # Input Area (Popover)
        with st.popover("➕ 추가", use_container_width=True):
            in_val = st.text_input("할 일", key=f"in_{q['num']}", placeholder="내용 입력...", label_visibility="collapsed")
            if st.button("저장", key=f"btn_{q['num']}", use_container_width=True):
                add_task(in_val, q['num'], selected_date)
                st.rerun()

        # Task List
        st.markdown('<div class="quadrant-container">', unsafe_allow_html=True)
        q_tasks = [t for t in visible_tasks if t['quadrant'] == q['num']]
        
        if not q_tasks:
            st.markdown("<div style='text-align:center; padding-top:40px; color:#cbd5e1; font-size:0.7rem;'>-</div>", unsafe_allow_html=True)
        
        for task in q_tasks:
            t_col1, t_col2, t_col3 = st.columns([0.15, 0.7, 0.15])
            
            with t_col1:
                if st.checkbox("", value=task['completed'], key=f"chk_{task['id']}", label_visibility="collapsed"):
                    task['completed'] = True
                    st.rerun()
                elif task['completed'] == True: # 체크 해제 시
                    task['completed'] = False
                    st.rerun()
            
            with t_col2:
                display_text = task['text']
                if task['completed']:
                    display_text = f"~~{display_text}~~"
                if task['date'] < str(selected_date):
                    display_text = f"⏳ {display_text}"
                st.markdown(f"<div style='font-size:0.75rem; padding-top:4px;'>{display_text}</div>", unsafe_allow_html=True)
            
            with t_col3:
                if st.button("×", key=f"del_{task['id']}"):
                    st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.caption("Focus Matrix 2x2 Fixed Layout")