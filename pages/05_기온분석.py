import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sklearn.linear_model import LinearRegression

# 1. 페이지 설정
st.set_page_config(page_title="서울 기온 분석 및 미래 예측", layout="wide")
st.title("🌡️ 서울 연도별 기온 분석 및 미래 예측")
st.write("과거 기온 데이터를 기반으로 미래의 최고/최저 기온을 예측하고 그래프로 확인하세요.")

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
    
    # 연도, 월, 일 칼럼 추가 (예측 모델 학습용)
    df['연도'] = df['날짜'].dt.year
    df['월일'] = df['날짜'].dt.strftime('%m-%d')
    
    # 정렬
    df = df.sort_values('날짜').reset_index(drop=True)
    return df

try:
    df = load_data()
    
    # 데이터의 실제 시작/종료 연도 파악
    min_year = int(df['연도'].min())
    max_year = int(df['연도'].max())

    # 3. 사이드바 입력 설정
    st.sidebar.header("📅 설정 및 예측 범위")
    
    # 과거 데이터 조회 범위 선택
    start_date, end_date = st.sidebar.date_input(
        "1. 과거 데이터 조회 범위:",
        value=[df['날짜'].min().to_pydatetime(), df['날짜'].max().to_pydatetime()],
        min_value=df['날짜'].min().to_pydatetime(),
        max_value=df['날짜'].max().to_pydatetime()
    )
    
    # 미래 예측 연도 선택 (기존 데이터 마지막 연도 다음 해 ~ 2050년)
    predict_target_year = st.sidebar.slider(
        "2. 예측할 미래 연도 선택:",
        min_value=max_year + 1,
        max_value=2050,
        value=max_year + 5
    )

    # 4. 과거 데이터 필터링 및 통계
    filtered_df = df[(df['날짜'] >= pd.to_datetime(start_date)) & (df['날짜'] <= pd.to_datetime(end_date))].copy()

    # 5. 미래 데이터 예측 로직 (머신러닝 선형 회귀)
    # 각 날짜별(월-일) 기온 변화 경향성을 학습하여 미래 특정 해의 365일 기온을 예측합니다.
    future_dates = pd.date_range(start=f"{predict_target_year}-01-01", end=f"{predict_target_year}-12-31", freq='D')
    future_df = pd.DataFrame({'날짜': future_dates})
    future_df['연도'] = future_df['날짜'].dt.year
    future_df['월일'] = future_df['날짜'].dt.strftime('%m-%d')
    
    pred_max_list = []
    pred_min_list = []
    
    # 월-일별로 모델을 쪼개어 학습 (계절성 반영)
    for target_md in future_df['월일']:
        day_data = df[df['월일'] == target_md]
        
        if len(day_data) > 5: # 학습 데이터가 충분한 경우에만 진행
            X = day_data[['연도']].values
            
            # 최고기온 모델 학습 및 예측
            model_max = LinearRegression().fit(X, day_data['최고기온(℃)'].values)
            pred_max = model_max.predict([[predict_target_year]])[0]
            
            # 최저기온 모델 학습 및 예측
            model_min = LinearRegression().fit(X, day_data['최저기온(℃)'].values)
            pred_min = model_min.predict([[predict_target_year]])[0]
        else:
            pred_max, pred_min = np.nan, np.nan
            
        pred_max_list.append(pred_max)
        pred_min_list.append(pred_min)
        
    future_df['최고기온(℃)'] = pred_max_list
    future_df['최저기온(℃)'] = pred_min_list
    future_df = future_df.dropna()

    # 6. 화면 레이아웃 구성 및 메트릭 표시
    col1, col2 = st.columns(2)
    with col1:
        if not filtered_df.empty:
            max_past = filtered_df.loc[filtered_df['최고기온(℃)'].idxmax()]
            st.metric(f"선택 과거 기간 최고 기온", f"{max_past['최고기온(℃)']} ℃", f"({max_past['날짜'].strftime('%Y-%m-%d')})")
        if not future_df.empty:
            max_fut = future_df.loc[future_df['최고기온(℃)'].idxmax()]
            st.metric(f"🔮 {predict_target_year}년 예측 최고 기온", f"{max_fut['최고기온(℃)']:.1f} ℃", f"({max_fut['날짜'].strftime('%m-%d')} 예상)")
            
    with col2:
        if not filtered_df.empty:
            min_past = filtered_df.loc[filtered_df['최저기온(℃)'].idxmin()]
            st.metric(f"선택 과거 기간 최저 기온", f"{min_past['최저기온(℃)']} ℃", f"({min_past['날짜'].strftime('%Y-%m-%d')})")
        if not future_df.empty:
            min_fut = future_df.loc[future_df['최저기온(℃)'].idxmin()]
            st.metric(f"🔮 {predict_target_year}년 예측 최저 기온", f"{min_fut['최저기온(℃)']:.1f} ℃", f"({min_fut['날짜'].strftime('%m-%d')} 예상)")

    # 7. 꺾은선 그래프 시각화
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # 요구사항 색상 설정 (라일락, 하늘색)
    lilac_color = "#C8A2C8"
    skyblue_color = "#87CEEB"
    
    # 과거 데이터 그리기
    if not filtered_df.empty:
        ax.plot(filtered_df['날짜'], filtered_df['최고기온(℃)'], label='과거 최고기온 (Max Temp)', color=lilac_color, alpha=0.8, linewidth=1)
        ax.plot(filtered_df['날짜'], filtered_df['최저기온(℃)'], label='과거 최저기온 (Min Temp)', color=skyblue_color, alpha=0.8, linewidth=1)
        
    # 미래 예측 데이터 그리기 (스타일을 점선 '--' 및 진한 색상으로 구분)
    if not future_df.empty:
        ax.plot(future_df['날짜'], future_df['최고기온(℃)'], label=f'🔮 {predict_target_year}년 예측 최고', color="#9400D3", linestyle='--', linewidth=2)
        ax.plot(future_df['날짜'], future_df['최저기온(℃)'], label=f'🔮 {predict_target_year}년 예측 최저', color="#00BFFF", linestyle='--', linewidth=2)

    # 그래프 스타일링
    ax.set_title(f"📌 서울 기온 변화 추이 및 {predict_target_year}년 미래 예측", fontsize=14, pad=15)
    ax.set_xlabel("Date (날짜)", fontsize=11)
    ax.set_ylabel("Temperature (기온, ℃)", fontsize=11)
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()
    ax.grid(True, linestyle='--', alpha=0.5)
    
    # 범례 표시 요구사항 만족
    ax.legend(loc="upper right", fontsize=10)
    
    # 스트림릿 출력
    st.pyplot(fig)
    
    # 데이터 테이블 탭 분리 표시
    tab1, tab2 = st.tabs(["📄 과거 선택 데이터", "🔮 미래 예측 데이터"])
    with tab1:
        st.dataframe(filtered_df[['날짜', '최저기온(℃)', '최고기온(℃)']], use_container_width=True)
    with tab2:
        st.dataframe(future_df[['날짜', '최저기온(℃)', '최고기온(℃)']].rename(columns={'최저기온(℃)':'예측 최저(℃)', '최고기온(℃)':'예측 최고(℃)'}), use_container_width=True)

except Exception as e:
    st.error(f"데이터를 처리하는 중 오류가 발생했습니다: {e}")
