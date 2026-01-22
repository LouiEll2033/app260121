import streamlit as st
import requests
import json
import uuid
from datetime import datetime, timedelta

# --- 페이지 설정 ---
st.set_page_config(page_title="아이젠하워 기록장", layout="wide")

# --- 스타일 커스텀 ---
st.markdown("""
    <style>
    .task-card {
        padding: 10px;
        border-radius: 10px;
        background-color: white;
        border: 1px solid #f1f5f9;
        margin-bottom: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .quadrant-header {
        font-weight: bold;
        padding: 5px 10px;
        border-radius: 8px;
        margin-bottom: 10px;
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 초기 상태 설정 ---
if 'tasks' not in st.session_state:
    st.session_state.tasks = []

# --- Gemini API 설정 ---
# API 키가 없으면 AI 기능이 비활성화됩니다.
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
        return f"AI 연결 오류: {str(e)}"

# --- 주요 로직 ---
def add_task(text, quadrant_num, date):
    config = {
        1: {"urgent": True, "important": True},
        2: {"urgent": False, "important": True},
        3: {"urgent": True, "important": False},
        4: {"urgent": False, "important": False}
    }[quadrant_num]
    
    # 중복 오류 방지를 위해 uuid 사용
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
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.title("📝 아이젠하워 기록장")
with col_head2:
    selected_date = st.date_input("날짜 선택", datetime.now())

# --- 입력 섹션 ---
with st.container():
    st.write("### ✨ 새로운 할 일 추가")
    task_input = st.text_input("어떤 일을 기록할까요?", key="task_input_field", placeholder="내용을 입력하고 아래 버튼을 누르세요")
    
    cols = st.columns(4)
    btn_labels = ["1번 저장 (중요/긴급)", "2번 저장 (중요/비긴급)", "3번 저장 (긴급/비중요)", "4번 저장 (비중요/비긴급)"]
    
    for i in range(4):
        if cols[i].button(btn_labels[i], use_container_width=True, key=f"save_btn_{i+1}"):
            if task_input:
                add_task(task_input, i+1, selected_date)
                st.rerun()

# --- AI 코칭 섹션 (API 키가 있을 때만 표시) ---
if API_KEY:
    if st.button("✨ 오늘 하루 AI 코칭 받기", use_container_width=True, key="daily_coaching_btn"):
        today_tasks = [t for t in st.session_state.tasks if t['date'] == str(selected_date)]
        if today_tasks:
            with st.spinner("AI가 오늘의 일정을 분석 중입니다..."):
                list_str = "\n".join([f"- {t['text']} (박스 {t['quadrant']})" for t in today_tasks])
                prompt = f"오늘의 할 일 목록:\n{list_str}\n\n오늘 하루를 어떻게 보내면 좋을지 전략을 짜줘."
                coaching = call_gemini(prompt, "너는 시간 관리 전문가야. 한국어로 3줄 요약해줘.")
                if coaching:
                    st.info(f"💡 AI 코칭: {coaching}")
        else:
            st.warning("기록된 할 일이 없습니다.")

# --- 매트릭스 뷰 (2x2) ---
st.divider()
quadrants = [
    {"num": 1, "title": "① 중요하고 긴급한 일", "color": "#fee2e2", "icon": "🔥"},
    {"num": 2, "title": "② 중요하지만 긴급하지 않은 일", "color": "#d1fae5", "icon": "📅"},
    {"num": 3, "title": "③ 긴급하지만 중요하지 않은 일", "color": "#e0f2fe", "icon": "📞"},
    {"num": 4, "title": "④ 중요하지도 긴급하지도 않은 일", "color": "#f3e8ff", "icon": "🗑️"}
]

# 화면 필터링 (선택 날짜 + 과거 미완료 이월)
visible_tasks = [t for t in st.session_state.tasks if t['date'] == str(selected_date) or (t['date'] < str(selected_date) and not t['completed'])]

row1 = st.columns(2)
row2 = st.columns(2)
grid = [row1[0], row1[1], row2[0], row2[1]]

for i, q in enumerate(quadrants):
    with grid[i]:
        st.markdown(f'<div class="quadrant-header" style="background-color: {q["color"]};">{q["icon"]} {q["title"]}</div>', unsafe_allow_html=True)
        q_tasks = [t for t in visible_tasks if t['quadrant'] == q['num']]
        
        if not q_tasks:
            st.caption("기록 없음")
        
        for task in q_tasks:
            with st.container():
                inner_col1, inner_col2, inner_col3 = st.columns([0.15, 0.65, 0.2])
                
                # 완료 체크박스
                is_done = inner_col1.checkbox("", value=task['completed'], key=f"check_{task['id']}")
                if is_done != task['completed']:
                    task['completed'] = is_done
                    st.rerun()
                
                # 텍스트 표시
                task_text = task['text']
                if task['completed']:
                    task_text = f"~~{task_text}~~"
                
                label = f"{task_text}"
                if task['date'] < str(selected_date):
                    label += " ⚠️"
                
                inner_col2.markdown(f"<div style='font-size: 0.85rem; padding-top: 5px;'>{label}</div>", unsafe_allow_html=True)
                
                # 삭제 버튼
                if inner_col3.button("🗑️", key=f"del_{task['id']}"):
                    st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                    st.rerun()
                
                # AI 분석 버튼 (API 키가 있을 때만 표시)
                if API_KEY:
                    if st.button(f"✨ AI 분석", key=f"ai_btn_{task['id']}", size="small", use_container_width=True):
                        with st.spinner("분석 중..."):
                            prompt = f"할 일: '{task['text']}', 분류: {q['title']}. 효율적인 처리 조언을 2문장으로 해줘."
                            advice = call_gemini(prompt, "생산성 코치")
                            if advice:
                                st.toast(advice)

# --- 푸터 ---
st.markdown("---")
st.caption("아이젠하워 매트릭스 - Streamlit 버전")