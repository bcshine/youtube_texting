import streamlit as st
import re
from youtube_text_extractor import YouTubeTextExtractor

# 페이지 설정
st.set_page_config(
    page_title="유튜브 텍스트 추출기",
    page_icon="📺",
    layout="centered"
)

# 전체 디자인 CSS
st.markdown("""
<style>
    /* 기본 스타일 리셋 */
    .main .block-container {
        max-width: 800px !important;
        padding-top: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    
    /* Streamlit 기본 요소 숨기기 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* 전체 배경 */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* 메인 컨테이너 카드 스타일 */
    .main .block-container {
        background: white;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        margin: 2rem auto;
        text-align: center;
    }
    
    /* 제목 스타일 */
    h1 {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: bold !important;
        margin-bottom: 1rem !important;
        text-align: center;
    }
    
    /* 부제목 스타일 */
    .subtitle {
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    /* 섹션 제목 */
    h3 {
        color: #333;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
        font-weight: 600;
    }
    
    /* 입력 필드 스타일 */
    .stTextInput > div > div > input {
        border-radius: 10px !important;
        border: 2px solid #e1e5e9 !important;
        padding: 12px 16px !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #4ECDC4 !important;
        box-shadow: 0 0 0 3px rgba(78, 205, 196, 0.1) !important;
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4) !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 15px 30px !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        margin: 10px 0 !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.2) !important;
    }
    
    /* 체크박스 스타일 */
    .stCheckbox {
        margin: 1rem 0 !important;
        padding: 10px !important;
        background: #f8f9fa;
        border-radius: 10px;
    }
    
    /* 텍스트 영역 스타일 */
    .stTextArea textarea {
        border-radius: 10px !important;
        border: 2px solid #e1e5e9 !important;
        font-family: 'Courier New', monospace !important;
        line-height: 1.6 !important;
    }
    
    /* 성공 메시지 스타일 */
    .stSuccess {
        background: linear-gradient(45deg, #4ECDC4, #44A08D) !important;
        color: white !important;
        border-radius: 10px !important;
        text-align: center !important;
    }
    
    /* 정보 메시지 스타일 */
    .stInfo {
        background: linear-gradient(45deg, #667eea, #764ba2) !important;
        color: white !important;
        border-radius: 10px !important;
        text-align: center !important;
    }
    
    /* 메트릭 카드 스타일 */
    [data-testid="metric-container"] {
        background: linear-gradient(45deg, #f093fb, #f5576c);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    [data-testid="metric-container"] > div {
        color: white !important;
    }
    
    /* 에러 메시지 스타일 */
    .stAlert > div {
        border-radius: 10px !important;
        border: none !important;
    }
    
    /* 경고 메시지 스타일 */
    .stWarning > div {
        background: linear-gradient(45deg, #ffeaa7, #fab1a0) !important;
        color: #2d3436 !important;
        border-radius: 10px !important;
    }
    
    /* 에러 메시지 스타일 */
    .stError > div {
        background: linear-gradient(45deg, #fd79a8, #e84393) !important;
        color: white !important;
        border-radius: 10px !important;
    }
    
    /* 코드 스타일 */
    code {
        background: rgba(255,255,255,0.8) !important;
        color: #333 !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
        font-weight: 500 !important;
    }
    
    /* 모바일 반응형 */
    @media only screen and (max-width: 768px) {
        .main .block-container {
            margin: 1rem auto !important;
            padding: 1.5rem !important;
            border-radius: 15px !important;
        }
        
        h1 {
            font-size: 2rem !important;
        }
        
        .stButton > button {
            padding: 12px 20px !important;
            font-size: 14px !important;
        }
        
        .stTextInput > div > div > input {
            font-size: 16px !important;
            padding: 10px 14px !important;
        }
    }
    
    @media only screen and (max-width: 480px) {
        .main .block-container {
            margin: 0.5rem !important;
            padding: 1rem !important;
        }
        
        h1 {
            font-size: 1.8rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# 제목과 설명
st.title("📺 YouTube Text Extractor")
st.markdown('<div class="subtitle">🎬 유튜브 영상의 자막과 음성을 텍스트로 쉽게 변환하세요</div>', unsafe_allow_html=True)
# URL 입력 섹션
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
<div style="background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); padding: 20px; border-radius: 15px; margin: 10px 0;">
<b>📝 쉬운 4단계 사용법</b><br><br>
<b>1️⃣ URL 입력</b>: 추출하고 싶은 유튜브 비디오 URL을 붙여넣기하세요<br>
<b>2️⃣ 옵션 선택</b>: 자막이 없는 경우 음성 인식을 사용할지 선택하세요<br>
<b>3️⃣ 추출 실행</b>: "텍스트 추출하기" 버튼을 클릭하세요<br>
<b>4️⃣ 결과 복사</b>: 추출된 텍스트를 선택하고 복사하세요
</div>
""", unsafe_allow_html=True)

st.markdown("### 📌 지원 형식")
st.markdown("""
<div style="background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%); padding: 15px; border-radius: 15px; margin: 10px 0; font-family: monospace;">
✅ <code>youtube.com/watch?v=VIDEO_ID</code><br>
✅ <code>youtu.be/VIDEO_ID</code><br>
✅ <code>youtube.com/embed/VIDEO_ID</code><br>
✅ <code>youtube.com/live/VIDEO_ID</code>
</div>
""", unsafe_allow_html=True)

# 푸터
st.markdown("""
<div style="text-align: center; padding: 30px 0; margin-top: 40px; border-top: 2px solid #e1e5e9;">
<div style="background: linear-gradient(45deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-weight: bold; font-size: 18px;">
✨ Made with ❤️ by YouTube Text Extractor ✨
</div>
<div style="color: #888; margin-top: 10px; font-size: 14px;">
🚀 빠르고 정확한 유튜브 텍스트 추출 서비스
</div>
</div>
""", unsafe_allow_html=True) 