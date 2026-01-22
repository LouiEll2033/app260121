import streamlit as st
from datetime import datetime
import uuid

# --- 페이지 설정 ---
st.set_page_config(page_title="하우젠 매트릭스", layout="wide", initial_sidebar_state="expanded")

# --- 화면 보기 모드 선택 ---
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = "Mobile"

with st.sidebar:
    st.title("📱 화면 설정")
    st.session_state.view_mode = st.radio(
        "버전 선택", 
        ["Mobile", "PC"], 
        index=0 if st.session_state.view_mode == "Mobile" else 1,
        help="언제든 버전을 전환하여 기기에 최적화된 화면을 볼 수 있습니다."
    )
    st.divider()
    st.info("💡 **Mobile 모드**: 세로 모드 가독성에 최적화되어 한 화면에 고정됩니다.\n\n💡 **PC 모드**: 넓은 화면에서 많은 내용을 한눈에 확인하기 좋습니다.")

# --- 동적 스타일 적용 ---
if st.session_state.view_mode == "Mobile":
    # 모바일 세로 모드 가독성 중심 스타일
    st.markdown("""
        <style>
        [data-testid="stHeader"] {visibility: hidden; height: 0;}
        footer {visibility: hidden;}
        .main { background-color: #ffffff; overflow: hidden; }
        
        /* 전체 컨테이너 패딩 최적화 */
        .block-container { 
            padding-top: 0.5rem !important; 
            padding-bottom: 0 !important; 
            padding-left: 0.4rem !important; 
            padding-right: 0.4rem !important;
            max-width: 100vw !important;
            overflow-x: hidden !important;
        }
        
        /* 2열 강제 고정 */
        [data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            width: 100% !important;
            gap: 6px !important;
        }
        
        [data-testid="stHorizontalBlock"] [data-testid="column"] {
            width: calc(50% - 3px) !important;
            flex: 1 1 calc(50% - 3px) !important;
            min-width: 0 !important;
            max-width: 50% !important;
        }

        /* 사분면 헤더 (가독성 위해 폰트 상향) */
        .q-header {
            font-weight: 800; padding: 6px 0; border-radius: 10px 10px 0 0;
            font-size: 0.75rem; text-align: center; color: #333;
            border: 1px solid rgba(0,0,0,0.05); line-height: 1.2;
        }

        /* 컨테이너 높이 (한 화면에 쏙 들어오게 최적화) */
        .quadrant-container {
            border: 1px solid #f1f5f9; border-radius: 0 0 10px 10px;
            padding: 6px; background-color: #fafafa;
            height: 37vh; overflow-y: auto;
        }

        /* 할 일 텍스트 가독성 (0.6 -> 0.75rem으로 상향) */
        .stMarkdown div p { 
            font-size: 0.75rem !important; 
            line-height: 1.3 !important; 
            word-break: break-all;
            color: #1e293b;
        }

        /* 체크박스 터치 편의성 */
        div[data-testid="stCheckbox"] { 
            margin-top: -8px !important; 
            margin-bottom: -10px !important; 
            transform: scale(0.9); 
        }
        div[data-testid="stCheckbox"] label { display: none !important; }

        /* 버튼 및 팝오버 크기 최적화 */
        .stButton>button { font-size: 0.65rem; height: 26px; min-height: 26px; border-radius: 6px; }
        div[data-testid="stPopover"] > button { height: 26px !important; font-size: 0.65rem !important; border-radius: 6px !important; }
        </style>
        """, unsafe_allow_html=True)
else:
    # PC 최적화 스타일 (시원한 레이아웃)
    st.markdown("""
        <style>
        .main { background-color: #f8fafc; }
        .block-container { 
            padding-top: 2rem !important; 
            max-width: 1100px !important;
        }
        [data-testid="stHorizontalBlock"] { gap: 16px !important; margin-bottom: 16px !important; }
        .q-header {
            font-weight: 800; padding: 14px; border-radius: 14px 14px 0 0;
            font-size: 1.1rem; text-align: center; color: #1e293b;
        }
        .quadrant-container {
            border: 1px solid #e2e8f0; border-radius: 0 0 14px 14px;
            padding: 16px; background-color: #ffffff;
            min-height: 420px; overflow-y: auto;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }
        .stMarkdown div p { font-size: 1rem !important; line-height: 1.6 !important; }
        .stButton>button { border-radius: 8px; font-size: 0.95rem; font-weight: 600; }
        div[data-testid="stCheckbox"] { margin-bottom: 6px !important; }
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
    st.markdown(f"### 📋 하우젠 매트릭스")
with h_col2:
    selected_date = st.date_input("날짜 선택", datetime.now(), label_visibility="collapsed")

# --- 매트릭스 설정 ---
quadrants = [
    {"num": 1, "title": "중요/긴급", "color": "#FFD6D6", "icon": "🔥"},
    {"num": 2, "title": "중요/비긴급", "color": "#D6FFDA", "icon": "🌱"},
    {"num": 3, "title": "긴급/비중요", "color": "#D6E9FF", "icon": "📢"},
    {"num": 4, "title": "비중요/비긴급", "color": "#E9D6FF", "icon": "☕"}
]

# 필터링: 선택된 날짜의 태스크 + 과거 미완료 태스크
visible_tasks = [t for t in st.session_state.tasks if t['date'] == str(selected_date) or (t['date'] < str(selected_date) and not t['completed'])]

# --- 2x2 그리드 배치 ---
row1 = st.columns(2)
row2 = st.columns(2)
grid = [row1[0], row1[1], row2[0], row2[1]]

for i, q in enumerate(quadrants):
    with grid[i]:
        st.markdown(f'<div class="q-header" style="background-color: {q["color"]};">{q["icon"]} {q["title"]}</div>', unsafe_allow_html=True)
        
        with st.popover("➕ 추가", use_container_width=True):
            in_val = st.text_input("할 일", key=f"in_{q['num']}", placeholder="할 일을 적고 엔터", label_visibility="collapsed")
            if st.button("저장", key=f"btn_{q['num']}", use_container_width=True):
                add_task(in_val, q['num'], selected_date)
                st.rerun()

        st.markdown('<div class="quadrant-container">', unsafe_allow_html=True)
        q_tasks = [t for t in visible_tasks if t['quadrant'] == q['num']]
        
        for task in q_tasks:
            # 비율 조정 (모바일은 체크박스 영역 확보, PC는 텍스트 영역 확보)
            col_ratio = [0.1, 0.8, 0.1] if st.session_state.view_mode == "PC" else [0.22, 0.63, 0.15]
            t_col1, t_col2, t_col3 = st.columns(col_ratio)
            
            with t_col1:
                # 체크박스 로직
                is_checked = st.checkbox("", value=task['completed'], key=f"chk_{task['id']}", label_visibility="collapsed")
                if is_checked != task['completed']:
                    task['completed'] = is_checked
                    st.rerun()
            
            with t_col2:
                txt = task['text']
                if task['completed']: 
                    txt = f"<span style='text-decoration: line-through; color: #94a3b8;'>{txt}</span>"
                if task['date'] < str(selected_date): 
                    txt = f"⏳ {txt}"
                st.markdown(f"<div style='padding-top: 2px;'>{txt}</div>", unsafe_allow_html=True)
            
            with t_col3:
                if st.button("×", key=f"del_{task['id']}", help="삭제"):
                    st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# 푸터 영역
if st.session_state.view_mode == "PC":
    st.divider()
    st.caption("Eisenhower Matrix - Productivity Tool")
else:
    st.caption(f"Mode: {st.session_state.view_mode} | {selected_date}")
