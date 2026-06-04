import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# 1. 페이지 설정
st.set_page_config(page_title="서울 특정 날짜 기온 분석 및 예측", layout="wide")
st.title("📅 서울 특정 월·일별 기온 분석 및 미래 예측")
st.write("원하는 월과 일을 선택하면, 모든 연도의 해당 날짜 기온 변화 추이와 미래 예측을 확인원하실 수 있습니다.")

# 2. 데이터 로드 및 전처리
@st.cache_data
def load_data():
    # 인코딩 오류 방지 (CP949)
    df = pd.read_csv("seoul.csv", encoding="cp949")
    
    # 칼럼명 공백 제거
    df.columns = df.columns.str.strip()
    
    # 날짜 데이터 정제 및 datetime 변환
    df['날짜'] = df['날짜'].astype(str).str.strip()
    df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
    
    # 결측치 제거
    df = df.dropna(subset=['날짜', '최고기온(℃)', '최저기온(℃)'])
    
    # 분석에 필요한 연도, 월, 일 칼럼 추출
    df['연도'] = df['날짜'].dt.year
    df['월'] = df['날짜'].dt.month
    df['일'] = df['날짜'].dt.day
    
    # 정렬
    df = df.sort_values('날짜').reset_index(drop=True)
    return df

try:
    df = load_data()
    max_year = int(df['연도'].max())

    # 3. 사이드바 입력 설정 (월, 일, 미래 연도 선택)
    st.sidebar.header("🔍 조건 설정")
    
    # 월 선택 (1월 ~ 12월)
    selected_month = st.sidebar.selectbox("1. 분석할 월 선택:", range(1, 13), index=7) # 기본값 8월
    
    # 선택한 월에 맞는 일 수 계산 (윤년 고려하여 최대 범위 설정)
    if selected_month in [4, 6, 9, 11]:
        max_day = 30
    elif selected_month == 2:
        max_day = 29
    else:
        max_day = 31
        
    selected_day = st.sidebar.selectbox("2. 분석할 일 선택:", range(1, max_day + 1), index=14) # 기본값 15일
    
    # 미래 예측 연도 선택
    predict_target_year = st.sidebar.slider(
        "3. 예측할 미래 연도 선택:",
        min_value=max_year + 1,
        max_value=2050,
        value=max_year + 10
    )

    st.subheader(f"📌 역대 {selected_month}월 {selected_day}일 기온 데이터 분석")

    # 4. 모든 연도의 특정 월·일 데이터 필터링
    filtered_df = df[(df['월'] == selected_month) & (df['일'] == selected_day)].copy()
    filtered_df = filtered_df.sort_values('연도').reset_index(drop=True)

    if filtered_df.empty:
        st.warning(f"{selected_month}월 {selected_day}일에 해당하는 데이터가 없습니다.")
    else:
        # 5. 미래 데이터 예측 로직 (선형 회귀)
        X = filtered_df[['연도']].values
        
        # 최고기온 모델 학습 및 예측
        model_max = LinearRegression().fit(X, filtered_df['최고기온(℃)'].values)
        
        # 최저기온 모델 학습 및 예측
        model_min = LinearRegression().fit(X, filtered_df['최저기온(℃)'].values)
        
        # 예측용 연도 배열 생성 (기존 마지막 연도 다음 해부터 사용자가 선택한 미래 연도까지)
        future_years = np.arange(max_year + 1, predict_target_year + 1).reshape(-1, 1)
        pred_max = model_max.predict(future_years)
        pred_min = model_min.predict(future_years)
        
        future_df = pd.DataFrame({
            '연도': future_years.flatten(),
            '최고기온(℃)': pred_max,
            '최저기온(℃)': pred_min
        })

        # 6. 주요 통계 및 예측값 화면 표시
        col1, col2 = st.columns(2)
        with col1:
            max_past = filtered_df.loc[filtered_df['최고기온(℃)'].idxmax()]
            st.metric(f"역대 최고 기온", f"{max_past['최고기온(℃)']} ℃", f"{max_past['연도']}년")
            
            target_pred_max = future_df[future_df['연도'] == predict_target_year]['최고기온(℃)'].values[0]
            st.metric(f"🔮 {predict_target_year}년 최고 기온 예측", f"{target_pred_max:.1f} ℃")
            
        with col2:
            min_past = filtered_df.loc[filtered_df['최저기온(℃)'].idxmin()]
            st.metric(f"역대 최저 기온", f"{min_past['최저기온(℃)']} ℃", f"{min_past['연도']}년")
            
            target_pred_min = future_df[future_df['연도'] == predict_target_year]['최저기온(℃)'].values[0]
            st.metric(f"🔮 {predict_target_year}년 최저 기온 예측", f"{target_pred_min:.1f} ℃")

        # 7. 꺾은선 그래프 시각화 (X축: 연도)
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # 요구사항 색상 설정 (라일락, 하늘색)
        lilac_color = "#C8A2C8"
        skyblue_color = "#87CEEB"
        
        # 과거 데이터 선 그래프 그리기
        ax.plot(filtered_df['연도'], filtered_df['최고기온(℃)'], label='과거 최고기온 (Max Temp)', color=lilac_color, marker='o', markersize=4, linewidth=1.5)
        ax.plot(filtered_df['연도'], filtered_df['최저기온(℃)'], label='과거 최저기온 (Min Temp)', color=skyblue_color, marker='o', markersize=4, linewidth=1.5)
        
        # 미래 예측 데이터 선 그래프 그리기 (추세선 형태의 점선 스타일)
        ax.plot(future_df['연도'], future_df['최고기온(℃)'], label='🔮 미래 최고 예측', color="#9400D3", linestyle='--', linewidth=2)
        ax.plot(future_df['연도'], future_df['최저기온(℃)'], label='🔮 미래 최저 예측', color="#00BFFF", linestyle='--', linewidth=2)

        # 그래프 꾸미기 및 폰트 설정 대안
        ax.set_title(f"📌 서울 {selected_month}월 {selected_day}일 연도별 기온 변화 및 추세 예측", fontsize=14, pad=15)
        ax.set_xlabel("Year (연도)", fontsize=11)
        ax.set_ylabel("Temperature (기온, ℃)", fontsize=11)
        
        ax.grid(True, linestyle='--', alpha=0.5)
        
        # 범례 표시 요구사항 만족
        ax.legend(loc="upper right", fontsize=10)
        
        # 스트림릿 출력
        st.pyplot(fig)
        
        # 데이터 테이블 탭 분리 표시
        tab1, tab2 = st.tabs(["📄 역대 전체 연도 데이터", "🔮 연도별 미래 예측값"])
        with tab1:
            st.dataframe(filtered_df[['연도', '평균기온(℃)', '최저기온(℃)', '최고기온(℃)']].set_index('연도'), use_container_width=True)
        with tab2:
            st.dataframe(future_df.rename(columns={'최저기온(℃)':'예측 최저(℃)', '최고기온(℃)':'예측 최고(℃)'}).set_index('연도'), use_container_width=True)

except Exception as e:
    st.error(f"데이터를 처리하는 중 오류가 발생했습니다: {e}")
