import streamlit as st
import requests
import json
import uuid
from datetime import datetime, timedelta

# --- 페이지 설정 ---
st.set_page_config(page_title="아이젠하워 기록장", layout="wide", initial_sidebar_state="collapsed")

# --- 스타일 커스텀 (모바일 2x2 그리드 및 최적화) ---
st.markdown("""
    <style>
    /* 전체 배경 및 폰트 설정 */
    .main {
        background-color: #ffffff;
    }
    
    /* 카드 및 헤더 스타일 */
    .quadrant-header {
        font-weight: 800;
        padding: 8px;
        border-radius: 12px;
        margin-bottom: 8px;
        font-size: 0.8rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* 모바일 2x2 그리드 강제 고정 */
    @media (max-width: 768px) {
        div[data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: wrap !important;
            gap: 0.4rem !important;
        }
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
            width: calc(50% - 0.2rem) !important;
            flex: 1 1 calc(50% - 0.2rem) !important;
            min-width: calc(50% - 0.2rem) !important;
            padding: 0 !important;
        }
        
        /* 텍스트 크기 최적화 */
        h1 { font-size: 1.5rem !important; }
        .stMarkdown div p { font-size: 0.75rem !important; }
        
        /* 버튼 및 입력창 컴팩트화 */
        button {
            padding: 0.2rem 0.5rem !important;
            font-size: 0.7rem !important;
        }
    }
    
    /* 할 일 아이템 스타일 */
    .task-item {
        background: rgba(255, 255, 255, 0.7);
        border-radius: 8px;
        padding: 5px;
        margin-bottom: 5px;
        border: 1px solid #f0f0f0;
    }

    /* 상단 메뉴바 숨기기 등 깔끔한 UI */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 스크롤바 커스텀 */
    div.stColumn > div {
        overflow-y: auto;
        max-height: 50vh;
        padding-right: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 초기 상태 설정 ---
if 'tasks' not in st.session_state:
    st.session_state.tasks = []

# --- Gemini API 설정 ---
API_KEY = "" 

def call_gemini(prompt, system_instruction=""):
    if not API_KEY:
        return None
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": system_instruction}]} if system_instruction else None
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"AI 연결 오류"

# --- 할 일 추가 로직 ---
def add_task(text, quadrant_num, date):
    if not text.strip():
        return
    config = {
        1: {"urgent": True, "important": True},
        2: {"urgent": False, "important": True},
        3: {"urgent": True, "important": False},
        4: {"urgent": False, "important": False}
    }[quadrant_num]
    
    new_task = {
        "id": str(uuid.uuid4()), 
        "text": text,
        "urgent": config["urgent"],
        "important": config["important"],
        "completed": False,
        "date": str(date),
        "quadrant": quadrant_num
    }
    st.session_state.tasks.append(new_task)

# --- 헤더 섹션 ---
col_head1, col_head2 = st.columns([3, 2])
with col_head1:
    st.markdown("### 📝 아이젠하워")
with col_head2:
    selected_date = st.date_input("날짜", datetime.now(), label_visibility="collapsed")

# --- 통합 입력 및 AI 코칭 ---
with st.expander("➕ 빠른 추가 및 AI 코칭", expanded=False):
    t_input = st.text_input("기록할 내용", key="global_input", placeholder="내용 입력...")
    c1, c2, c3, c4 = st.columns(4)
    for i in range(4):
        if cols_i := c1 if i==0 else c2 if i==1 else c3 if i==2 else c4:
            if cols_i.button(f"{i+1}번", use_container_width=True, key=f"g_save_{i}"):
                add_task(t_input, i+1, selected_date)
                st.rerun()
    
    if API_KEY:
        if st.button("✨ 오늘 하루 전략 코칭 받기", use_container_width=True):
            today_tasks = [t for t in st.session_state.tasks if t['date'] == str(selected_date)]
            if today_tasks:
                with st.spinner("분석 중..."):
                    list_str = "\n".join([f"- {t['text']} (박스 {t['quadrant']})" for t in today_tasks])
                    coaching = call_gemini(f"오늘 할 일:\n{list_str}\n전략 2줄 요약.", "시간 관리 전문가")
                    if coaching: st.info(coaching)
            else:
                st.warning("기록이 없습니다.")

# --- 매트릭스 뷰 (2x2) ---
quadrants = [
    {"num": 1, "title": "중요/긴급", "color": "#FFD1D1", "icon": "🔥"},
    {"num": 2, "title": "중요/비긴급", "color": "#D1FFD6", "icon": "📅"},
    {"num": 3, "title": "긴급/비중요", "color": "#D1E9FF", "icon": "📞"},
    {"num": 4, "title": "비중요/비긴급", "color": "#E9D1FF", "icon": "🗑️"}
]

# 화면 필터링 (선택 날짜 + 과거 미완료 이월)
visible_tasks = [t for t in st.session_state.tasks if t['date'] == str(selected_date) or (t['date'] < str(selected_date) and not t['completed'])]

row1 = st.columns(2)
row2 = st.columns(2)
grid = [row1[0], row1[1], row2[0], row2[1]]

for i, q in enumerate(quadrants):
    with grid[i]:
        # 헤더와 직접 추가 버튼(Popover)
        st.markdown(f'<div class="quadrant-header" style="background-color: {q["color"]}; color: #333;">{q["icon"]} {q["title"]}</div>', unsafe_allow_html=True)
        
        # 각 박스 내부에서 직접 입력하기
        with st.popover("➕ 추가", use_container_width=True):
            local_input = st.text_input("내용", key=f"local_in_{q['num']}")
            if st.button("저장", key=f"local_btn_{q['num']}", use_container_width=True):
                add_task(local_input, q['num'], selected_date)
                st.rerun()
        
        q_tasks = [t for t in visible_tasks if t['quadrant'] == q['num']]
        
        for task in q_tasks:
            # 개별 할 일 아이템
            with st.container():
                c_check, c_txt, c_del = st.columns([0.2, 0.65, 0.15])
                
                # 완료 체크
                is_done = c_check.checkbox("", value=task['completed'], key=f"chk_{task['id']}")
                if is_done != task['completed']:
                    task['completed'] = is_done
                    st.rerun()
                
                # 텍스트 표시
                display_text = task['text']
                if task['completed']:
                    display_text = f"~~{display_text}~~"
                
                # 과거 이월 표시
                if task['date'] < str(selected_date):
                    display_text = f"⚠️ {display_text}"
                
                c_txt.markdown(f"<div style='font-size: 0.75rem; line-height: 1.2; padding-top: 4px;'>{display_text}</div>", unsafe_allow_html=True)
                
                # 삭제
                if c_del.button("×", key=f"del_{task['id']}"):
                    st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                    st.rerun()
                
                # AI 분석 (키가 있을 때만 작게 표시)
                if API_KEY:
                    if st.button("✨", key=f"ai_{task['id']}", size="small"):
                        with st.spinner(""):
                            advice = call_gemini(f"'{task['text']}' 처리 팁 1줄.", "생산성 코치")
                            if advice: st.toast(advice)

# --- 푸터 ---
st.markdown("---")
st.caption("Focus Matrix v2 - 모바일 최적화 버전")