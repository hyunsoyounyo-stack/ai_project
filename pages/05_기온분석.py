import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 1. 페이지 설정
st.set_page_config(page_title="서울 기온 데이터 분석", layout="wide")
st.title("🌡️ 서울 연도별 기온 데이터 시각화")
st.write("1907년부터의 서울 기온 데이터를 조회하고 그래프로 확인하세요.")

# 2. 데이터 로드 및 전처리 (캐싱 처리로 속도 향상)
@st.cache_data
def load_data():
    # 데이터 읽기
    df = pd.read_csv("seoul.csv")
    
    # 칼럼명 공백 제거
    df.columns = df.columns.str.strip()
    
    # 날짜 데이터 앞뒤 공백 및 탭(\t) 제거 후 datetime 변환
    df['날짜'] = df['날짜'].astype(str).str.strip()
    df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
    
    # 결측치 및 날짜 변환 실패 데이터 제거
    df = df.dropna(subset=['날짜', '최고기온(℃)', '최저기온(℃)'])
    
    # 정렬
    df = df.sort_values('날짜').reset_index(drop=True)
    return df

try:
    df = load_data()

    # 3. 사이드바 - 날짜 선택기
    min_date = df['날짜'].min().to_pydatetime()
    max_date = df['날짜'].max().to_pydatetime()

    st.sidebar.header("📅 기간 선택")
    start_date, end_date = st.sidebar.date_input(
        "조회할 범위를 선택하세요:",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

    # 4. 데이터 필터링
    filtered_df = df[(df['날짜'] >= pd.to_datetime(start_date)) & (df['날짜'] <= pd.to_datetime(end_date))]

    if filtered_df.empty:
        st.warning("선택한 기간에 데이터가 없습니다. 다른 기간을 선택해 주세요.")
    else:
        # 주요 통계 요약 표시
        col1, col2 = st.columns(2)
        with col1:
            max_temp_row = filtered_df.loc[filtered_df['최고기온(℃)'].idxmax()]
            st.metric("선택 기간 최고 기온", f"{max_temp_row['최고기온(℃)']} ℃", f"({max_temp_row['날짜'].strftime('%Y-%m-%d')})")
        with col2:
            min_temp_row = filtered_df.loc[filtered_df['최저기온(℃)'].idxmin()]
            st.metric("선택 기간 최저 기온", f"{min_temp_row['최저기온(℃)']} ℃", f"({min_temp_row['날짜'].strftime('%Y-%m-%d')})")

        # 5. 꺾은선 그래프 그리기
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # 지정된 색상 설정 (라일락: #C8A2C8, 하늘색: #87CEEB)
        lilac_color = "#C8A2C8"
        skyblue_color = "#87CEEB"
        
        # 그래프 플롯 (범례 표시를 위한 label 지정)
        ax.plot(filtered_df['날짜'], filtered_df['최고기온(℃)'], label='Max Temp (최고기온)', color=lilac_color, linewidth=1.5)
        ax.plot(filtered_df['날짜'], filtered_df['최저기온(℃)'], label='Min Temp (최저기온)', color=skyblue_color, linewidth=1.5)
        
        # 그래프 꾸미기
        ax.set_title("📌 최고/최저 기온 변화 추이", fontsize=14, pad=15)
        ax.set_xlabel("Date (날짜)", fontsize=11)
        ax.set_ylabel("Temperature (기온, ℃)", fontsize=11)
        
        # 날짜 포맷팅 (데이터 양에 따라 보기 좋게 조절)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        fig.autofmt_xdate() # 날짜 겹침 방지 회전
        
        ax.grid(True, linestyle='--', alpha=0.5)
        
        # 범례 표시 (요구사항 반영)
        ax.legend(loc="upper right", fontsize=10)
        
        # 스트림릿에 그래프 출력
        st.pyplot(fig)
        
        # 데이터 테이블 보여주기 (선택 사항)
        with st.expander("📄 선택한 기간의 상세 데이터 보기"):
            st.dataframe(filtered_df[['날짜', '평균기온(℃)', '최저기온(℃)', '최고기온(℃)']], use_container_width=True)

except Exception as e:
    st.error(f"데이터를 처리하는 중 오류가 발생했습니다: {e}")
    st.info("csv 파일의 컬럼명이나 데이터 형식을 다시 한번 확인해 주세요.")
