import streamlit as st
import uuid
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(
    page_title="Eisenhower Matrix",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 상태 초기화
if 'tasks' not in st.session_state:
    st.session_state.tasks = []
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
if 'adding_to' not in st.session_state:
    st.session_state.adding_to = None

# 3. 테마 컬러 정의
if st.session_state.dark_mode:
    c = {
        'bg': '#0f172a', 'card': '#1e293b', 'text': '#f8fafc', 
        'muted': '#94a3b8', 'border': '#334155', 'accent': '#6366f1'
    }
else:
    c = {
        'bg': '#f8fafc', 'card': '#ffffff', 'text': '#1e293b', 
        'muted': '#64748b', 'border': '#e2e8f0', 'accent': '#4f46e5'
    }

# 4. 커스텀 CSS
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    * {{ font-family: 'Inter', 'Noto Sans KR', sans-serif !important; }}
    .main {{ background-color: {c['bg']} !important; }}
    .block-container {{ padding: 1rem 2rem !important; max-width: 1000px !important; }}
    
    /* 헤더 및 통계 */
    .header-title {{
        text-align: center; font-size: 2.2rem; font-weight: 800;
        background: linear-gradient(135deg, #6366f1, #a855f7);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }}
    .stat-container {{
        background: {c['card']}; border: 1px solid {c['border']};
        border-radius: 12px; padding: 12px; text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        height: 100%;
    }}
    .stat-val {{ font-size: 1.4rem; font-weight: 800; color: {c['text']}; }}
    .stat-lbl {{ font-size: 0.8rem; color: {c['muted']}; text-transform: uppercase; letter-spacing: 0.05em; }}

    /* 사분면 카드 스타일 */
    .q-card {{
        background: {c['card']};
        border-radius: 20px; padding: 0px; margin-bottom: 24px;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.04);
        overflow: hidden;
        min-height: 350px;
        border: 2px solid {c['border']};
        transition: transform 0.2s ease;
    }}
    
    /* 할 일 아이템 */
    .task-row {{
        display: flex; align-items: center; background: {c['bg']};
        padding: 10px 14px; border-radius: 12px; margin: 0 12px 8px 12px;
        border: 1px solid {c['border']}; transition: all 0.2s ease;
    }}
    .task-text {{ font-size: 0.95rem; color: {c['text']}; flex-grow: 1; }}
    .task-done {{ text-decoration: line-through; color: {c['muted']}; opacity: 0.6; }}

    /* 기본 요소 커스텀 */
    #MainMenu, footer, header {{ visibility: hidden; }}
    div[data-testid="stCheckbox"] label {{ display: none !important; }}
    
    /* 버튼 통합 스타일 */
    .stButton > button {{
        border-radius: 8px !important;
        font-weight: 700 !important;
    }}
    
    /* 카드 헤더 버튼 전용 */
    .header-btn > div > button {{
        border-radius: 0px !important;
        border: none !important;
        padding: 1.2rem !important;
        font-size: 1.1rem !important;
        margin: 0 !important;
        text-align: left !important;
        display: flex !important;
        justify-content: flex-start !important;
    }}

    /* 입력창 마진 조정 */
    .stTextInput {{ padding: 10px 15px; }}
</style>
""", unsafe_allow_html=True)

# 5. 비즈니스 로직
def add_task(text, quad, date):
    if not text.strip(): return
    configs = {1: (True, True), 2: (False, True), 3: (True, False), 4: (False, False)}
    urgent, important = configs[quad]
    st.session_state.tasks.append({
        "id": str(uuid.uuid4()), "text": text, "urgent": urgent, "important": important,
        "completed": False, "date": str(date), "quadrant": quad
    })
    st.session_state.adding_to = None

# 6. 헤더 및 컨트롤
st.markdown("<div class='header-title'>Matrix Focus</div>", unsafe_allow_html=True)

ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([3, 1, 1])
with ctrl_col1:
    selected_date = st.date_input("날짜 선택", datetime.now(), label_visibility="collapsed")
with ctrl_col2:
    if st.button("✨ 완료 일감 삭제", use_container_width=True):
        st.session_state.tasks = [t for t in st.session_state.tasks if not t['completed']]
        st.rerun()
with ctrl_col3:
    dark = st.toggle("🌙 다크 모드", value=st.session_state.dark_mode)
    if dark != st.session_state.dark_mode:
        st.session_state.dark_mode = dark
        st.rerun()

# 7. 통계 섹션
tasks_today = [t for t in st.session_state.tasks if t['date'] == str(selected_date)]
total = len(tasks_today)
done = len([t for t in tasks_today if t['completed']])
rate = round(done/total*100) if total > 0 else 0
urgent_count = len([t for t in tasks_today if t['urgent']])

st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
s_col1, s_col2, s_col3, s_col4 = st.columns(4)

with s_col1:
    st.markdown(f"<div class='stat-container'><div class='stat-val'>{total}</div><div class='stat-lbl'>전체</div></div>", unsafe_allow_html=True)
with s_col2:
    st.markdown(f"<div class='stat-container'><div class='stat-val'>{done}</div><div class='stat-lbl'>완료</div></div>", unsafe_allow_html=True)
with s_col3:
    st.markdown(f"<div class='stat-container'><div class='stat-val'>{rate}%</div><div class='stat-lbl'>진행률</div></div>", unsafe_allow_html=True)
with s_col4:
    # 긴급 추가 버튼 스타일링
    if st.button(f"{urgent_count}\n긴급 추가", key="urgent_trigger", use_container_width=True):
        st.session_state.adding_to = 1
        st.rerun()
    st.markdown('<style>div[data-testid="stColumn"]:nth-of-type(4) button { border: 2px solid #ef4444 !important; color: #ef4444 !important; border-radius: 12px !important; height: 100% !important; background: transparent !important; font-weight: 800 !important; }</style>', unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
st.progress(rate / 100)
st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

# 8. 매트릭스 그리드 (색상 및 클릭 추가)
quad_data = [
    {"n": 1, "t": "🔥 DO FIRST", "desc": "중요함 & 긴급함", "bg": "#fee2e2", "fg": "#b91c1c", "border": "#fca5a5"},
    {"n": 2, "t": "🌱 SCHEDULE", "desc": "중요함 & 여유로움", "bg": "#dcfce7", "fg": "#15803d", "border": "#86efac"},
    {"n": 3, "t": "📢 DELEGATE", "desc": "사소함 & 긴급함", "bg": "#e0f2fe", "fg": "#0369a1", "border": "#7dd3fc"},
    {"n": 4, "t": "☕ ELIMINATE", "desc": "사소함 & 여유로움", "bg": "#f1f5f9", "fg": "#334155", "border": "#cbd5e1"}
]

if st.session_state.dark_mode:
    for q in quad_data:
        q['bg'] = "#1e293b"
        q['border'] = q['fg']

m_row1_col1, m_row1_col2 = st.columns(2)
m_row2_col1, m_row2_col2 = st.columns(2)
cols = [m_row1_col1, m_row1_col2, m_row2_col1, m_row2_col2]

visible_tasks = [t for t in st.session_state.tasks if t['date'] == str(selected_date) or (t['date'] < str(selected_date) and not t['completed'])]

for i, q in enumerate(quad_data):
    with cols[i]:
        # 개별 카드 테두리 색상 적용을 위한 스타일 주입
        st.markdown(f"""
            <style>
                div.q-card-{q['n']} {{ border-color: {q['border']} !important; }}
                div.q-card-{q['n']} .header-btn button {{ background-color: {q['bg']} !important; color: {q['fg']} !important; border-bottom: 1px solid {q['border']} !important; }}
            </style>
        """, unsafe_allow_html=True)
        
        st.markdown(f"<div class='q-card q-card-{q['n']}'>", unsafe_allow_html=True)
        
        # 헤더를 클릭 가능한 버튼으로 구성 (내용 추가 트리거)
        st.markdown("<div class='header-btn'>", unsafe_allow_html=True)
        if st.button(f"{q['t']} ({q['desc']})", key=f"head{q['n']}", use_container_width=True):
            st.session_state.adding_to = q['n']
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        # 입력 모드
        if st.session_state.adding_to == q['n']:
            st.markdown("<div style='padding: 0 15px;'>", unsafe_allow_html=True)
            new_txt = st.text_input("새로운 할 일", key=f"in{q['n']}", placeholder="내용 입력 후 저장...", label_visibility="collapsed")
            btn_c1, btn_c2 = st.columns(2)
            if btn_c1.button("✅ 저장", key=f"sv{q['n']}", use_container_width=True, type="primary"):
                add_task(new_txt, q['n'], selected_date)
                st.rerun()
            if btn_c2.button("❌ 취소", key=f"cc{q['n']}", use_container_width=True):
                st.session_state.adding_to = None
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        
        # 목록 영역
        q_tasks = sorted([t for t in visible_tasks if t['quadrant'] == q['n']], key=lambda x: x['completed'])
        
        if not q_tasks:
            # 빈 상태일 때도 클릭하여 추가할 수 있도록 버튼 배치
            st.markdown("<div style='padding: 40px 15px; text-align: center;'>", unsafe_allow_html=True)
            if st.button("➕ 할 일 추가하기", key=f"empty_add_{q['n']}", use_container_width=True):
                st.session_state.adding_to = q['n']
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='padding-top: 15px;'></div>", unsafe_allow_html=True)
            for task in q_tasks:
                t_c1, t_c2, t_c3 = st.columns([0.12, 0.76, 0.12])
                with t_c1:
                    is_done = st.checkbox("", value=task['completed'], key=f"chk{task['id']}")
                    if is_done != task['completed']:
                        task['completed'] = is_done
                        st.rerun()
                with t_c2:
                    cls = "task-done" if task['completed'] else ""
                    overdue = "⏳" if task['date'] < str(selected_date) else ""
                    st.markdown(f"<div class='task-text {cls}'>{overdue} {task['text']}</div>", unsafe_allow_html=True)
                with t_c3:
                    if st.button("🗑️", key=f"del{task['id']}", help="삭제"):
                        st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                        st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

# 9. 푸터
st.markdown("<br>", unsafe_allow_html=True)
footer_col1, footer_col2 = st.columns([3, 1])
with footer_col1:
    st.caption(f"마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
with footer_col2:
    if st.button("⚠️ 데이터 초기화", use_container_width=True):
        st.session_state.tasks = []
        st.rerun()

st.markdown("<div style='text-align:center; font-size:0.75rem; color:#94a3b8; margin-top:30px; border-top:1px solid #e2e8f0; padding-top:20px;'>Focus on what matters. Eisenhower Matrix v8.0</div>", unsafe_allow_html=True)
