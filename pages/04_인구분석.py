import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 페이지 설정
st.set_page_config(page_title="서울시 자치구별 인구 구조 분석", layout="centered")

# 데이터 로드 함수 (캐싱 적용)
@st.cache_data
def load_data():
    # CSV 파일 읽기 (인코딩은 환경에 따라 cp949 또는 utf-8-sig 대응)
    try:
        df = pd.read_csv("population.csv", encoding="utf-8-sig")
    except UnicodeDecodeError:
        df = pd.read_csv("population.csv", encoding="cp949")
    
    # 쉼표(,)가 포함된 숫자 데이터 문자열을 숫자로 변환
    age_columns = [
        "0~9세", "10~19세", "20~29세", "30~39세", "40~49세", 
        "50~59세", "60~69세", "70~79세", "80~89세", "90~99세", "100세 이상"
    ]
    
    for col in age_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(",", "").astype(int)
            
    return df, age_columns

# 데이터 불러오기
try:
    df, age_cols = load_data()
    
    st.title("📊 서울시 자치구별 인구 구조 분석")
    st.markdown("행정구를 선택하면 연령대별 인구수 추이를 꺾은선 그래프로 확인할 수 있습니다.")
    st.text("Data 기준: 2026년 4월")
    
    # 1. 행정구 선택 사이드바/셀렉트박스
    district_list = df["행정구역"].unique()
    selected_district = st.selectbox("분석할 행정구역을 선택하세요:", district_list)
    
    # 선택된 행정구의 데이터 추출
    district_data = df[df["행정구역"] == selected_district].iloc[0]
    y_values = [district_data[col] for col in age_cols]
    
    # 2. 그래프 그리기 (Matplotlib 스타일 적용)
    # 한글 폰트 깨짐 방지 설정 (Streamlit Cloud 환경용)
    plt.rcParams['font.family'] = 'NanumGothic' or 'sans-serif'
    plt.rcParams['axes.unicode_minus'] = False
    
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # 바탕색을 연한 회색으로 설정 (#F0F2F6는 스트림릿 기본 배경과 잘 어울리는 연회색입니다)
    ax.set_facecolor("#F0F2F6") 
    fig.patch.set_facecolor("#F0F2F6")
    
    # 꺾은선 그래프 그리기 (라일락 색상: #C8A2C8)
    ax.plot(age_cols, y_values, marker='o', linestyle='-', color='#C8A2C8', linewidth=2.5, markersize=6)
    
    # 그래프 상세 설정
    ax.set_title(f"[{selected_district}] 연령대별 인구수 추이", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("연령대 (나이)", fontsize=11, labelpad=10)
    ax.set_ylabel("인구수 (명)", fontsize=11, labelpad=10)
    ax.grid(True, linestyle='--', alpha=0.5, color='white') # 연회색 바탕 위에 하얀 점선 그리드
    
    # 천 단위 콤마 포맷팅 적용
    ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
    
    # 스트림릿에 그래프 출력
    st.pyplot(fig)
    
    # 3. 데이터 테이블 요약 보기 (선택사항)
    with st.expander("상세 데이터 보기"):
        summary_df = pd.DataFrame({"연령대": age_cols, "인구수(명)": y_values})
        st.dataframe(summary_df.style.format({"인구수(명)": "{:,}"}), use_container_width=True)

except Exception as e:
    st.error(f"데이터를 불러오거나 처리하는 중 오류가 발생했습니다: {e}")
    st.info("`population.csv` 파일이 `app.py`와 같은 폴더에 있는지 확인해 주세요.")
    # ------------------------------------------------------------------
# 4. 추가 기능: 연령대별 인구수가 가장 많은 행정구역 분석 (기존 코드 밑에 추가)
# ------------------------------------------------------------------
st.divider()  # 화면 구분을 위한 선
st.header("✨ 추가 기능: 연령대별 인구 우수 자치구 분석")
st.markdown("특정 연령대를 선택하면, 해당 연령대의 인구수가 가장 많은 자치구 순으로 그래프를 보여줍니다.")

# 연령대 선택 셀렉트박스
selected_age = st.selectbox("분석할 연령대를 선택하세요:", age_cols)

if selected_age:
    # '서울특별시 (1100000000)' 등 전체 합계 행은 제외하고 자치구만 추출
    # 보통 구별 데이터는 구 이름이 포함되어 있으므로 조건 필터링
    df_districts = df[df["행정구역"].str.contains("구 \(")]
    
    # 선택한 연령대 인구수 기준으로 내림차순 정렬 (상위 10개 구 추출)
    top_districts = df_districts.sort_values(by=selected_age, ascending=False).head(10)
    
    # 그래프에 깔끔하게 표시하기 위해 '서울특별시 강서구 (1150000000)' -> '강서구' 형태로 가공
    x_labels = top_districts["행정구역"].str.split().str[1]
    y_values_age = top_districts[selected_age].values

    # 그래프 그리기
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    
    # 디자인 조건 반영: 바탕은 연한 회색(#F0F2F6), 꺾은선은 라일락 색상(#C8A2C8)
    ax2.set_facecolor("#F0F2F6")
    fig2.patch.set_facecolor("#F0F2F6")
    
    # 꺾은선 그래프 그리기
    ax2.plot(x_labels, y_values_age, marker='s', linestyle='-', color='#C8A2C8', linewidth=2.5, markersize=7)
    
    # 그래프 상세 설정
    ax2.set_title(f"[{selected_age}] 인구수 상위 10개 자치구", fontsize=14, fontweight='bold', pad=15)
    ax2.set_xlabel("행정구역 (자치구)", fontsize=11, labelpad=10)
    ax2.set_ylabel("인구수 (명)", fontsize=11, labelpad=10)
    ax2.grid(True, linestyle='--', alpha=0.5, color='white')
    
    # 천 단위 쉼표 포맷팅
    ax2.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
    
    # 스트림릿 앱에 출력
    st.pyplot(fig2)
    
    # 순위 데이터 테이블 표시
    with st.expander(f"{selected_age} 인구 순위 Top 10 상세 보기"):
        rank_df = pd.DataFrame({
            "순위": range(1, 11),
            "자치구": x_labels,
            "인구수(명)": y_values_age
        }).set_index("순위")
        st.dataframe(rank_df.style.format({"인구수(명)": "{:,}"}), use_container_width=True)
