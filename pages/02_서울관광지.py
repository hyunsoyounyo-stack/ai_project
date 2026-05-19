import streamlit as st
import folium
from streamlit_folium import st_folium

# 스트림릿 페이지 설정
st.set_page_config(page_title="Seoul Top 10 Attractions", layout="wide")

st.title("외국인이 좋아하는 서울 주요 관광지 TOP 10 🗺️")
st.markdown("마우스 커서를 **연한 보라색 마커** 위에 올리면 가장 가까운 지하철역을 확인할 수 있습니다.")

# 관광지 데이터 (이름, 위도, 경도, 가까운 지하철역, 놀거리)
seoul_attractions = [
    {
        "name": "경복궁 (Gyeongbokgung Palace)",
        "lat": 37.5796, "lon": 126.9770,
        "subway": "경복궁역 (3호선)",
        "activity": "한복 대여 후 고궁 산책, 수문장 교대식 관람, 사진 촬영"
    },
    {
        "name": "명동 쇼핑거리 (Myeongdong)",
        "lat": 37.5635, "lon": 126.9846,
        "subway": "명동역 (4호선)",
        "activity": "길거리 음식 탐방, 화장품 및 패션 쇼핑, K-뷰티 체험"
    },
    {
        "name": "N서울타워 (N Seoul Tower)",
        "lat": 37.5512, "lon": 126.9882,
        "subway": "명동역/충무로역 (케이블카 또는 버스 연계)",
        "activity": "서울 시내 파노라마 야경 감상, 사랑의 자물쇠 걸기"
    },
    {
        "name": "북촌한옥마을 (Bukchon Hanok Village)",
        "lat": 37.5829, "lon": 126.9835,
        "subway": "안국역 (3호선)",
        "activity": "전통 한옥 골목길 출사, 전통 차 문화 체험, 공방 투어"
    },
    {
        "name": "홍대 걷고싶은거리 (Hongdae)",
        "lat": 37.5575, "lon": 126.9244,
        "subway": "홍대입구역 (2호선, 공항철도)",
        "activity": "저녁 버스킹 관람, 이색 카페 투어, 인디 문화 및 클럽 경험"
    },
    {
        "name": "동대문디자인플라자 (DDP)",
        "lat": 37.5668, "lon": 127.0094,
        "subway": "동대문역사문화공원역 (2, 4, 5호선)",
        "activity": "독특한 건축물 야경 촬영, 디자인 전시회 관람, 밤도깨비 야시장"
    },
    {
        "name": "인사동 문화거리 (Insadong)",
        "lat": 37.5744, "lon": 126.9856,
        "subway": "안국역 (3호선) / 종로3가역 (1, 3, 5호선)",
        "activity": "한국 전통 기념품 쇼핑, 쌈지길 구경, 전통 찻집 방문"
    },
    {
        "name": "롯데월드 타워 & 몰 (Lotte World Tower)",
        "lat": 37.5126, "lon": 127.1025,
        "subway": "잠실역 (2, 8호선)",
        "activity": "서울스카이 전망대에서 아찔한 뷰 감상, 쇼핑, 석촌호수 산책"
    },
    {
        "name": "이태원 관광특구 (Itaewon)",
        "lat": 37.5345, "lon": 126.9942,
        "subway": "이태원역 (6호선)",
        "activity": "세계 각국 유니크한 다국적 요리 맛보기, 트렌디한 라운지 바 투어"
    },
    {
        "name": "여의도 한강공원 (Yeouido Hangang Park)",
        "lat": 37.5284, "lon": 126.9331,
        "subway": "여의나루역 (5호선)",
        "activity": "한강 라면 먹기, 배달 음식 주문, 따릉이 자전거 대여 및 피크닉"
    }
]

# 지도 레이아웃과 상세 설명 레이아웃 분리
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("서울 관광지도")
    # 서울 중심부 좌표로 지도 초기화
    m = folium.Map(location=[37.5580, 126.9784], zoom_start=12)

    # 마커 추가 루프
    for place in seoul_attractions:
        # 연한 보라색(Light Purple) 마커 생성
        folium.Marker(
            location=[place["lat"], place["lon"]],
            # 클릭했을 때 나오는 팝업 (관광지 이름)
            popup=folium.Popup(f"<b>{place['name']}</b>", max_width=300),
            # 마우스를 올렸을 때 나오는 툴팁 (가까운 지하철역)
            tooltip=f"📍 가까운 역: {place['subway']}",
            icon=folium.Icon(color="purple", icon="info-sign")
        ).add_to(m)

    # 스트림릿에 지도 렌더링
    st_folium(m, width="100%", height=500)

with col2:
    st.subheader("💡 이용 팁")
    st.info(
        "1. 지도 위의 마커에 **마우스를 올리면(Hover)** 가장 가까운 지하철역 정보가 나타납니다.\n"
        "2. 마커를 **클릭(Click)**하면 관광지의 영문/국문 이름이 표시됩니다."
    )

st.write("---")

# 지도 하단 관광지 상세 설명 정보 출력 (표 형태로 가독성 업그레이드)
st.subheader("📋 관광지 10곳 상세 안내 (지하철역 & 놀거리)")

# 가독성을 위해 리스트 데이터를 테이블용 데이터로 변환
table_data = []
for idx, place in enumerate(seoul_attractions, 1):
    table_data.append({
        "순번": idx,
        "관광지 이름": place["name"],
        "가까운 지하철역": place["subway"],
        "주요 놀거리 및 추천 활동": place["activity"]
    })

st.table(table_data)
