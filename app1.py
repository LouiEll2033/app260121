# pip install streamlit
# python -m streamlit run eisenhower_streamlit.py

import streamlit as st
import uuid
from datetime import datetime

st.set_page_config(page_title="아이젠하워 매트릭스", layout="centered", initial_sidebar_state="collapsed")

# 초기화
if 'tasks' not in st.session_state:
    st.session_state.tasks = []
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
if 'adding_to' not in st.session_state:
    st.session_state.adding_to = None

# 테마
c = {
    'bg': '#0f172a' if st.session_state.dark_mode else '#f8fafc',
    'card': '#1e293b' if st.session_state.dark_mode else '#ffffff',
    'text': '#e2e8f0' if st.session_state.dark_mode else '#1e293b',
    'muted': '#94a3b8' if st.session_state.dark_mode else '#64748b',
    'border': '#334155' if st.session_state.dark_mode else '#e2e8f0',
}

# 스타일
st.markdown(f"""
<style>
* {{font-family: 'Noto Sans KR', sans-serif !important;}}
.main {{background: {c['bg']} !important; padding: 0 !important;}}
.block-container {{padding: 0.3rem 0.5rem !important; max-width: 100% !important;}}
.header {{text-align:center; background:linear-gradient(135deg,#667eea,#764ba2); -webkit-background-clip:text; -webkit-text-fill-color:transparent; font-size:1.4rem; font-weight:900; margin:8px 0;}}
.stat {{background: {c['card']}; border: 1px solid {c['border']}; border-radius: 8px; padding: 6px; text-align: center;}}
.stat-n {{font-size: 1.3rem; font-weight: 900; color: {c['text']};}}
.stat-l {{font-size: 0.7rem; color: {c['muted']};}}
.qbox {{background: {c['card']}; border: 2px solid {c['border']}; border-radius: 12px; padding: 8px; margin-bottom: 8px; cursor: pointer; transition: all 0.2s;}}
.qbox:active {{transform: scale(0.98);}}
.qtitle {{font-size: 0.95rem; font-weight: 900; color: {c['text']}; padding: 8px; border-radius: 6px; text-align: center; margin-bottom: 6px;}}
.task {{background: {c['bg']}; border: 1px solid {c['border']}; border-radius: 6px; padding: 6px 8px; margin-bottom: 4px; font-size: 0.85rem; color: {c['text']};}}
.done {{text-decoration: line-through; color: {c['muted']}; opacity: 0.5;}}
.empty {{text-align: center; padding: 15px; color: {c['muted']}; font-size: 0.8rem;}}
div[data-testid="stCheckbox"] label {{display: none !important;}}
div[data-testid="stCheckbox"] {{margin: 0 !important; padding: 0 !important;}}
.stButton > button {{border-radius: 8px !important; font-weight: 700 !important; padding: 0.4rem 0.8rem !important; font-size: 0.85rem !important;}}
.stTextInput input {{border-radius: 6px !important; font-size: 0.9rem !important;}}
#MainMenu, footer, header {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# 함수
def add_task(text, quad, date):
    if not text.strip(): return
    configs = {1: (True, True), 2: (False, True), 3: (True, False), 4: (False, False)}
    urgent, important = configs[quad]
    st.session_state.tasks.append({
        "id": str(uuid.uuid4()), "text": text, "urgent": urgent, "important": important,
        "completed": False, "date": str(date), "quadrant": quad
    })
    st.session_state.adding_to = None

def get_stats(date):
    tasks = [t for t in st.session_state.tasks if t['date'] == str(date)]
    if not tasks: return {"total": 0, "done": 0, "rate": 0, "urgent": 0}
    total = len(tasks)
    done = len([t for t in tasks if t['completed']])
    urgent = len([t for t in tasks if t['urgent']])
    return {"total": total, "done": done, "rate": round(done/total*100 if total > 0 else 0), "urgent": urgent}

# 헤더
st.markdown("<div class='header'>📋 아이젠하워 매트릭스</div>", unsafe_allow_html=True)

# 날짜 & 다크모드
col1, col2 = st.columns([5, 1])
with col1:
    selected_date = st.date_input("날짜", datetime.now(), label_visibility="collapsed")
with col2:
    dark = st.toggle("🌙", st.session_state.dark_mode, label_visibility="collapsed")
    if dark != st.session_state.dark_mode:
        st.session_state.dark_mode = dark
        st.rerun()

# 통계
stats = get_stats(selected_date)
cols = st.columns(4)
for i, (num, label) in enumerate([(stats['total'], '전체'), (stats['done'], '완료'), (stats['rate'], '완료율'), (stats['urgent'], '긴급')]):
    with cols[i]:
        unit = '%' if label == '완료율' else ''
        st.markdown(f"<div class='stat'><div class='stat-n'>{num}{unit}</div><div class='stat-l'>{label}</div></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 사분면
quads = [
    {"n": 1, "t": "🔥 중요&긴급", "c": "#fecaca" if not st.session_state.dark_mode else "#991b1b"},
    {"n": 2, "t": "🌱 중요&여유", "c": "#d1fae5" if not st.session_state.dark_mode else "#065f46"},
    {"n": 3, "t": "📢 긴급&사소", "c": "#bae6fd" if not st.session_state.dark_mode else "#0c4a6e"},
    {"n": 4, "t": "☕ 여유&사소", "c": "#e2e8f0" if not st.session_state.dark_mode else "#475569"}
]

visible = [t for t in st.session_state.tasks if t['date'] == str(selected_date) or (t['date'] < str(selected_date) and not t['completed'])]

for q in quads:
    # 박스 클릭으로 입력 모드 전환
    if st.session_state.adding_to != q['n']:
        if st.button(f"**{q['t']}**", key=f"btn{q['n']}", use_container_width=True):
            st.session_state.adding_to = q['n']
            st.rerun()
    
    st.markdown(f"<div class='qbox'>", unsafe_allow_html=True)
    
    # 입력 모드
    if st.session_state.adding_to == q['n']:
        st.markdown(f"<div class='qtitle' style='background:{q['c']};'>{q['t']}</div>", unsafe_allow_html=True)
        txt = st.text_input("할 일을 입력하세요", key=f"input{q['n']}", placeholder="예: 프로젝트 마감")
        col_s, col_c = st.columns(2)
        with col_s:
            if st.button("✅ 저장", key=f"save{q['n']}", use_container_width=True):
                add_task(txt, q['n'], selected_date)
                st.rerun()
        with col_c:
            if st.button("❌ 취소", key=f"cancel{q['n']}", use_container_width=True):
                st.session_state.adding_to = None
                st.rerun()
    else:
        # 일반 모드 - 할 일 목록
        st.markdown(f"<div class='qtitle' style='background:{q['c']};'>{q['t']}</div>", unsafe_allow_html=True)
        
        tasks = sorted([t for t in visible if t['quadrant'] == q['n']], key=lambda x: x['completed'])
        
        if not tasks:
            st.markdown("<div class='empty'>탭하여 할 일 추가</div>", unsafe_allow_html=True)
        else:
            for task in tasks:
                c1, c2, c3 = st.columns([0.12, 0.76, 0.12])
                with c1:
                    chk = st.checkbox("", task['completed'], key=f"chk{task['id']}")
                    if chk != task['completed']:
                        task['completed'] = chk
                        st.rerun()
                with c2:
                    t = task['text']
                    if task['date'] < str(selected_date): t = f"⏳ {t}"
                    cls = "done" if task['completed'] else ""
                    st.markdown(f"<div class='task {cls}'>{t}</div>", unsafe_allow_html=True)
                with c3:
                    if st.button("🗑️", key=f"del{task['id']}"):
                        st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# 관리 버튼
st.markdown("<br>", unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    if st.button("✅ 완료 삭제", use_container_width=True):
        st.session_state.tasks = [t for t in st.session_state.tasks if not t['completed']]
        st.rerun()
with c2:
    if st.button("🗑️ 전체 초기화", use_container_width=True):
        st.session_state.tasks = []
        st.rerun()

st.caption("v5.3 Mobile Compact")
