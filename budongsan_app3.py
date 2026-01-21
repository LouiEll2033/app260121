import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
import re

# 1. 페이지 설정 (가장 먼저 실행되어야 함)
st.set_page_config(page_title="부동산 가격 예측기", layout="wide", page_icon="🏠")

def clean_value(val):
    """문자열에서 숫자와 소수점만 추출하는 안전한 함수"""
    if pd.isna(val) or val == '': return np.nan
    s = str(val).strip()
    # 숫자와 마침표(.)를 제외한 모든 문자 제거 (콤마, 한글 등)
    s = re.sub(r'[^0-9.]', '', s)
    if s == '' or s == '.': return np.nan
    try:
        return float(s)
    except:
        return np.nan

@st.cache_data
def load_data_robust(file_source):
    """모든 인코딩 및 컬럼 형식을 지원하는 강력한 데이터 로더"""
    try:
        df = None
        # 인코딩 순차 시도
        encodings = ['utf-8-sig', 'cp949', 'utf-8', 'euc-kr']
        for enc in encodings:
            try:
                if isinstance(file_source, str):
                    df = pd.read_csv(file_source, encoding=enc)
                else:
                    file_source.seek(0)
                    df = pd.read_csv(file_source, encoding=enc)
                if df is not None: break
            except:
                continue
        
        if df is None:
            return None, "파일 내용을 읽을 수 없습니다. 인코딩이나 파일 형식을 확인해주세요."

        # 컬럼명 정리
        df.columns = [str(col).strip() for col in df.columns]
        
        # 데이터 매핑
        new_df = pd.DataFrame()
        
        # 컬럼 검색 패턴
        col_patterns = {
            '지역명': ['지역', '시도', 'city'],
            '규모구분': ['규모', '면적', 'size'],
            '연도': ['연도', 'year'],
            '월': ['월', 'month'],
            '분양가격': ['분양가격', '가격', 'price']
        }
        
        found_mapping = {}
        for key, patterns in col_patterns.items():
            for col in df.columns:
                if any(p in col for p in patterns):
                    found_mapping[key] = col
                    break
        
        # 필수 컬럼 체크
        if len(found_mapping) < 4:
            return None, f"필수 컬럼을 찾을 수 없습니다. (인식된 컬럼: {list(df.columns)})"

        new_df['지역명'] = df[found_mapping['지역명']].astype(str)
        new_df['규모구분'] = df[found_mapping['규모구분']].astype(str)
        new_df['연도'] = pd.to_numeric(df[found_mapping['연도']], errors='coerce')
        new_df['월'] = pd.to_numeric(df[found_mapping['월']], errors='coerce')
        new_df['분양가격'] = df[found_mapping['분양가격']].apply(clean_value)

        # 데이터 청소
        new_df = new_df.dropna(subset=['연도', '월', '분양가격'])
        
        def safe_date(row):
            try:
                return pd.Timestamp(year=int(row['연도']), month=int(row['월']), day=1)
            except:
                return pd.NaT

        new_df['날짜'] = new_df.apply(safe_date, axis=1)
        new_df = new_df.dropna(subset=['날짜'])
        new_df['평당가'] = new_df['분양가격'] * 3.3
        
        return new_df, None

    except Exception as e:
        return None, f"전처리 중 오류 발생: {str(e)}"

# --- UI 메인 ---
st.title("🏠 부동산 지역별 분양가 분석 및 2026 예측")

# 파일 검색 로직
FILE_NAME = '한국부동산 가격 데이터.csv'
csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]

st.sidebar.header("📁 데이터 설정")
uploaded_file = st.sidebar.file_uploader("CSV 파일 업로드", type=['csv'])

target = None
if uploaded_file:
    target = uploaded_file
elif os.path.exists(FILE_NAME):
    target = FILE_NAME
elif csv_files:
    # 폴더 내에 다른 이름의 CSV가 있으면 첫 번째 파일 시도
    target = csv_files[0]

if target:
    df, err = load_data_robust(target)
    
    if err:
        st.error(f"❌ 데이터 로드 실패: {err}")
    else:
        st.sidebar.success(f"✅ 로드됨: {target if isinstance(target, str) else target.name}")
        
        # 필터 설정
        st.markdown("### 🔍 데이터 필터링")
        c1, c2 = st.columns(2)
        with c1:
            regions = sorted(df['지역명'].unique())
            sel_region = st.selectbox("📍 지역 선택", regions)
        with c2:
            sizes = sorted(df['규모구분'].unique())
            sel_size = st.selectbox("📏 면적 규모 선택", sizes)

        filtered = df[(df['지역명'] == sel_region) & (df['규모구분'] == sel_size)].sort_values('날짜')

        if filtered.empty:
            st.warning("선택한 조건의 데이터가 없습니다. 다른 지역이나 규모를 선택해 주세요.")
        else:
            # 1. 시각화
            st.subheader(f"📈 {sel_region} ({sel_size}) 가격 추이")
            fig = px.line(filtered, x='날짜', y='평당가', markers=True,
                          labels={'평당가': '평당가(만원)', '날짜': '조사시점'},
                          template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

            # 2. 예측
            st.divider()
            st.subheader("🔮 2026년 예측 데이터 (선형 분석)")
            
            filtered['time_idx'] = filtered['연도'] + (filtered['월'] - 1) / 12
            x = filtered['time_idx'].values
            y = filtered['평당가'].values

            if len(x) >= 2:
                # Numpy를 이용한 1차 회귀
                z = np.polyfit(x, y, 1)
                p = np.poly1d(z)
                pred_2026 = p(2026.0)
                last_val = y[-1]
                
                m1, m2, m3 = st.columns(3)
                m1.metric("최근 실거래가", f"{last_val:,.0f} 만원")
                m2.metric("2026년 예상가", f"{max(0, pred_2026):,.0f} 만원")
                m3.metric("예상 등락률", f"{((pred_2026 - last_val) / last_val) * 100:+.1f}%")

                # 예측 선 그래프
                future_x = np.linspace(x.min(), 2026, 50)
                future_y = p(future_x)
                fig_p = px.scatter(filtered, x='time_idx', y='평당가', opacity=0.4, labels={'time_idx': '연도'})
                fig_p.add_traces(px.line(x=future_x, y=future_y).data)
                fig_p.data[1].line.color = 'red'
                fig_p.data[1].name = '예측 추세선'
                st.plotly_chart(fig_p, use_container_width=True)
            else:
                st.info("시계열 데이터가 부족하여 2026년 가격 예측을 진행할 수 없습니다.")

        with st.expander("📄 데이터 상세 확인"):
            st.dataframe(filtered.drop(columns=['time_idx'], errors='ignore'))
else:
    # 파일이 전혀 없을 때 안내
    st.warning("### ⚠️ 데이터를 찾을 수 없습니다.")
    st.markdown("""
    **문제 해결 방법:**
    1. 왼쪽 사이드바의 **'Browse files'** 버튼을 클릭하여 파일을 직접 업로드하세요.
    2. 파일명이 `한국부동산 가격 데이터.csv`인지 확인하세요.
    3. 현재 이 도구가 접근 가능한 파일 목록은 아래와 같습니다.
    """)
    
    st.write("🔍 **현재 디렉토리 파일 목록:**", os.listdir('.') if os.path.exists('.') else "목록 읽기 실패")