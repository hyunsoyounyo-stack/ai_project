import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="서울시 미디어 이용태도 분석 대시보드", layout="wide")
st.title("📊 서울시민 스마트폰/미디어 사용량 분석 대시보드")
st.markdown("업로드된 `aa.csv` 데이터를 바탕으로 다양한 인구통계학적 특성별 이용 패턴을 분석하고 나의 위치를 확인합니다.")

# 2. 데이터 로드 함수 (인코딩 처리 및 캐싱)
@st.cache_data
def load_data():
    df = pd.read_csv("aa.csv", skiprows=2, header=None, encoding='cp949')
    df.columns = ["구분별(1)", "구분별(2)", "1일평균사용시간", "1시간이하", "1-3시간", "3-5시간", "5시간초과"]
    
    # 공백 제거
    df["구분별(1)"] = df["구분별(1)"].str.strip()
    df["구분별(2)"] = df["구분별(2)"].str.strip()
    
    # 수치형 데이터 변환
    numeric_cols = ["1일평균사용시간", "1시간이하", "1-3시간", "3-5시간", "5시간초과"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    return df

try:
    df_all = load_data()

    # 💡 [추가 기능 3] 분석 기준 필터 확장 (상단 사이드바 혹은 메인에 배치)
    st.sidebar.header("⚙️ 대시보드 설정")
    analysis_target = st.sidebar.radio(
        "분석 기준을 선택하세요:",
        ["연령별", "성별", "학력별", "소득별", "혼인상태별"]
    )
    
    # 선택된 기준에 맞게 데이터 필터링
    df_filtered = df_all[df_all["구분별(1)"] == analysis_target].copy()

    # 화면 분할
    col1, col2 = st.columns([1.8, 1.2])

    with col1:
        st.subheader(f"🎵 {analysis_target} 사용 빈도 (구간별 비율)")
        
        # Plotly 기반 막대그래프
        categories = ["1시간이하", "1-3시간", "3-5시간", "5시간초과"]
        colors = ["#DCD0FF", "#C8A2C8", "#B19CD9", "#9370DB"] # 라일락 테마
        
        fig = go.Figure()
        for cat, color in zip(categories, colors):
            fig.add_trace(go.Bar(
                name=cat,
                x=df_filtered["구분별(2)"],
                y=df_filtered[cat],
                marker_color=color
            ))
            
        fig.update_layout(
            title=f"{analysis_target} 사용 시간대 분포 (%)",
            xaxis_title=analysis_target,
            yaxis_title="비율 (%)",
            barmode='group',
            legend_title="이용 시간 구간",
            template="plotly_white",
            margin=dict(l=40, r=40, t=60, b=40)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 💡 [추가 기능 1] 집단 간 비교(Compare) 기능 추가
        st.write("---")
        st.markdown(f"#### 🔄 {analysis_target} 집단 간 평균 사용시간 비교")
        compare_groups = st.multiselect(
            "비교하고 싶은 집단들을 선택하세요 (여러 개 선택 가능):",
            df_filtered["구분별(2)"].tolist(),
            default=df_filtered["구분별(2)"].tolist()[:2] if len(df_filtered) >= 2 else df_filtered["구분별(2)"].tolist()
        )
        
        if compare_groups:
            df_compare = df_filtered[df_filtered["구분별(2)"].isin(compare_groups)]
            fig_compare = go.Figure([go.Bar(
                x=df_compare["구분별(2)"],
                y=df_compare["1일평균사용시간"],
                marker_color="#C8A2C8",
                text=df_compare["1일평균사용시간"].apply(lambda x: f"{x}시간"),
                textposition='auto'
            )])
            fig_compare.update_layout(
                title="선택한 집단별 1일 평균 사용시간",
                xaxis_title=analysis_target,
                yaxis_title="평균 사용시간 (시간)",
                template="plotly_white"
            )
            st.plotly_chart(fig_compare, use_container_width=True)

    with col2:
        st.subheader(f"🔍 나의 {analysis_target} 위치 측정")
        
        # 세부 집단 선택
        group_list = df_filtered["구분별(2)"].tolist()
        selected_group = st.selectbox(f"본인의 해당 항목을 선택하세요 ({analysis_target}):", group_list)
        
        selected_data = df_filtered[df_filtered["구분별(2)"] == selected_group].iloc[0]
        avg_time = selected_data["1일평균사용시간"]
        
        st.info(f"### 🕒 {selected_group} 평균 사용 시간: **{avg_time} 시간**")
        st.write("---")
        
        # 나의 사용시간 입력 및 정밀 % 계산
        st.markdown("#### 💡 나의 정확한 상위 퍼센트(%) 계산")
        my_time = st.number_input(
            "하루 평균 스마트폰 사용 시간(시간 단위)을 입력하세요:", 
            min_value=0.0, max_value=24.0, value=2.0, step=0.1
        )
        
        p_under_1 = selected_data["1시간이하"]
        p_1_to_3 = selected_data["1-3시간"]
        p_3_to_5 = selected_data["3-5시간"]
        p_over_5 = selected_data["5시간초과"]
        
        # 선형 보간법을 적용한 정밀 상위 % 계산 로직
        if my_time > 5.0:
            clamped_time = min(my_time, 10.0)
            ratio = (clamped_time - 5.0) / 5.0
            estimated_top = max(p_over_5 * (1.0 - ratio), 0.1)
        elif 3.0 <= my_time <= 5.0:
            ratio = (my_time - 3.0) / (5.0 - 3.0)
            estimated_top = p_over_5 + (p_3_to_5 * (1.0 - ratio))
        elif 1.0 <= my_time < 3.0:
            ratio = (my_time - 1.0) / (3.0 - 1.0)
            estimated_top = p_over_5 + p_3_to_5 + (p_1_to_3 * (1.0 - ratio))
        else:
            ratio = my_time / 1.0
            estimated_top = min(p_over_5 + p_3_to_5 + p_1_to_3 + (p_under_1 * (1.0 - ratio)), 100.0)

        st.markdown(f"**[정밀 분석 결과]**")
        if estimated_top <= 10.0:
            st.error(f"선택하신 **{selected_group} 중 상위 약 {estimated_top:.1f}%**에 해당합니다! 🚀")
        elif 10.0 < estimated_top <= 40.0:
            st.warning(f"선택하신 **{selected_group} 중 상위 약 {estimated_top:.1f}%**에 해당합니다. 👍")
        else:
            st.success(f"선택하신 **{selected_group} 중 상위 약 {estimated_top:.1f}%**에 해당합니다. ☕")

        # 💡 [추가 기능 2] 사용량 기반 맞춤형 건강 행동 가이드 제공
        st.write("---")
        st.markdown("#### 🌿 스마트 헬스 가이드")
        
        time_diff = my_time - avg_time
        if time_diff > 0:
            st.write(f"⚠️ 해당 집단 평균보다 하루에 **{abs(time_diff):.1f}시간 더** 사용하고 계십니다.")
        else:
            st.write(f"✨ 해당 집단 평균보다 하루에 **{abs(time_diff):.1f}시간 덜** 사용하여 잘 조절하고 계십니다.")
            
        if my_time >= 4.0:
            st.markdown("""
            * **추천 행동:** 1시간 사용 후 10분간 먼 곳을 바라보며 눈의 피로를 풀어주세요. 
            * **디톡스 팁:** 취침 1시간 전에는 스마트폰을 거실에 두고 침실에 들어가는 습관을 들여보세요!
            """)
        elif 2.0 <= my_time < 4.0:
            st.markdown("""
            * **추천 행동:** 움직임 없이 고정된 자세가 오래 유지될 수 있으니 가벼운 목/어깨 스트레칭을 해주세요.
            """)
        else:
            st.markdown("""
            * **추천 행동:** 아주 훌륭한 미디어 조절 능력을 가지고 계십니다. 오프라인 취미 활동을 계속 즐겨보세요!
            """)

except FileNotFoundError:
    st.error("📂 `aa.csv` 파일을 찾을 수 없습니다. GitHub 저장소에 코드가 있는 위치와 같은 곳에 데이터를 업로드해 주세요.")
except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")
