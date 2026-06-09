import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="서울시 연령별 미디어 사용량 분석", layout="wide")
st.title("📊 2013년 서울시 연령별 스마트폰/미디어 사용량 분석")
st.markdown("업로드된 `aa.csv` 데이터를 바탕으로 연령대별 사용 빈도와 평균 사용 시간을 분석합니다.")

# 2. 데이터 로드 함수 (캐싱 처리)
@st.cache_data
def load_data():
    # 데이터 불러오기 (헤더가 2번 줄까지 연결되어 있어 skiprows 활용 및 컬럼명 재정의)
    df = pd.read_csv("aa.csv", skiprows=2, header=None)
    df.columns = ["구분별(1)", "구분별(2)", "1일평균사용시간", "1시간이하", "1-3시간", "3-5시간", "5시간초과"]
    
    # '연령별' 데이터만 필터링
    age_df = df[df["구분별(1)"] == "연령별"].copy()
    
    # 수치형 데이터 변환 (공백 제거 및 float 변환)
    numeric_cols = ["1일평균사용시간", "1시간이하", "1-3시간", "3-5시간", "5시간초과"]
    for col in numeric_cols:
        age_df[col] = pd.to_numeric(age_df[col], errors='coerce')
        
    return age_df

try:
    df_age = load_data()

    # 화면을 두 개의 구역(Column)으로 분할
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("🎵 연령대별 사용 빈도 (구간별 비율)")
        
        # 시각화를 위해 데이터 재구조화 (Melt)
        melted_df = df_age.melt(
            id_vars=["구분별(2)"], 
            value_vars=["1시간이하", "1-3시간", "3-5시간", "5시간초과"],
            var_name="사용시간_구간", 
            value_name="비율"
        )
        
        # 한글 폰트 설정 (스트림릿 클라우드 리눅스 환경 고려하여 기본 폰트 구성 혹은 폰트 비지정 시 matplotlib 기본 대응)
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['axes.unicode_minus'] = False
        
        # 그래프 생성 (라일락 색상 반영: #C8A2C8)
        fig, ax = plt.subplots(figsize=(10, 6))
        lilac_color = "#C8A2C8"
        
        sns.barplot(
            data=melted_df, 
            x="구분별(2)", 
            y="비율", 
            hue="사용시간_구간", 
            palette=[lilac_color, "#DCD0FF", "#B19CD9", "#9370DB"], # 라일락 및 유사 자수정/보라 계열
            ax=ax
        )
        
        ax.set_title("연령대별 사용 시간대 분포 (%)", fontsize=14, pad=15)
        ax.set_xlabel("연령대", fontsize=12)
        ax.set_ylabel("비율 (%)", fontsize=12)
        ax.legend(title="이용 시간 구간")
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        st.pyplot(fig)

    with col2:
        st.subheader("🔍 연령대별 평균 사용시간 조회")
        
        # 나잇대 선택 셀렉트박스
        age_list = df_age["구분별(2)"].tolist()
        selected_age = st.selectbox("나잇대를 선택하세요:", age_list)
        
        # 선택된 나이의 데이터 추출
        selected_data = df_age[df_age["구분별(2)"] == selected_age].iloc[0]
        avg_time = selected_data["1일평균사용시간"]
        
        # 깔끔한 카드 형태로 평균 사용 시간 표시
        st.info(f"### 🕒 {selected_age} 평균 사용 시간")
        st.metric(label="하루 평균", value=f"{avg_time} 시간")
        
        # 추가 세부 지표 표시
        st.write(f"**{selected_age}의 상세 분포:**")
        st.write(f"- 1시간 이하: {selected_data['1시간이하']}%")
        st.write(f"- 1~3 시간: {selected_data['1-3시간']}%")
        st.write(f"- 3~5 시간: {selected_data['3-5시간']}%")
        st.write(f"- 5시간 초과: {selected_data['5시간초과']}%")

except FileNotFoundError:
    st.error("📂 `aa.csv` 파일을 찾을 수 없습니다. GitHub 저장소에 코드가 있는 위치와 같은 곳에 데이터를 업로드해 주세요.")
except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")
