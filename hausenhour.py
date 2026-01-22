import streamlit as st
from datetime import datetime
import uuid

# --- 페이지 설정 ---
st.set_page_config(page_title="하우젠 매트릭스", layout="wide", initial_sidebar_state="collapsed")

# --- 화면 보기 모드 선택 ---
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = "Mobile"

with st.sidebar:
    st.title("📱 화면 설정")
    st.session_state.view_mode = st.radio(
        "버전 선택", 
        ["Mobile", "PC"], 
        index=0 if st.session_state.view_mode == "Mobile" else 1
    )
    st.divider()
    st.info("Mobile 모드는 세로 화면 비율에 최적화되어 스크롤 없이 박제됩니다.")

# --- 디자인 개선 및 모바일 박제 스타일 ---
if st.session_state.view_mode == "Mobile":
    st.markdown("""
        <style>
        /* 1. 전체 배경 및 스크롤 차단 */
        html, body, [data-testid="stAppViewContainer"] {
            overflow: hidden !important;
            height: 100vh !important;
            background-color: #fcfcfc;
        }
        [data-testid="stHeader"] { visibility: hidden; height: 0; }
        footer { visibility: hidden; }
        
        /* 2. 메인 컨테이너 최적화 (여백 확보) */
        .block-container { 
            padding-top: 0.8rem !important; 
            padding-bottom: 0 !important; 
            padding-left: 0.5rem !important; 
            padding-right: 0.5rem !important;
            height: 100vh !important;
            max-width: 100vw !important;
            display: flex !important;
            flex-direction: column !important;
            overflow: hidden !important;
        }
        
        /* 3. 위젯 간 간격 조정 */
        [data-testid="stVerticalBlock"] { gap: 0rem !important; }
        [data-testid="stHorizontalBlock"] { gap: 8px !important; margin-bottom: 8px !important; }
        div[data-testid="stVerticalBlockBorderWrapper"] > div > div { gap: 0rem !important; }
        div[data-testid="element-container"] { margin-bottom: 0px !important; }

        /* 4. 2x2 그리드 고정 */
        [data-testid="stHorizontalBlock"] [data-testid="column"] {
            width: calc(50% - 4px) !important;
            flex: 1 1 calc(50% - 4px) !important;
            min-width: 0 !important;
            max-width: 50% !important;
        }

        /* 5. 사분면 디자인 (헤더 두께 강화 및 비율 조정) */
        .q-header {
            font-weight: 800; 
            padding: 10px 0; /* 헤더 두께를 키워 안정감 부여 */
            border-radius: 12px 12px 0 0;
            font-size: 0.85rem; 
            text-align: center; 
            color: #333;
            border: 1px solid rgba(0,0,0,0.05);
            line-height: 1.2;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        }

        .quadrant-container {
            border: 1px solid #e2e8f0; 
            border-radius: 0 0 12px 12px;
            padding: 8px; 
            background-color: #ffffff;
            /* 세로 비율을 36vh로 조정하여 2x2가 화면에 꽉 차게 배치 */
            height: 36vh; 
            overflow-y: auto;
            overflow-x: hidden;
            margin-bottom: 4px;
        }

        /* 6. 항목 텍스트 스타일 */
        .stMarkdown div p { 
            font-size: 0.78rem !important; 
            line-height: 1.3 !important; 
            margin: 0 !important;
            color: #1e293b;
        }
        
        /* 체크박스 크기 조절 */
        div[data-testid="stCheckbox"] { 
            margin-top: -8px !important; 
            margin-bottom: -10px !important; 
            transform: scale(0.95); 
        }
        div[data-testid="stCheckbox"] label { display: none !important; }

        /* 버튼 디자인 (더욱 뚜렷하게) */
        .stButton>button, div[data-testid="stPopover"] > button {
            height: 28px !important; 
            min-height: 28px !important;
            font-size: 0.7rem !important;
            border-radius: 8px !important;
            background-color: #ffffff !important;
            border: 1px solid #cbd5e1 !important;
            color: #475569 !important;
            font-weight: 600 !important;
        }
        
        div[data-testid="stDateInput"] { transform: scale(0.95); transform-origin: top right; }
        </style>
        """, unsafe_allow_html=True)
else:
    # PC 모드 스타일 (여유로운 레이아웃)
    st.markdown("""
        <style>
        .main { background-color: #f8fafc; }
        .block-container { padding-top: 2.5rem !important; max-width: 1100px !important; }
        .q-header { font-weight: 800; padding: 18px; border-radius: 16px 16px 0 0; font-size: 1.15rem; text-align: center; }
        .quadrant-container { border: 1px solid #e2e8f0; border-radius: 0 0 16px 16px; padding: 24px; background-color: #ffffff; min-height: 450px; overflow-y: auto; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
        .stMarkdown div p { font-size: 1rem !important; }
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
    st.markdown("<h3 style='margin:0; padding:0; color:#0f172a; font-weight:900;'>📋 하우젠</h3>", unsafe_allow_html=True)
with h_col2:
    selected_date = st.date_input("날짜", datetime.now(), label_visibility="collapsed")

# --- 매트릭스 설정 (파스텔 톤) ---
quadrants = [
    {"num": 1, "title": "중요 / 긴급", "color": "#FFD6D6", "icon": "🔥"},
    {"num": 2, "title": "중요 / 비긴급", "color": "#D6FFDA", "icon": "🌱"},
    {"num": 3, "title": "긴급 / 비중요", "color": "#D6E9FF", "icon": "📢"},
    {"num": 4, "title": "비중요 / 비긴급", "color": "#E9D6FF", "icon": "☕"}
]

visible_tasks = [t for t in st.session_state.tasks if t['date'] == str(selected_date) or (t['date'] < str(selected_date) and not t['completed'])]

# --- 2x2 그리드 배치 ---
row1 = st.columns(2)
row2 = st.columns(2)
grid = [row1[0], row1[1], row2[0], row2[1]]

for i, q in enumerate(quadrants):
    with grid[i]:
        # Quadrant Header
        st.markdown(f'<div class="q-header" style="background-color: {q["color"]};">{q["icon"]} {q["title"]}</div>', unsafe_allow_html=True)
        
        # Quadrant Container
        st.markdown('<div class="quadrant-container">', unsafe_allow_html=True)
        
        # Add Task Button
        with st.popover("➕ 추가", use_container_width=True):
            in_val = st.text_input("할 일 입력", key=f"in_{q['num']}", placeholder="입력 후 엔터", label_visibility="collapsed")
            if st.button("저장하기", key=f"btn_{q['num']}", use_container_width=True):
                add_task(in_val, q['num'], selected_date)
                st.rerun()
        
        q_tasks = [t for t in visible_tasks if t['quadrant'] == q['num']]
        
        for task in q_tasks:
            t_col1, t_col2, t_col3 = st.columns([0.18, 0.67, 0.15])
            with t_col1:
                if st.checkbox("", value=task['completed'], key=f"chk_{task['id']}", label_visibility="collapsed"):
                    task['completed'] = not task['completed']
                    st.rerun()
            with t_col2:
                txt = task['text']
                if task['completed']: 
                    txt = f"<span style='text-decoration: line-through; color: #94a3b8;'>{txt}</span>"
                if task['date'] < str(selected_date): 
                    txt = f"⏳ {txt}"
                st.markdown(f"<div style='padding-top:3px;'>{txt}</div>", unsafe_allow_html=True)
            with t_col3:
                if st.button("×", key=f"del_{task['id']}", help="삭제"):
                    st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
