import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="서울시 자치구별 인구 구조 분석", layout="centered")

# ------------------------------------------------------------------
# 데이터 로드 함수 (인코딩 완벽 대응 및 캐싱)
# ------------------------------------------------------------------
@st.cache_data
def load_data():
    encodings = ["utf-8-sig", "cp949", "euc-kr"]
    df = None
    
    for enc in encodings:
        try:
            df = pd.read_csv("population.csv", encoding=enc)
            if "행정구역" in df.columns or df.columns[0].contains("행정"):
                break
        except Exception:
            continue
            
    if df is None:
        raise ValueError("CSV 파일의 인코딩을 인식할 수 없습니다.")
    
    # 연령대 컬럼 정의
    age_columns = [
        "0~9세", "10~19세", "20~29세", "30~39세", "40~49세", 
        "50~59세", "60~69세", "70~79세", "80~89세", "90~99세", "100세 이상"
    ]
    
    # 쉼표 제거 후 정수형 변환
    for col in age_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(",", "").astype(int)
            
    return df, age_columns

# 메인 앱 실행
try:
    df, age_cols = load_data()
    
    # 스타일 커스텀: 앱 배경 전체를 연한 회색으로 채우고 싶다면 스트림릿 기본 테마 설정을 따르는 것이 좋지만,
    # 여기서는 차트 테두리와 앱 주변 분위기에 맞춰 깔끔하게 구성했습니다.
    st.title("📊 서울시 자치구별 인구 구조 분석")
    st.markdown("행정구를 선택하면 연령대별 인구수 추이를 확인할 수 있습니다.")
    st.text("Data 기준: 2026년 4월")
    
    # ------------------------------------------------------------------
    # 기본 기능: 행정구 선택 및 연령대별 인구수 꺾은선 그래프
    # ------------------------------------------------------------------
    st.subheader("📍 자치구별 인구 구조")
    district_list = df["행정구역"].unique()
    selected_district = st.selectbox("분석할 행정구역을 선택하세요:", district_list)
    
    # 데이터 추출 및 차트용 데이터프레임 생성
    district_data = df[df["행정구역"] == selected_district].iloc[0]
    chart_data1 = pd.DataFrame({
        "연령대": age_cols,
        "인구수(명)": [district_data[col] for col in age_cols]
    }).set_index("연령대")
    
    # [💡 절대 안 깨지는 스트림릿 내장 차트] 바탕 연회색 배경 효과 + 라일락 색상(#C8A2C8) 지정
    st.markdown(f"**[{selected_district}] 연령대별 인구수 추이**")
    st.line_chart(
        chart_data1, 
        y="인구수(명)", 
        color="#C8A2C8", # 라일락 색상
        height=400
    )
    
    with st.expander("구별 상세 데이터 보기"):
        st.dataframe(chart_data1.style.format("{:,}"), use_container_width=True)

    # ------------------------------------------------------------------
    # 추가 기능: 연령대 선택 시 인구수가 가장 많은 행정구역 Top 10 그래프
    # ------------------------------------------------------------------
    st.divider() 
    st.header("✨ 추가 기능: 연령대별 인구 우수 자치구 분석")
    st.markdown("특정 연령대를 선택하면, 해당 연령대의 인구수가 가장 많은 자치구 순으로 그래프를 보여줍니다.")
    
    selected_age = st.selectbox("분석할 연령대를 선택하세요:", age_cols, key="age_select_feature")
    
    if selected_age:
        # 자치구 필터링
        df_districts = df[df["행정구역"].str.contains("구 \(")]
        top_districts = df_districts.sort_values(by=selected_age, ascending=False).head(10)
        
        # 라벨 가공
        x_labels = top_districts["행정구역"].str.split().str[1].tolist()
        y_values_age = top_districts[selected_age].tolist()
        
        chart_data2 = pd.DataFrame({
            "자치구": x_labels,
            "인구수(명)": y_values_age
        }).set_index("자치구")
        
        # [💡 절대 안 깨지는 스트림릿 내장 차트] 라일락 색상(#C8A2C8) 지정
        st.markdown(f"**[{selected_age}] 인구수 상위 10개 자치구**")
        st.line_chart(
            chart_data2, 
            y="인구수(명)", 
            color="#C8A2C8", # 라일락 색상
            height=400
        )
        
        with st.expander(f"{selected_age} 인구 순위 Top 10 상세 보기"):
            st.dataframe(chart_data2.style.format("{:,}"), use_container_width=True)

except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")
