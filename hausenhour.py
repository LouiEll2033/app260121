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
    st.info("Mobile 모드는 세로 화면에서도 스크롤 없이 사분면 전체를 한 화면에 박제합니다.")

# --- 초강력 모바일 박제 스타일 (세로 모드 최적화) ---
if st.session_state.view_mode == "Mobile":
    st.markdown("""
        <style>
        /* 1. 전체 레이아웃 강제 고정 */
        html, body, [data-testid="stAppViewContainer"] {
            overflow: hidden !important;
            height: 100vh !important;
        }
        [data-testid="stHeader"] { visibility: hidden; height: 0; }
        footer { visibility: hidden; }
        
        /* 2. 메인 컨테이너 패딩 최소화 */
        .block-container { 
            padding-top: 0.2rem !important; 
            padding-bottom: 0 !important; 
            padding-left: 0.1rem !important; 
            padding-right: 0.1rem !important;
            height: 100vh !important;
            display: flex !important;
            flex-direction: column !important;
            overflow: hidden !important;
        }
        
        /* 3. Streamlit 기본 간격 제거 */
        [data-testid="stVerticalBlock"] { gap: 0rem !important; }
        [data-testid="stHorizontalBlock"] { gap: 2px !important; margin: 0 !important; padding: 0 !important; }
        div[data-testid="stVerticalBlockBorderWrapper"] > div > div { gap: 0rem !important; }

        /* 4. 2x2 그리드 강제 고정 */
        [data-testid="stHorizontalBlock"] [data-testid="column"] {
            width: calc(50% - 1px) !important;
            flex: 1 1 calc(50% - 1px) !important;
            min-width: 0 !important;
            max-width: 50% !important;
        }

        /* 5. 사분면 높이 극단적 최적화 (세로 모드용) */
        .q-header {
            font-weight: 800; padding: 1px 0; border-radius: 4px 4px 0 0;
            font-size: 0.6rem; text-align: center; color: #333;
            border: 1px solid rgba(0,0,0,0.05); line-height: 1;
        }

        .quadrant-container {
            border: 1px solid #f1f5f9; border-radius: 0 0 4px 4px;
            padding: 2px; background-color: #fafafa;
            /* 높이를 더 낮추어 헤더/버전선택기 공간 확보 */
            height: 32vh; 
            overflow-y: auto;
            overflow-x: hidden;
        }

        /* 6. 할 일 리스트 압축 */
        .stMarkdown div p { font-size: 0.65rem !important; line-height: 1.0 !important; margin: 0 !important; }
        
        /* 체크박스 영역 최소화 */
        div[data-testid="stCheckbox"] { 
            margin-top: -14px !important; 
            margin-bottom: -16px !important; 
            transform: scale(0.7); 
        }
        div[data-testid="stCheckbox"] label { display: none !important; }

        /* 버튼 및 팝오버 크기 최소화 (세로 모드 공간 확보의 핵심) */
        .stButton>button, div[data-testid="stPopover"] > button {
            height: 16px !important; 
            min-height: 16px !important;
            font-size: 0.5rem !important;
            padding: 0 !important;
            line-height: 1 !important;
            border-radius: 2px !important;
        }
        
        /* 상단 날짜 입력창 크기 축소 */
        div[data-testid="stDateInput"] { transform: scale(0.75); transform-origin: top right; margin-top: -5px; }
        h6 { font-size: 0.7rem !important; margin: 0 !important; }
        </style>
        """, unsafe_allow_html=True)
else:
    # PC 모드 스타일
    st.markdown("""
        <style>
        .main { background-color: #f1f5f9; }
        .block-container { padding-top: 2rem !important; max-width: 1100px !important; }
        .q-header { font-weight: 800; padding: 12px; border-radius: 12px 12px 0 0; font-size: 1rem; text-align: center; }
        .quadrant-container { border: 1px solid #e2e8f0; border-radius: 0 0 12px 12px; padding: 15px; background-color: #ffffff; min-height: 400px; overflow-y: auto; }
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
    st.markdown("<h6 style='margin:0; padding:0;'>📋 하우젠</h6>", unsafe_allow_html=True)
with h_col2:
    selected_date = st.date_input("날짜", datetime.now(), label_visibility="collapsed")

# --- 매트릭스 설정 ---
quadrants = [
    {"num": 1, "title": "중요/긴급", "color": "#FFD6D6", "icon": "🔥"},
    {"num": 2, "title": "중요/비긴급", "color": "#D6FFDA", "icon": "🌱"},
    {"num": 3, "title": "긴급/비중요", "color": "#D6E9FF", "icon": "📢"},
    {"num": 4, "title": "비중요/비긴급", "color": "#E9D6FF", "icon": "☕"}
]

visible_tasks = [t for t in st.session_state.tasks if t['date'] == str(selected_date) or (t['date'] < str(selected_date) and not t['completed'])]

# --- 2x2 그리드 배치 ---
row1_cols = st.columns(2)
row2_cols = st.columns(2)
grid = [row1_cols[0], row1_cols[1], row2_cols[0], row2_cols[1]]

for i, q in enumerate(quadrants):
    with grid[i]:
        # 헤더
        st.markdown(f'<div class="q-header" style="background-color: {q["color"]};">{q["icon"]} {q["title"]}</div>', unsafe_allow_html=True)
        
        # 추가 버튼
        with st.popover("➕", use_container_width=True):
            in_val = st.text_input("할 일", key=f"in_{q['num']}", placeholder="입력 후 엔터", label_visibility="collapsed")
            if st.button("저장", key=f"btn_{q['num']}", use_container_width=True):
                add_task(in_val, q['num'], selected_date)
                st.rerun()

        # 리스트 영역
        st.markdown('<div class="quadrant-container">', unsafe_allow_html=True)
        q_tasks = [t for t in visible_tasks if t['quadrant'] == q['num']]
        
        for task in q_tasks:
            ratio = [0.25, 0.6, 0.15] if st.session_state.view_mode == "Mobile" else [0.15, 0.7, 0.15]
            t_col1, t_col2, t_col3 = st.columns(ratio)
            
            with t_col1:
                if st.checkbox("", value=task['completed'], key=f"chk_{task['id']}", label_visibility="collapsed"):
                    task['completed'] = not task['completed']
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
