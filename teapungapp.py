import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
import re

# 1. 페이지 설정 (최상단 배치)
st.set_page_config(page_title="한국 부동산 가격 예측기", layout="wide", page_icon="🏠")

def clean_value(val):
    """문자열에서 숫자와 소수점만 추출하는 안전한 함수"""
    if pd.isna(val) or val == '': return np.nan
    s = str(val).strip()
    # 숫자와 마침표(.)를 제외한 모든 문자 제거 (콤마, 한글, 공백 등)
    s = re.sub(r'[^0-9.]', '', s)
    if s == '' or s == '.': return np.nan
    try:
        return float(s)
    except:
        return np.nan

@st.cache_data
def load_data_robust(file_source):
    """다양한 형식의 부동산 데이터를 안전하게 로드하는 함수"""
    try:
        df = None
        # 인코딩 순차 시도 (한글 깨짐 방지)
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
            return None, "파일 내용을 읽을 수 없습니다. 올바른 CSV 파일인지 확인해주세요."

        # 컬럼명 정리 (공백 제거)
        df.columns = [str(col).strip() for col in df.columns]
        
        # 2. 필수 컬럼 자동 매핑 (유연한 검색)
        col_patterns = {
            '지역명': r'지역|시도|city',
            '규모구분': r'규모|면적|size',
            '연도': r'연도|year',
            '월': r'월|month',
            '분양가격': r'분양가격|가격|price'
        }
        
        final_mapping = {}
        for key, pattern in col_patterns.items():
            found_col = next((c for c in df.columns if re.search(pattern, c)), None)
            if found_col:
                final_mapping[key] = found_col
        
        # 필수 컬럼 검증 (지역, 연도, 월, 가격은 필수)
        essential_keys = ['지역명', '연도', '월', '분양가격']
        if not all(k in final_mapping for k in essential_keys):
            return None, f"필수 컬럼을 찾을 수 없습니다. (현재 컬럼: {list(df.columns)})"

        # 데이터 프레임 재구성
        new_df = pd.DataFrame()
        new_df['지역명'] = df[final_mapping['지역명']].astype(str)
        # 규모구분은 없을 경우 '전체'로 처리
        if '규모구분' in final_mapping:
            new_df['규모구분'] = df[final_mapping['규모구분']].astype(str)
        else:
            new_df['규모구분'] = '모든면적'
            
        new_df['연도'] = pd.to_numeric(df[final_mapping['연도']], errors='coerce')
        new_df['월'] = pd.to_numeric(df[final_mapping['월']], errors='coerce')
        new_df['분양가격'] = df[final_mapping['분양가격']].apply(clean_value)

        # 결측치 제거
        new_df = new_df.dropna(subset=['연도', '월', '분양가격'])
        
        # 날짜 객체 생성
        def create_date(row):
            try:
                return pd.Timestamp(year=int(row['연도']), month=int(row['월']), day=1)
            except:
                return pd.NaT

        new_df['날짜'] = new_df.apply(create_date, axis=1)
        new_df = new_df.dropna(subset=['날짜'])
        
        # 평당 가격 환산
        new_df['평당가'] = new_df['분양가격'] * 3.3
        
        return new_df.sort_values('날짜'), None

    except Exception as e:
        return None, f"데이터 처리 중 오류가 발생했습니다: {str(e)}"

# --- UI 메인 섹션 ---
st.title("🏠 부동산 지역별 분양가 분석 및 2026 예측")

# 파일 로딩 로직
DEFAULT_FILE = '한국부동산 가격 데이터.csv'
uploaded_file = st.sidebar.file_uploader("📂 데이터 업로드 (CSV)", type=['csv'])

# 타겟 파일 결정
target_source = None
if uploaded_file:
    target_source = uploaded_file
elif os.path.exists(DEFAULT_FILE):
    target_source = DEFAULT_FILE

