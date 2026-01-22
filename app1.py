import streamlit as st
import pandas as pd
from datetime import datetime

# 페이지 설정
st.set_page_config(page_title="아이젠하워 매트릭스 플래너", layout="wide")

# 세션 상태 초기화 (데이터 저장용)
if 'tasks' not in st.session_state:
    st.session_state.tasks = []

# 제목 섹션
st.title("🚀 Eisenhower Matrix Pro")
st.write("중요도와 긴급성에 따라 작업을 분류하세요.")

# 입력 섹션
with st.container():
    col1, col2, col3 = st.columns([4, 2, 1])
    with col1:
        new_task = st.text_input("새로운 할 일", placeholder="무엇을 해야 하나요?")
    with col2:
        category = st.selectbox("분류 선택", [
            "Q1: 긴급 & 중요 (Do First)",
            "Q2: 안 긴급 & 중요 (Schedule)",
            "Q3: 긴급 & 안 중요 (Delegate)",
            "Q4: 안 긴급 & 안 중요 (Eliminate)"
        ])
    with col3:
        st.write("##") # 간격 조절
        if st.button("추가", use_container_width=True):
            if new_task:
                st.session_state.tasks.append({
                    "text": new_task,
                    "quadrant": category.split(":")[0],
                    "completed": False,
                    "time": datetime.now().strftime("%H:%M")
                })
                st.rerun()

st.divider()

# 매트릭스 레이아웃 (2x2)
q_info = {
    "Q1": {"title": "🔴 Do First", "desc": "즉시 실행", "color": "#fee2e2"},
    "Q2": {"title": "🔵 Schedule", "desc": "계획 수립", "color": "#dbeafe"},
    "Q3": {"title": "🟠 Delegate", "desc": "권한 위임", "color": "#ffedd5"},
    "Q4": {"title": "⚪ Eliminate", "desc": "삭제/제거", "color": "#f1f5f9"}
}

cols = st.columns(2)

for i, q_id in enumerate(["Q1", "Q2", "Q3", "Q4"]):
    with cols[i % 2]:
        st.subheader(q_info[q_id]["title"])
        st.caption(f"{q_info[q_id]['desc']} (위치: {q_id})")
        
        # 해당 사분면의 할 일 필터링
        q_tasks = [t for t in st.session_state.tasks if t["quadrant"] == q_id]
        
        if not q_tasks:
            st.info("비어 있습니다.")
        else:
            for idx, task in enumerate(q_tasks):
                # 할 일 표시 레이아웃
                t_col1, t_col2 = st.columns([5, 1])
                with t_col1:
                    is_done = st.checkbox(f"{task['text']} ({task['time']})", key=f"check_{q_id}_{idx}", value=task['completed'])
                    # 완료 상태 업데이트
                    for t in st.session_state.tasks:
                        if t == task:
                            t['completed'] = is_done
                with t_col2:
                    if st.button("🗑️", key=f"del_{q_id}_{idx}"):
                        st.session_state.tasks.remove(task)
                        st.rerun()

# 하단 통계
st.sidebar.title("📊 통계")
total = len(st.session_state.tasks)
done = len([t for t in st.session_state.tasks if t['completed']])
if total > 0:
    st.sidebar.progress(done / total)
    st.sidebar.write(f"진행률: {int(done/total*100)}% ({done}/{total})")
else:
    st.sidebar.write("등록된 작업이 없습니다.")

if st.sidebar.button("완료 항목 모두 삭제"):
    st.session_state.tasks = [t for t in st.session_state.tasks if not t['completed']]
    st.rerun()
