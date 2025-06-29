import streamlit as st
import re
from youtube_text_extractor import YouTubeTextExtractor

# 페이지 설정
st.set_page_config(
    page_title="유튜브 텍스트 추출기",
    page_icon="📺",
    layout="centered"
)

# 가독성 중심 디자인 CSS
st.markdown("""
<style>
    /* Streamlit 기본 요소 숨기기 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* 전체 배경 - 연한 그라데이션 */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* 메인 컨테이너 - 깔끔한 화이트 카드 */
    .main .block-container {
        max-width: 900px !important;
        background: #ffffff;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin: 2rem auto;
        padding: 3rem 2rem !important;
        text-align: center;
    }
    
    /* 제목 스타일 - 높은 대비 */
    h1 {
        color: #2c3e50 !important;
        font-weight: 700 !important;
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem !important;
        text-align: center;
        text-shadow: none !important;
    }
    
    /* 부제목 스타일 - 선명한 그레이 */
    .subtitle {
        color: #5a6c7d;
        font-size: 1.2rem;
        font-weight: 400;
        margin-bottom: 3rem;
        text-align: center;
        line-height: 1.5;
    }
    
    /* 섹션 제목 - 진한 색상 */
    h3 {
        color: #2c3e50 !important;
        font-weight: 600 !important;
        font-size: 1.4rem !important;
        margin: 2.5rem 0 1.5rem 0 !important;
        text-align: left;
    }
    
    /* 입력 필드 - 깔끔한 스타일 */
    .stTextInput > div > div > input {
        border: 2px solid #dde4ef !important;
        border-radius: 8px !important;
        padding: 14px 16px !important;
        font-size: 16px !important;
        color: #2c3e50 !important;
        background: #ffffff !important;
        transition: border-color 0.2s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #3498db !important;
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1) !important;
    }
    
    /* 버튼 - 선명한 블루 */
    .stButton > button {
        background: #3498db !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 16px 32px !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        width: 100% !important;
        margin: 15px 0 !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
    }
    
    .stButton > button:hover {
        background: #2980b9 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3) !important;
    }
    
    /* 체크박스 - 깔끔한 배경 */
    .stCheckbox {
        background: #f8fafb !important;
        border: 1px solid #e9ecef !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
        margin: 1rem 0 !important;
    }
    
    .stCheckbox label {
        color: #2c3e50 !important;
        font-weight: 500 !important;
    }
    
    /* 텍스트 영역 - 가독성 높은 스타일 */
    .stTextArea textarea {
        border: 2px solid #dde4ef !important;
        border-radius: 8px !important;
        font-family: 'SF Mono', 'Monaco', 'Cascadia Code', 'Roboto Mono', monospace !important;
        font-size: 14px !important;
        line-height: 1.6 !important;
        color: #2c3e50 !important;
        background: #ffffff !important;
        padding: 16px !important;
    }
    
    /* Alert 메시지 공통 스타일 */
    .stAlert > div {
        border-radius: 8px !important;
        border: none !important;
        font-weight: 500 !important;
        font-size: 15px !important;
    }
    
    /* 성공 메시지 - 진한 초록 */
    .stSuccess > div {
        background: #27ae60 !important;
        color: white !important;
    }
    
    /* 정보 메시지 - 진한 블루 */
    .stInfo > div {
        background: #3498db !important;
        color: white !important;
    }
    
    /* 경고 메시지 - 진한 주황 */
    .stWarning > div {
        background: #f39c12 !important;
        color: white !important;
    }
    
    /* 에러 메시지 - 진한 빨강 */
    .stError > div {
        background: #e74c3c !important;
        color: white !important;
    }
    
    /* 메트릭 카드 - 깔끔한 카드 스타일 */
    [data-testid="metric-container"] {
        background: #f8fafb;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
    }
    
    [data-testid="metric-container"] > div {
        color: #2c3e50 !important;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #3498db !important;
        font-weight: 700 !important;
    }
    
    /* 구분선 스타일 */
    hr {
        border: none !important;
        height: 1px !important;
        background: #e9ecef !important;
        margin: 2rem 0 !important;
    }
    
    /* 일반 텍스트 가독성 개선 */
    .stMarkdown, .stText {
        color: #2c3e50 !important;
        line-height: 1.6 !important;
    }
    
    /* 코드 블록 - 높은 대비 */
    code {
        background: #f8f9fa !important;
        color: #2c3e50 !important;
        padding: 4px 8px !important;
        border-radius: 4px !important;
        font-weight: 600 !important;
        border: 1px solid #e9ecef !important;
    }
    
    /* 모바일 반응형 */
    @media only screen and (max-width: 768px) {
        .main .block-container {
            margin: 1rem !important;
            padding: 2rem 1.5rem !important;
            border-radius: 12px !important;
        }
        
        h1 {
            font-size: 2rem !important;
        }
        
        .subtitle {
            font-size: 1rem !important;
        }
        
        h3 {
            font-size: 1.2rem !important;
        }
    }
    
    @media only screen and (max-width: 480px) {
        .main .block-container {
            margin: 0.5rem !important;
            padding: 1.5rem 1rem !important;
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
    placeholder="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    help="유튜브 비디오 URL을 입력하세요"
)

# 테스트 URL 안내
st.info("🧪 **처음 사용하시나요?** 위 입력창에 표시된 샘플 URL로 먼저 테스트해보세요!")

# 옵션 설정
st.markdown("### ⚙️ 추출 옵션")
use_speech_recognition = st.checkbox(
    "🎤 **음성 인식 모드** (자막이 없을 때 음성을 텍스트로 변환)", 
    value=True,
    help="체크하면: 자막이 없는 경우 영상의 음성을 분석해서 텍스트로 변환합니다 (처리 시간이 더 오래 걸림)"
)

st.info("💡 **체크박스 설명**: 대부분의 유튜브 영상은 자막이 있어서 빠르게 추출됩니다. 자막이 없는 영상의 경우에만 음성 인식을 사용합니다.")

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
                        st.error("❌ **텍스트 추출에 실패했습니다**")
                        st.markdown("""
                        **🔍 가능한 원인:**
                        - 🔒 비디오가 비공개 또는 삭제됨
                        - 🚫 자막이 없고 음성도 명확하지 않음
                        - 🌍 지역 제한으로 접근 불가
                        - ⏱️ 영상이 너무 길거나 용량이 큼
                        
                        **💡 해결 방법:**
                        - ✅ 다른 공개 영상으로 시도해보세요
                        - ✅ 자막이 있는 영상을 선택해보세요
                        - ✅ 짧은 영상(10분 이하)으로 테스트해보세요
                        """)
                        
                except Exception as e:
                    st.error("❌ **시스템 오류가 발생했습니다**")
                    st.markdown(f"""
                    **🔧 오류 내용:** `{str(e)}`
                    
                    **💡 해결 방법:**
                    - 🔄 페이지를 새로고침하고 다시 시도해보세요
                    - 🔗 URL이 정확한지 확인해보세요
                    - ⏰ 잠시 후 다시 시도해보세요
                    """)
        else:
            st.error("❌ 올바른 유튜브 URL을 입력해주세요.")
    else:
        st.warning("⚠️ 유튜브 URL을 입력해주세요.")

# 사용 안내
st.markdown("---")
st.markdown("### 💡 사용 방법")
st.markdown("""
**📝 쉬운 4단계 사용법**

**1️⃣ URL 입력**: 추출하고 싶은 유튜브 비디오 URL을 붙여넣기하세요  
**2️⃣ 옵션 선택**: 자막이 없는 경우 음성 인식을 사용할지 선택하세요  
**3️⃣ 추출 실행**: "텍스트 추출하기" 버튼을 클릭하세요  
**4️⃣ 결과 복사**: 추출된 텍스트를 선택하고 복사하세요

**🎯 잘 작동하는 영상 유형:**
- ✅ **공개 영상** (비공개/삭제된 것은 불가)
- ✅ **자막이 있는 영상** (한국어/영어 자막 권장)  
- ✅ **짧은 영상** (10분 이하 권장, 긴 영상은 시간 소요)
- ✅ **교육/뉴스 영상** (음성이 명확한 영상)

**⚠️ 추출이 어려운 경우:**
- ❌ 비공개/삭제된 영상
- ❌ 지역 제한 영상  
- ❌ 음악만 있고 말이 없는 영상
- ❌ 너무 긴 영상 (1시간 이상)
""")

st.markdown("### 📌 지원 형식")
st.markdown("""
✅ `youtube.com/watch?v=VIDEO_ID`  
✅ `youtu.be/VIDEO_ID`  
✅ `youtube.com/embed/VIDEO_ID`  
✅ `youtube.com/live/VIDEO_ID`
""")

# 푸터
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #5a6c7d; font-size: 14px; padding: 20px 0;">
✨ Made with ❤️ by YouTube Text Extractor<br>
🚀 빠르고 정확한 유튜브 텍스트 추출 서비스
</div>
""", unsafe_allow_html=True) 