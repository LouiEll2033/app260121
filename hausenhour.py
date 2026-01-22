import streamlit as st
from datetime import datetime
import uuid

# --- 페이지 설정 ---
st.set_page_config(page_title="하우젠 매트릭스", layout="wide", initial_sidebar_state="expanded")

# --- 화면 보기 모드 선택 ---
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = "Mobile"

with st.sidebar:
    st.title("설정")
    st.session_state.view_mode = st.radio("화면 보기 버전", ["Mobile", "PC"], index=0 if st.session_state.view_mode == "Mobile" else 1)
    st.info("Mobile 모드는 한 화면에 모든 사분면을 고정하고, PC 모드는 더 넓고 큰 화면을 제공합니다.")

# --- 동적 스타일 적용 ---
if st.session_state.view_mode == "Mobile":
    # 모바일 최적화 스타일 (기존 버전 유지)
    st.markdown("""
        <style>
        [data-testid="stHeader"] {visibility: hidden; height: 0;}
        footer {visibility: hidden;}
        .main { background-color: #ffffff; overflow: hidden; }
        .block-container { 
            padding-top: 0.5rem !important; 
            padding-bottom: 0 !important; 
            padding-left: 0.2rem !important; 
            padding-right: 0.2rem !important;
            max-width: 100vw !important;
            overflow-x: hidden !important;
        }
        [data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            width: 100% !important;
            gap: 4px !important;
        }
        [data-testid="stHorizontalBlock"] [data-testid="column"] {
            width: calc(50% - 2px) !important;
            flex: 1 1 calc(50% - 2px) !important;
            min-width: 0 !important;
            max-width: 50% !important;
        }
        .q-header {
            font-weight: 800; padding: 4px 0; border-radius: 8px 8px 0 0;
            font-size: 0.65rem; text-align: center; color: #333;
            border: 1px solid rgba(0,0,0,0.05); line-height: 1;
        }
        .quadrant-container {
            border: 1px solid #f1f5f9; border-radius: 0 0 8px 8px;
            padding: 4px; background-color: #fafafa;
            height: 38vh; overflow-y: auto;
        }
        .stMarkdown div p { font-size: 0.6rem !important; line-height: 1.1 !important; word-break: break-all; }
        div[data-testid="stCheckbox"] { margin-top: -12px !important; margin-bottom: -14px !important; transform: scale(0.8); }
        div[data-testid="stCheckbox"] label { display: none !important; }
        .stButton>button { font-size: 0.55rem; height: 22px; min-height: 22px; }
        div[data-testid="stPopover"] > button { height: 22px !important; font-size: 0.55rem !important; }
        </style>
        """, unsafe_allow_html=True)
else:
    # PC 최적화 스타일 (더 크게, 여유 있게)
    st.markdown("""
        <style>
        .main { background-color: #f8fafc; }
        .block-container { 
            padding-top: 2rem !important; 
            max-width: 1200px !important;
        }
        [data-testid="stHorizontalBlock"] { gap: 20px !important; margin-bottom: 20px !important; }
        .q-header {
            font-weight: 800; padding: 12px; border-radius: 12px 12px 0 0;
            font-size: 1rem; text-align: center; color: #333;
        }
        .quadrant-container {
            border: 1px solid #e2e8f0; border-radius: 0 0 12px 12px;
            padding: 15px; background-color: #ffffff;
            min-height: 400px; overflow-y: auto;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .stMarkdown div p { font-size: 1rem !important; line-height: 1.5 !important; }
        .stButton>button { border-radius: 8px; font-size: 0.9rem; }
        div[data-testid="stCheckbox"] { margin-bottom: 5px !important; }
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
h_col1, h_col2 = st.columns([1, 1])
with h_col1:
    st.markdown(f"### 📋 하우젠 ({st.session_state.view_mode} Ver.)")
with h_col2:
    selected_date = st.date_input("날짜 선택", datetime.now(), label_visibility="collapsed")

# --- 매트릭스 설정 ---
quadrants = [
    {"num": 1, "title": "중요/긴급", "color": "#FFD6D6", "icon": "🔥"},
    {"num": 2, "title": "중요/비긴급", "color": "#D6FFDA", "icon": "🌱"},
    {"num": 3, "title": "긴급/비중요", "color": "#D6E9FF", "icon": "📢"},
    {"num": 4, "title": "비중요/비긴급", "color": "#E9D6FF", "icon": "☕"}
]

visible_tasks = [t for t in st.session_state.tasks if t['date'] == str(selected_date) or (t['date'] < str(selected_date) and not t['completed'])]

# --- 2x2 그리드 배치 ---
row1 = st.columns(2)
row2 = st.columns(2)
grid = [row1[0], row1[1], row2[0], row2[1]]

for i, q in enumerate(quadrants):
    with grid[i]:
        st.markdown(f'<div class="q-header" style="background-color: {q["color"]};">{q["icon"]} {q["title"]}</div>', unsafe_allow_html=True)
        
        with st.popover("➕ 추가", use_container_width=True):
            in_val = st.text_input("할 일 입력", key=f"in_{q['num']}", placeholder="입력 후 엔터", label_visibility="collapsed")
            if st.button("저장", key=f"btn_{q['num']}", use_container_width=True):
                add_task(in_val, q['num'], selected_date)
                st.rerun()

        st.markdown('<div class="quadrant-container">', unsafe_allow_html=True)
        q_tasks = [t for t in visible_tasks if t['quadrant'] == q['num']]
        
        for task in q_tasks:
            # PC 모드와 모바일 모드에서 체크박스 컬럼 비율 조정
            col_ratio = [0.1, 0.8, 0.1] if st.session_state.view_mode == "PC" else [0.2, 0.65, 0.15]
            t_col1, t_col2, t_col3 = st.columns(col_ratio)
            
            with t_col1:
                if st.checkbox("", value=task['completed'], key=f"chk_{task['id']}", label_visibility="collapsed" if st.session_state.view_mode == "Mobile" else "visible"):
                    if not task['completed']:
                        task['completed'] = True
                        st.rerun()
                elif task['completed']:
                    task['completed'] = False
                    st.rerun()
            with t_col2:
                txt = task['text']
                if task['completed']: txt = f"~~{txt}~~"
                if task['date'] < str(selected_date): txt = f"⏳{txt}"
                st.markdown(f"<div>{txt}</div>", unsafe_allow_html=True)
            with t_col3:
                if st.button("×", key=f"del_{task['id']}"):
                    st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.view_mode == "PC":
    st.write("")
    st.caption("Eisenhower Matrix - PC Optimized View")
else:
    st.caption("Focus Matrix Fixed 2x2")
