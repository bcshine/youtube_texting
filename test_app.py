import streamlit as st

st.title("🎉 Streamlit 테스트")
st.write("안녕하세요! Streamlit이 정상적으로 작동하고 있습니다.")

name = st.text_input("이름을 입력하세요:")
if name:
    st.write(f"안녕하세요, {name}님!")

if st.button("클릭해보세요!"):
    st.balloons()
    st.success("성공적으로 작동합니다! 🎊") 