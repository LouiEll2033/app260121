import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
import os

# [1. 페이지 기본 설정]
st.set_page_config(
    page_title="전남 태풍 피해 분석 대시보드",
    page_icon="🌪️",
    layout="wide"
)

# [2. 데이터 로드 및 전처리]
@st.cache_data
def load_data():
    # 파일명 확인 (업로드된 파일명과 정확히 일치해야 함)
    file_name = '전라남도_연도별 태풍피해 현황_20251104.csv'
    
    if not os.path.exists(file_name):
        return None

    try:
        # 한글 인코딩 문제 해결 (cp949 또는 utf-8-sig)
        try:
            df = pd.read_csv(file_name, encoding='utf-8-sig')
        except:
            df = pd.read_csv(file_name, encoding='cp949')

        # 데이터 클렌징 함수 (더 견고한 파싱 로직)
        def parse_val(text, data_type='jeonnam'):
            if pd.isna(text): return 0.0
            text = str(text).replace(',', '').strip()
            
            if data_type == 'jeonnam':
                # 가로 안의 숫자 추출 (예: 15(2) -> 2)
                match = re.search(r'\((\d+\.?\d*)\)', text)
                return float(match.group(1)) if match else 0.0
            else:
                # 가로 앞의 숫자 추출 (예: 15(2) -> 15)
                match = re.search(r'^(\d+\.?\d*)', text)
                return float(match.group(1)) if match else 0.0

        # 전남 및 전국 데이터 컬럼 생성 (기존 컬럼명 기준)
        target_cols = {
            '인명': '인명피해 규모 전국(전남)_명',
            '재산': '재산피해규모 전국(전남)_억 원',
            '복구': '복구액 전국(전남)_억 원'
        }

        for key, col in target_cols.items():
            if col in df.columns:
                df[f'{key}_전남'] = df[col].apply(lambda x: parse_val(x, 'jeonnam'))
                df[f'{key}_전국'] = df[col].apply(lambda x: parse_val(x, 'national'))
        
        return df
    except Exception as e:
        st.error(f"데이터 처리 중 오류 발생: {e}")
        return None

df = load_data()

# [3. 대시보드 UI 구성]
if df is not None:
    st.title("🌪️ 전라남도 연도별 태풍 피해 대시보드")
    
    # 사이드바: 연도 필터
    with st.sidebar:
        st.header("📊 분석 설정")
        years = sorted(df['연도'].unique())
        selected_years = st.select_slider(
            "분석 기간 선택", 
            options=years, 
            value=(min(years), max(years))
        )
        
        st.divider()
        st.info("💡 **실행 가이드**\n\nVS Code 터미널에서 아래 명령어를 입력하세요:\n`streamlit run typhoon_dashboard.py`")

    # 선택된 연도 데이터 필터링
    f_df = df[(df['연도'] >= selected_years[0]) & (df['연도'] <= selected_years[1])]

    # 상단 주요 지표 (KPI)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("총 태풍 횟수", f"{len(f_df)}건")
    with c2:
        st.metric("총 인명 피해(전남)", f"{int(f_df['인명_전남'].sum()):,}명")
    with c3:
        st.metric("총 재산 피해(전남)", f"{f_df['재산_전남'].sum():,.1f}억")
    with c4:
        st.metric("총 복구액(전남)", f"{f_df['복구_전남'].sum():,.1f}억")

    st.divider()

    # 4가지 분석 탭
    t1, t2, t3, t4 = st.tabs(["📅 시계열 추이", "🥇 피해 순위", "⚖️ 전국 대비 비중", "📈 상관관계 분석"])

    with t1:
        st.subheader("연도별 피해 규모 변화 추이")
        # 연도별 합계 데이터 계산
        yearly_sum = f_df.groupby('연도').agg({'재산_전남':'sum', '복구_전남':'sum', '인명_전남':'sum'}).reset_index()
        
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(x=yearly_sum['연도'], y=yearly_sum['재산_전남'], name='재산피해(억)', marker_color='#E74C3C'))
        fig1.add_trace(go.Scatter(x=yearly_sum['연도'], y=yearly_sum['복구_전남'], name='복구액(억)', line=dict(color='#3498DB', width=3)))
        fig1.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode="x unified",
            xaxis_title="연도",
            yaxis_title="금액 (억 원)"
        )
        st.plotly_chart(fig1, use_container_width=True)

    with t2:
        st.subheader("가장 피해가 컸던 태풍 TOP 10 (전남 기준)")
        top10 = f_df.sort_values('재산_전남', ascending=False).head(10)
        fig2 = px.bar(
            top10, x='재산_전남', y='태풍명', orientation='h', 
            color='재산_전남', color_continuous_scale='Reds',
            labels={'재산_전남':'재산피해(억 원)', '태풍명':'태풍 이름'},
            text_auto='.1f'
        )
        fig2.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig2, use_container_width=True)

    with t3:
        st.subheader("전국 피해액 중 전라남도 피해 비중 (%)")
        f_df['비중'] = (f_df['재산_전남'] / f_df['재산_전국'] * 100).fillna(0)
        
        fig3 = px.line(
            f_df, x='연도', y='비중', markers=True, text='태풍명',
            hover_data=['재산_전남', '재산_전국'],
            title="태풍 발생 시 전국 피해 규모 대비 전남 비중"
        )
        fig3.update_traces(textposition="top center")
        st.plotly_chart(fig3, use_container_width=True)
        
        avg_share = f_df['비중'].mean()
        st.info(f"선택 기간 내 전남 지역의 평균 재산 피해 비중은 약 **{avg_share:.2f}%** 입니다.")

    with t4:
        st.subheader("재산 피해액과 복구비의 상관관계")
        try:
            fig4 = px.scatter(
                f_df, x='재산_전남', y='복구_전남', trendline="ols",
                size='인명_전남', hover_name='태풍명', color='연도',
                labels={'재산_전남': '재산피해(억)', '복구_전남': '복구액(억)'},
                title="피해 규모와 복구 비용의 선형 관계"
            )
            st.plotly_chart(fig4, use_container_width=True)
            
            corr = f_df['재산_전남'].corr(f_df['복구_전남'])
            st.success(f"두 변수 간의 상관계수는 **{corr:.2f}**입니다. (1에 가까울수록 피해액만큼 복구비가 비례하여 발생함을 의미)")
        except:
            st.warning("상관 분석 추세선을 보려면 `pip install statsmodels` 설치가 필요합니다.")
            fig4 = px.scatter(f_df, x='재산_전남', y='복구_전남', size='인명_전남', hover_name='태풍명')
            st.plotly_chart(fig4, use_container_width=True)

    with st.expander("📝 상세 데이터 리스트 (전라남도 수치 추출 결과)"):
        st.dataframe(f_df[['연도', '태풍명', '발생기간', '인명_전남', '재산_전남', '복구_전남']].sort_values('연도', ascending=False))

else:
    st.error("데이터 파일을 로드할 수 없습니다.")
    st.markdown(f"""
    ### ⚠️ 문제가 발생했나요?
    1. **파일 확인**: 프로젝트 폴더 안에 `전라남도_연도별 태풍피해 현황_20251104.csv` 파일이 있는지 확인하세요.
    2. **파일명 일치**: 파일 이름의 공백이나 특수문자가 위 코드와 정확히 일치해야 합니다.
    3. **인터프리터**: VS Code 하단에 올바른 Python 버전이 선택되어 있는지 확인하세요.
    """)