# 데이터 분석 시작
if target_source:
    df, error = load_data_robust(target_source)
    
    if error:
        st.error(f"❌ 분석 에러: {error}")
        st.info("파일의 컬럼명이 '지역명', '연도', '월', '분양가격'을 포함하고 있는지 확인해주세요.")
    else:
        st.sidebar.success("✅ 데이터가 성공적으로 로드되었습니다.")
        
        # 필터링 UI
        st.markdown("### 🔍 분석 조건 설정")
        col1, col2 = st.columns(2)
        
        with col1:
            all_regions = sorted(df['지역명'].unique())
            sel_region = st.selectbox("📍 분석 지역 선택", all_regions, index=0)
            
        with col2:
            all_sizes = sorted(df['규모구분'].unique())
            sel_size = st.selectbox("📏 면적 규모 선택", all_sizes, index=0)

        # 데이터 필터링
        filtered = df[(df['지역명'] == sel_region) & (df['규모구분'] == sel_size)]

        if filtered.empty:
            st.warning(f"⚠️ '{sel_region}' 지역의 '{sel_size}' 조건에 해당하는 데이터가 없습니다.")
        else:
            # 1. 가격 추이 그래프
            st.subheader(f"📈 {sel_region} - {sel_size} 분양가 추이")
            fig = px.line(filtered, x='날짜', y='평당가', markers=True,
                          labels={'평당가': '평당 가격(만원)', '날짜': '조사 시점'},
                          template="plotly_white")
            fig.update_traces(line_color='#007BFF', line_width=3)
            st.plotly_chart(fig, use_container_width=True)

            # 2. 2026년 가격 예측
            st.divider()
            st.subheader("🔮 2026년 예상 분양가 예측")
            
            # 회귀 분석을 위한 시간 수치화 (예: 2015.83, 2016.0)
            filtered['time_val'] = filtered['연도'] + (filtered['월'] - 1) / 12
            x = filtered['time_val'].values
            y = filtered['평당가'].values

            if len(x) >= 2:
                # Numpy 1차 선형 회귀 (y = ax + b)
                coefficients = np.polyfit(x, y, 1)
                poly_func = np.poly1d(coefficients)
                
                # 2026.0 시점 예측
                pred_2026 = poly_func(2026.0)
                current_val = y[-1]
                
                # 대시보드 지표
                m1, m2, m3 = st.columns(3)
                m1.metric("최근 실거래 평당가", f"{current_val:,.0f} 만원")
                m2.metric("2026년 예상 분양가", f"{max(0, pred_2026):,.0f} 만원")
                
                growth = ((pred_2026 - current_val) / current_val) * 100
                m3.metric("현재 대비 예상 등락률", f"{growth:+.1f}%")

                # 예측 추세선 그래프
                st.write("#### 📉 향후 추세 전망 시나리오")
                future_x = np.linspace(x.min(), 2026, 50)
                future_y = poly_func(future_x)
                
                fig_trend = px.scatter(filtered, x='time_val', y='평당가', opacity=0.5, 
                                      labels={'time_val': '연도', '평당가': '가격(만원)'})
                fig_trend.add_traces(px.line(x=future_x, y=future_y).data)
                fig_trend.data[1].line.color = 'red'
                fig_trend.data[1].name = '예측 추세선'
                st.plotly_chart(fig_trend, use_container_width=True)
                
                st.info("💡 위 예측은 과거 데이터를 기반으로 한 선형 추세이며, 정책 및 경제 상황에 따라 실제와 다를 수 있습니다.")
            else:
                st.warning("데이터 포인트가 부족하여(2개 미만) 미래 예측을 수행할 수 없습니다.")

        # 데이터 테이블 확인
        with st.expander("📄 데이터 상세 내역 보기"):
            st.dataframe(filtered.drop(columns=['time_val'], errors='ignore'))
else:
    # 파일이 로드되지 않았을 때의 메인 화면 가이드
    st.info("### 👋 부동산 가격 예측기에 오신 것을 환영합니다!")
    st.markdown("""
    분석을 시작하려면 먼저 **데이터 파일(CSV)**을 불러와야 합니다.
    
    1. 왼쪽 사이드바의 **[Browse files]** 버튼을 클릭하세요.
    2. 사용자님이 업로드하신 `한국부동산 가격 데이터.csv` 파일을 선택하세요.
    3. 파일이 인식되면 즉시 지역별 분석과 2026년 예측 결과가 나타납니다.
    """)
    
    # 예시 이미지 대용 아이콘
    st.image("https://img.icons8.com/clouds/300/real-estate.png", width=200)

# 도움말 섹션
st.sidebar.divider()
st.sidebar.caption("v1.5 - 컬럼 자동 인식 및 Numpy 엔진 탑재")