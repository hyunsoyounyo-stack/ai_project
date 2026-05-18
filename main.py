import streamlit as st
st.title('나의 첫 웹 서비스 만들기')
a=st.text_input('이름을 입력해주세요')
b=st.selectbox('좋아하는 음식을 선택하세요',['케이크','쿠키','마늘빵'])
if st.button('인삿말 생성'):
  st.write(a+'님, 안녕하세요')
