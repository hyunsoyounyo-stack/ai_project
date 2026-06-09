import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="서울시 연령별 미디어 사용량 분석", layout="wide")
st.title("📊 2013년 서울시 연령별 스마트폰/미디어 사용량 분석")
st.markdown("업로드된 `aa.csv` 데이터를 바탕으로 연령대별 사용 빈도와 나의 정확한 상위 위치(%)를 분석합니다.")

# 2. 데이터 로드 함수 (인코딩 처리 및 캐싱)
@st.cache_data
def load_data():
    df = pd.read_csv("aa.csv", skiprows=2, header=None, encoding='cp949')
    df.columns = ["구분별(1)", "구분별(2)", "1일평균사용시간", "1시간이하", "1-3시간", "3-5시간", "5시간초과"]
    
    # 공백 제거
    df["구분별(1)"] = df["구분별(1)"].str.strip()
    df["구분별(2)"] = df["구분별(2)"].str.strip()
    
    # '연령별' 데이터만 필터링
    age_df = df[df["구분별(1)"] == "연령별"].copy()
    
    # 수치형 데이터 변환
    numeric_cols = ["1일평균사용시간", "1시간이하", "1-3시간", "3-5시간", "5시간초과"]
    for col in numeric_cols:
        age_df[col] = pd.to_numeric(age_df[col], errors='coerce')
        
    return age_df

try:
    df_age = load_data()

    # 화면을 두 개의 구역(Column)으로 분할
    col1, col2 = st.columns([1.8, 1.2])

    with col1:
        st.subheader("🎵 연령대별 사용 빈도 (구간별 비율)")
        
        # 💡 스트림릿 클라우드 한글 깨짐 방지를 위해 Plotly 기반 막대그래프 구현
        categories = ["1시간이하", "1-3시간", "3-5시간", "5시간초과"]
        
        # 라일락 계열 색상 지정
        colors = ["#DCD0FF", "#C8A2C8", "#B19CD9", "#9370DB"]
        
        fig = go.Figure()
        for cat, color in zip(categories, colors):
            fig.add_trace(go.Bar(
                name=cat,
                x=df_age["구분별(2)"],
                y=df_age[cat],
                marker_color=color
            ))
            
        fig.update_layout(
            title="연령대별 사용 시간대 분포 (%)",
            xaxis_title="연령대",
            yaxis_title="비율 (%)",
            barmode='group',
            legend_title="이용 시간 구간",
            template="plotly_white",
            margin=dict(l=40, r=40, t=60, b=40)
        )
        
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🔍 연령대별 평균 및 나의 위치 측정")
        
        # 1. 나잇대 선택
        age_list = df_age["구분별(2)"].tolist()
        selected_age = st.selectbox("본인의 나잇대를 선택하세요:", age_list)
        
        # 선택된 나이의 데이터 추출
        selected_data = df_age[df_age["구분별(2)"] == selected_age].iloc[0]
        avg_time = selected_data["1일평균사용시간"]
        
        # 평균 사용 시간 표시
        st.info(f"### 🕒 {selected_age} 평균 사용 시간: **{avg_time} 시간**")
        
        st.write("---")
        
        # 2. 본인 사용 시간 입력 및 정밀 % 계산
        st.markdown("#### 💡 나의 정확한 상위 퍼센트(%) 계산")
        my_time = st.number_input(
            "하루 평균 스마트폰 사용 시간(시간 단위)을 입력하세요:", 
            min_value=0.0, max_value=24.0, value=2.0, step=0.1
        )
        
        p_under_1 = selected_data["1시간이하"]
        p_1_to_3 = selected_data["1-3시간"]
        p_3_to_5 = selected_data["3-5시간"]
        p_over_5 = selected_data["5시간초과"]
        
        # 💡 선형 보간법을 적용한 정밀 상위 % 계산 로직
        if my_time > 5.0:
            # 5시간을 초과하는 경우, 최대 10시간을 기준으로 비례 계산 (임의 기준선 제공)
            clamped_time = min(my_time, 10.0)
            ratio = (clamped_time - 5.0) / 5.0
            estimated_top = p_over_5 * (1.0 - ratio)
            # 최소값은 상위 0.1%로 제한
            estimated_top = max(estimated_top, 0.1)
            
        elif 3.0 <= my_time <= 5.0:
            # 3~5시간 구간 사이의 위치 계산
            ratio = (my_time - 3.0) / (5.0 - 3.0)
            estimated_top = p_over_5 + (p_3_to_5 * (1.0 - ratio))
            
        elif 1.0 <= my_time < 3.0:
            # 1~3시간 구간 사이의 위치 계산
            ratio = (my_time - 1.0) / (3.0 - 1.0)
            estimated_top = p_over_5 + p_3_to_5 + (p_1_to_3 * (1.0 - ratio))
            
        else:
            # 0~1시간 구간 사이의 위치 계산
            ratio = my_time / 1.0
            estimated_top = p_over_5 + p_3_to_5 + p_1_to_3 + (p_under_1 * (1.0 - ratio))
            # 최대값은 100%로 제한
            estimated_top = min(estimated_top, 100.0)

        # 결과 출력 구조화
        st.markdown(f"**[정밀 분석 결과]**")
        
        if estimated_top <= 10.0:
            st.error(f"선택하신 **{selected_age} 중 상위 약 {estimated_top:.1f}%**에 해당합니다! 대단한 헤비유저이시네요. 🚀")
        elif 10.0 < estimated_top <= 40.0:
            st.warning(f"선택하신 **{selected_age} 중 상위 약 {estimated_top:.1f}%**에 해당합니다. 평균보다 다소 많이 사용하는 편입니다. 👍")
        elif 40.0 < estimated_top <= 80.0:
            st.success(f"선택하신 **{selected_age} 중 상위 약 {estimated_top:.1f}%**에 해당합니다. 평균 범주에 속하는 안정적인 이용 상태입니다. ☕")
        else:
            st.success(f"선택하신 **{selected_age} 중 상위 약 {estimated_top:.1f}%**에 해당합니다. 미디어 기기를 거의 사용하지 않는 청정 구역에 계십니다! 🌳")

        # 세부 지표 확인
        with st.expander(f"📊 {selected_age} 분포 요약 데이터"):
            st.write(f"- 5시간 초과: {p_over_5}%")
            st.write(f"- 3~5시간: {p_3_to_5}%")
            st.write(f"- 1~3시간: {p_1_to_3}%")
            st.write(f"- 1시간 이하: {p_under_1}%")

except FileNotFoundError:
    st.error("📂 `aa.csv` 파일을 찾을 수 없습니다. GitHub 저장소에 코드가 있는 위치와 같은 곳에 데이터를 업로드해 주세요.")
except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")
