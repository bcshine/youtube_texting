import streamlit as st
import re
from youtube_text_extractor import YouTubeTextExtractor

# 페이지 설정
st.set_page_config(
    page_title="유튜브 텍스트 추출기",
    page_icon="📺",
    layout="centered"
)

# 모바일 반응형 CSS
st.markdown("""
<style>
    @media only screen and (max-width: 768px) {
        .main .block-container {
            padding-top: 1rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        .stButton > button {
            width: 100% !important;
            padding: 0.75rem !important;
            font-size: 1rem !important;
        }
        .stTextInput > div > div > input {
            font-size: 16px !important;
        }
        .stTextArea textarea {
            font-size: 14px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# 제목
st.title("📺 유튜브 텍스트 추출기")
st.markdown("유튜브 비디오의 자막을 추출하여 텍스트로 변환하는 도구입니다.")

# URL 입력
st.markdown("### 🔗 유튜브 URL 입력")
youtube_url = st.text_input(
    "URL",
    placeholder="https://www.youtube.com/watch?v=example",
    help="유튜브 비디오 URL을 입력하세요"
)

# 옵션
use_speech_recognition = st.checkbox(
    "🎤 음성 인식 사용 (자막이 없을 때)", 
    value=True,
    help="자막이 없는 경우 음성을 텍스트로 변환합니다"
)

# 추출 버튼
if st.button("📥 텍스트 추출하기", type="primary"):
    if youtube_url:
        # URL 유효성 검사
        url_pattern = r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/live\/)([^&\n?#]+)'
        if re.search(url_pattern, youtube_url):
            
            # 진행 상태 표시
            with st.spinner("텍스트를 추출하고 있습니다..."):
                try:
                    # 추출기 생성 및 실행
                    extractor = YouTubeTextExtractor()
                    extractor.use_speech_recognition = use_speech_recognition
                    
                    result_file = extractor.process_youtube_url(youtube_url)
                    
                    if result_file and extractor.formatted_text:
                        st.success("✅ 텍스트 추출 완료!")
                        
                        # 비디오 정보
                        if extractor.video_info:
                            st.info(f"🎬 **{extractor.video_info.get('title', '제목 없음')}**")
                        
                        # 추출된 텍스트 표시
                        st.markdown("### 📄 추출된 텍스트")
                        st.text_area(
                            "텍스트를 선택하고 Ctrl+C로 복사하세요:",
                            extractor.formatted_text,
                            height=400,
                            label_visibility="collapsed"
                        )
                        
                        # 통계 정보
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("자막 개수", f"{len(extractor.transcript_data)}개")
                        with col2:
                            st.metric("텍스트 길이", f"{len(extractor.formatted_text):,}자")
                        with col3:
                            word_count = len(extractor.formatted_text.split())
                            st.metric("단어 수", f"{word_count:,}개")
                        
                        st.markdown("---")
                        st.markdown("💡 **복사 방법:** 텍스트 영역을 클릭하고 `Ctrl+A`로 전체 선택 후 `Ctrl+C`로 복사하세요.")
                    
                    else:
                        st.error("❌ 텍스트 추출에 실패했습니다. 비디오가 비공개이거나 자막/음성을 추출할 수 없습니다.")
                        
                except Exception as e:
                    st.error(f"❌ 오류가 발생했습니다: {str(e)}")
        else:
            st.error("❌ 올바른 유튜브 URL을 입력해주세요.")
    else:
        st.warning("⚠️ 유튜브 URL을 입력해주세요.")

# 사용 안내
st.markdown("---")
st.markdown("### 💡 사용 방법")
st.markdown("""
1. **유튜브 URL 입력**: 추출하고 싶은 유튜브 비디오 URL을 붙여넣기하세요
2. **옵션 선택**: 자막이 없는 경우 음성 인식을 사용할지 선택하세요
3. **추출 실행**: "텍스트 추출하기" 버튼을 클릭하세요
4. **결과 복사**: 추출된 텍스트를 선택하고 복사하세요
""")

st.markdown("### 📌 지원 형식")
st.markdown("""
- `youtube.com/watch?v=VIDEO_ID`
- `youtu.be/VIDEO_ID`  
- `youtube.com/embed/VIDEO_ID`
- `youtube.com/live/VIDEO_ID`
""")

# 푸터
st.markdown("---")
st.markdown("Made with ❤️ by YouTube Text Extractor") 