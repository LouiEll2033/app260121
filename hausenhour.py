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
        help="기기에 맞춰 최적화된 화면을 선택하세요."
    )
    st.divider()
    st.info("💡 **Mobile**: 한 화면에 박제된 가독성 중심 레이아웃\n\n💡 **PC**: 넓고 시원한 데이터 확인용 레이아웃")

# --- 강력한 스타일 최적화 ---
if st.session_state.view_mode == "Mobile":
    st.markdown("""
        <style>
        /* 기본 레이아웃 강제 고정 */
        * { box-sizing: border-box !important; }
        [data-testid="stHeader"] { visibility: hidden; height: 0; }
        footer { visibility: hidden; }
        .main { background-color: #ffffff; overflow-x: hidden !important; }
        
        /* 모바일 전체 컨테이너: 가로 스크롤 절대 금지 */
        .block-container { 
            padding-top: 0.5rem !important; 
            padding-bottom: 0 !important; 
            padding-left: 0.2rem !important; 
            padding-right: 0.2rem !important;
            max-width: 100vw !important;
            overflow-x: hidden !important;
        }
        
        /* 2열 강제 고정 및 간격 최적화 */
        [data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important; /* 줄바꿈 절대 방지 */
            width: 100% !important;
            gap: 4px !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        /* 컬럼 너비를 정확히 절반으로 박제 */
        [data-testid="stHorizontalBlock"] [data-testid="column"] {
            width: calc(50% - 2px) !important;
            flex: 1 1 calc(50% - 2px) !important;
            min-width: 0 !important;
            max-width: 50% !important;
            padding: 0 !important;
        }

        /* 사분면 헤더 디자인 */
        .q-header {
            font-weight: 800; padding: 5px 0; border-radius: 8px 8px 0 0;
            font-size: 0.7rem; text-align: center; color: #333;
            border: 1px solid rgba(0,0,0,0.05); line-height: 1.1;
        }

        /* 사분면 내용 영역: 한 화면에 맞게 높이 계산 (Viewport Height) */
        .quadrant-container {
            border: 1px solid #f1f5f9; border-radius: 0 0 8px 8px;
            padding: 4px; background-color: #fafafa;
            height: 38vh; /* 화면의 38%씩 2개 층 배치 */
            overflow-y: auto;
            overflow-x: hidden;
        }

        /* 가독성 상향 (텍스트 크기 최적화) */
        .stMarkdown div p { 
            font-size: 0.75rem !important; 
            line-height: 1.25 !important; 
            word-break: break-all;
            color: #1e293b;
            margin: 0 !important;
        }

        /* 체크박스 및 위젯 압축 */
        .stVerticalBlock { gap: 0rem !important; }
        div[data-testid="stCheckbox"] { 
            margin-top: -10px !important; 
            margin-bottom: -12px !important; 
            transform: scale(0.85); 
        }
        div[data-testid="stCheckbox"] label { display: none !important; }

        /* 버튼 콤팩트화 */
        .stButton>button { 
            font-size: 0.6rem; height: 24px; min-height: 24px; 
            padding: 0 !important; border-radius: 6px; 
        }
        div[data-testid="stPopover"] > button { 
            height: 24px !important; font-size: 0.6rem !important; 
            padding: 0 !important; border-radius: 6px !important; 
        }
        </style>
        """, unsafe_allow_html=True)
else:
    # PC 버전: 여백과 크기를 확장하여 가독성 확보
    st.markdown("""
        <style>
        .main { background-color: #f1f5f9; }
        .block-container { 
            padding-top: 2rem !important; 
            max-width: 1200px !important;
        }
        [data-testid="stHorizontalBlock"] { gap: 20px !important; }
        .q-header {
            font-weight: 800; padding: 15px; border-radius: 12px 12px 0 0;
            font-size: 1.1rem; text-align: center;
        }
        .quadrant-container {
            border: 1px solid #e2e8f0; border-radius: 0 0 12px 12px;
            padding: 20px; background-color: #ffffff;
            min-height: 450px; overflow-y: auto;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }
        .stMarkdown div p { font-size: 1.05rem !important; line-height: 1.6 !important; }
        .stButton>button { font-size: 1rem; font-weight: 600; border-radius: 10px; }
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
    selected_date = st.date_input("날짜", datetime.now(), label_visibility="collapsed")

# --- 매트릭스 설정 ---
quadrants = [
    {"num": 1, "title": "중요/긴급", "color": "#FFD6D6", "icon": "🔥"},
    {"num": 2, "title": "중요/비긴급", "color": "#D6FFDA", "icon": "🌱"},
    {"num": 3, "title": "긴급/비중요", "color": "#D6E9FF", "icon": "📢"},
    {"num": 4, "title": "비중요/비긴급", "color": "#E9D6FF", "icon": "☕"}
]

# 필터링 로직
visible_tasks = [t for t in st.session_state.tasks if t['date'] == str(selected_date) or (t['date'] < str(selected_date) and not t['completed'])]

# --- 2x2 그리드 배치 ---
row1 = st.columns(2)
row2 = st.columns(2)
grid = [row1[0], row1[1], row2[0], row2[1]]

for i, q in enumerate(quadrants):
    with grid[i]:
        st.markdown(f'<div class="q-header" style="background-color: {q["color"]};">{q["icon"]} {q["title"]}</div>', unsafe_allow_html=True)
        
        with st.popover("➕ 추가", use_container_width=True):
            in_val = st.text_input("할 일", key=f"in_{q['num']}", placeholder="내용 입력 후 엔터", label_visibility="collapsed")
            if st.button("저장", key=f"btn_{q['num']}", use_container_width=True):
                add_task(in_val, q['num'], selected_date)
                st.rerun()

        st.markdown('<div class="quadrant-container">', unsafe_allow_html=True)
        q_tasks = [t for t in visible_tasks if t['quadrant'] == q['num']]
        
        for task in q_tasks:
            # 모바일과 PC 비율 미세 조정
            ratio = [0.15, 0.7, 0.15] if st.session_state.view_mode == "PC" else [0.2, 0.65, 0.15]
            t_col1, t_col2, t_col3 = st.columns(ratio)
            
            with t_col1:
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
                st.markdown(f"<div style='padding-top: 3px;'>{txt}</div>", unsafe_allow_html=True)
            
            with t_col3:
                if st.button("×", key=f"del_{task['id']}", help="삭제"):
                    st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# 푸터
if st.session_state.view_mode == "PC":
    st.divider()
    st.caption("Eisenhower Matrix - PC Optimized View")
else:
    st.caption(f"Ver: {st.session_state.view_mode} | {selected_date}")
