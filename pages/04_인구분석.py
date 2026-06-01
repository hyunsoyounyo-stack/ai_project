import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import urllib.request

# 페이지 설정
st.set_page_config(page_title="서울시 자치구별 인구 구조 분석", layout="centered")

# ------------------------------------------------------------------
# [해결책 1] Matplotlib 그래프 내부 한글 깨짐 방지 (폰트 자동 다운로드)
# ------------------------------------------------------------------
@st.cache_resource
def init_korean_font():
    font_path = "NanumGothic.ttf"
    
    # 폰트 파일이 없으면 구글 폰트 저장소에서 다운로드
    if not os.path.exists(font_path):
        url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
        urllib.request.urlretrieve(url, font_path)
    
    # Matplotlib에 폰트 등록 및 기본 폰트 설정
    font_entry = fm.FontEntry(fname=font_path, name='NanumGothic')
    fm.fontManager.ttflist.insert(0, font_entry)
    plt.rcParams['font.family'] = 'NanumGothic'
    plt.rcParams['axes.unicode_minus'] = False

# 폰트 초기화 실행
init_korean_font()

# ------------------------------------------------------------------
# [해결책 2] 스트림릿 텍스트 한글 깨짐 방지 데이터 로드 (인코딩 완벽 대응)
# ------------------------------------------------------------------
@st.cache_data
def load_data():
    # 여러 인코딩 방식을 순서대로 시도하여 글자 깨짐 방지
    encodings = ["utf-8-sig", "cp949", "euc-kr"]
    df = None
    
    for enc in encodings:
        try:
            df = pd.read_csv("population.csv", encoding=enc)
            # 첫 번째 컬럼 이름에 '행정구역'이 제대로 포함되어 있는지 확인하여 올바른 인코딩 검증
            if "행정구역" in df.columns or df.columns[0].contains("행정"):
                break
        except Exception:
            continue
            
    if df is None:
        # 모든 시도가 실패했을 때의 예외 처리
        raise ValueError("CSV 파일의 인코딩을 인식할 수 없습니다. 파일 형식을 확인해주세요.")
    
    # 연령대 컬럼 정의
    age_columns = [
        "0~9세", "10~19세", "20~29세", "30~39세", "40~49세", 
        "50~59세", "60~69세", "70~79세", "80~89세", "90~99세", "100세 이상"
    ]
    
    # 문자열로 되어 있는 숫자 데이터(콤마 포함)를 정수형으로 변환
    for col in age_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(",", "").astype(int)
            
    return df, age_columns

# 메인 앱 실행
try:
    df, age_cols = load_data()
    
    # 헤더 영역
    st.title("📊 서울시 자치구별 인구 구조 분석")
    st.markdown("행정구를 선택하면 연령대별 인구수 추이를 꺾은선 그래프로 확인할 수 있습니다.")
    st.text("Data 기준: 2026년 4월")
    
    # ------------------------------------------------------------------
    # 기본 기능: 행정구 선택 및 연령대별 인구수 꺾은선 그래프
    # ------------------------------------------------------------------
    st.subheader("📍 자치구별 인구 구조")
    district_list = df["행정구역"].unique()
    selected_district = st.selectbox("분석할 행정구역을 선택하세요:", district_list)
    
    # 선택된 행정구의 데이터 추출
    district_data = df[df["행정구역"] == selected_district].iloc[0]
    y_values = [district_data[col] for col in age_cols]
    
    # 그래프 그리기
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_facecolor("#F0F2F6")   # 바탕색: 연한 회색
    fig.patch.set_facecolor("#F0F2F6")
    
    # 꺾은선 그리기 (라일락 색상: #C8A2C8)
    ax.plot(age_cols, y_values, marker='o', linestyle='-', color='#C8A2C8', linewidth=2.5, markersize=6)
    
    # 그래프 스타일 설정
    ax.set_title(f"[{selected_district}] 연령대별 인구수 추이", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("연령대 (나이)", fontsize=11, labelpad=10)
    ax.set_ylabel("인구수 (명)", fontsize=11, labelpad=10)
    ax.grid(True, linestyle='--', alpha=0.5, color='white')
    ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
    
    st.pyplot(fig)
    
    # 표로 보기
    with st.expander("구별 상세 데이터 보기"):
        summary_df = pd.DataFrame({"연령대": age_cols, "인구수(명)": y_values})
        st.dataframe(summary_df.style.format({"인구수(명)": "{:,}"}), use_container_width=True)

    # ------------------------------------------------------------------
    # 추가 기능: 연령대 선택 시 인구수가 가장 많은 행정구역 Top 10 그래프
    # ------------------------------------------------------------------
    st.divider()  # 구분선
    st.header("✨ 추가 기능: 연령대별 인구 우수 자치구 분석")
    st.markdown("특정 연령대를 선택하면, 해당 연령대의 인구수가 가장 많은 자치구 순으로 그래프를 보여줍니다.")
    
    selected_age = st.selectbox("분석할 연령대를 선택하세요:", age_cols, key="age_select_feature")
    
    if selected_age:
        # '서울특별시' 전체 합계 행을 제외하고 구별 데이터만 필터링
        df_districts = df[df["행정구역"].str.contains("구 \(")]
        
        # 선택한 연령대 기준 내림차순 정렬 후 상위 10개 구 추출
        top_districts = df_districts.sort_values(by=selected_age, ascending=False).head(10)
        
        # 그래프 X축 라벨 가공 ('서울특별시 강서구 (115...)' -> '강서구')
        x_labels = top_districts["행정구역"].str.split().str[1]
        y_values_age = top_districts[selected_age].values
    
        # 그래프 그리기
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        ax2.set_facecolor("#F0F2F6")   # 바탕색: 연한 회색
        fig2.patch.set_facecolor("#F0F2F6")
        
        # 꺾은선 그리기 (라일락 색상: #C8A2C8, 사각형 마커)
        ax2.plot(x_labels, y_values_age, marker='s', linestyle='-', color='#C8A2C8', linewidth=2.5, markersize=7)
        
        # 그래프 스타일 설정
        ax2.set_title(f"[{selected_age}] 인구수 상위 10개 자치구", fontsize=14, fontweight='bold', pad=15)
        ax2.set_xlabel("행정구역 (자치구)", fontsize=11, labelpad=10)
        ax2.set_ylabel("인구수 (명)", fontsize=11, labelpad=10)
        ax2.grid(True, linestyle='--', alpha=0.5, color='white')
        ax2.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
        
        st.pyplot(fig2)
        
        # 순위 표로 보기
        with st.expander(f"{selected_age} 인구 순위 Top 10 상세 보기"):
            rank_df = pd.DataFrame({
                "순위": range(1, 11),
                "자치구": x_labels,
                "인구수(명)": y_values_age
            }).set_index("순위")
            st.dataframe(rank_df.style.format({"인구수(명)": "{:,}"}), use_container_width=True)

except Exception as e:
    st.error(f"데이터를 불러오거나 처리하는 중 오류가 발생했습니다: {e}")
    st.info("`population.csv` 파일이 `app.py`와 동일한 깃허브 폴더에 업로드되어 있는지 확인해 주세요.")
