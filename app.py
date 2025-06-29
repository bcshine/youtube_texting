import streamlit as st
import re
import os
import tempfile
from datetime import datetime
from youtube_text_extractor import YouTubeTextExtractor
import base64
import streamlit.components.v1 as components

# 페이지 설정
st.set_page_config(
    page_title="유튜브 텍스트 추출기",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 모바일 웹앱 메타 태그 추가
components.html("""
<meta name="theme-color" content="#ff0000">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="YT텍스트">
<meta name="mobile-web-app-capable" content="yes">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    /* 모바일 최적화 스타일 */
    @media only screen and (max-width: 768px) {
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
    }
</style>
""", height=0)

# CSS 스타일링
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #FF0000;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 3rem;
    }
    .feature-box {
        background: linear-gradient(90deg, #FF0000, #FF4444);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .success-box {
        background: linear-gradient(90deg, #00AA00, #44AA44);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .stButton > button {
        background: linear-gradient(90deg, #FF0000, #FF4444);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 25px;
        font-weight: bold;
        font-size: 1.1rem;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #CC0000, #FF2222);
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(255,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

# 메인 헤더
st.markdown('<h1 class="main-header">📺 유튜브 텍스트 추출기</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">유튜브 비디오의 자막을 추출하여 아름다운 HTML로 저장하는 도구</p>', unsafe_allow_html=True)

# 사이드바 - 기능 소개
with st.sidebar:
    st.markdown("## ✨ 주요 기능")
    st.markdown("""
    - ✅ 유튜브 URL에서 자막 자동 추출
    - ✅ **자막이 없어도 음성 인식으로 텍스트 추출**
    - ✅ 한국어/영어 자막 우선 지원  
    - ✅ OpenAI Whisper 기반 고품질 음성 인식
    - ✅ 대화 내용을 항목별로 분류
    - ✅ 타임스탬프와 함께 텍스트 정리
    - ✅ 아름다운 HTML 파일로 저장
    - ✅ 비디오 정보 포함
    """)
    
    st.markdown("## 🎯 지원 URL 형식")
    st.markdown("""
    - `youtube.com/watch?v=VIDEO_ID`
    - `youtu.be/VIDEO_ID`  
    - `youtube.com/embed/VIDEO_ID`
    - `youtube.com/live/VIDEO_ID`
    """)
    
    st.markdown("## 📱 모바일 바로가기 만들기")
    st.markdown("""
    **🍎 iOS (Safari)**
    1. 공유 버튼 (⬆️) 터치
    2. "홈 화면에 추가" 선택
    3. 앱 이름 확인 후 "추가"
    
    **🤖 Android (Chrome)**
    1. 메뉴 (⋮) → "홈 화면에 추가"
    2. 또는 주소창의 "설치" 아이콘 터치
    
    **💻 PC (Chrome/Edge)**
    1. 주소창 오른쪽 "앱 설치" 아이콘 클릭
    """)

# 메인 컨텐츠
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # URL 입력
    st.markdown("### 🔗 유튜브 URL 입력")
    youtube_url = st.text_input(
        "유튜브 URL",
        placeholder="유튜브 URL을 입력하세요 (예: https://www.youtube.com/watch?v=example)",
        help="유튜브 비디오의 URL을 입력하면 자막 또는 음성을 텍스트로 추출합니다.",
        label_visibility="collapsed"
    )
    
    # 옵션 설정
    st.markdown("### ⚙️ 추출 옵션")
    col_opt1, col_opt2 = st.columns(2)
    
    with col_opt1:
        use_speech_recognition = st.checkbox(
            "음성 인식 사용", 
            value=True,
            help="자막이 없을 때 OpenAI Whisper로 음성을 텍스트로 변환합니다."
        )
    
    with col_opt2:
        save_format = st.selectbox(
            "저장 형식",
            ["HTML", "텍스트"],
            help="추출된 텍스트를 저장할 파일 형식을 선택하세요."
        )
    
    # 추출 버튼
    if st.button("📥 텍스트 추출 시작", type="primary"):
        if youtube_url:
            # URL 유효성 검사
            url_pattern = r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/live\/)([^&\n?#]+)'
            if re.search(url_pattern, youtube_url):
                
                # 진행 상태 표시
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # YouTubeTextExtractor 인스턴스 생성
                    status_text.text("🔍 비디오 정보를 가져오는 중...")
                    progress_bar.progress(10)
                    
                    extractor = YouTubeTextExtractor()
                    extractor.use_speech_recognition = use_speech_recognition
                    
                    # URL 처리
                    status_text.text("🎬 비디오 분석 중...")
                    progress_bar.progress(30)
                    
                    result_file = extractor.process_youtube_url(youtube_url)
                    
                    if result_file:
                        progress_bar.progress(100)
                        status_text.text("✅ 추출 완료!")
                        
                        # 성공 메시지
                        st.markdown('<div class="success-box">🎉 <strong>텍스트 추출이 완료되었습니다!</strong></div>', unsafe_allow_html=True)
                        
                        # 비디오 정보 표시
                        if extractor.video_info:
                            st.markdown("### 📋 비디오 정보")
                            col_info1, col_info2 = st.columns(2)
                            
                            with col_info1:
                                st.write(f"**제목:** {extractor.video_info.get('title', '정보 없음')}")
                                st.write(f"**채널:** {extractor.video_info.get('channel', '정보 없음')}")
                            
                            with col_info2:
                                st.write(f"**비디오 ID:** {extractor.video_info.get('video_id', '정보 없음')}")
                                duration = extractor.video_info.get('duration', 0)
                                if duration:
                                    minutes = duration // 60
                                    seconds = duration % 60
                                    st.write(f"**길이:** {minutes}분 {seconds}초")
                        
                        # 추출된 텍스트
                        if extractor.formatted_text:
                            # 요약 텍스트 생성
                            def create_summary(text):
                                lines = text.split('\n')
                                # 타임스탬프가 있는 줄들만 필터링
                                timestamp_lines = [line for line in lines if '[' in line and ']' in line]
                                
                                # 처음 5개와 마지막 5개 라인으로 요약
                                if len(timestamp_lines) > 10:
                                    summary_lines = timestamp_lines[:5] + ['...'] + timestamp_lines[-5:]
                                else:
                                    summary_lines = timestamp_lines
                                
                                return '\n'.join(summary_lines)
                            
                            summary_text = create_summary(extractor.formatted_text)
                            
                            st.markdown("### 📋 텍스트 복사")
                            
                            # 탭으로 전체 텍스트와 요약 텍스트 분리
                            tab1, tab2 = st.tabs(["📄 전체 텍스트", "📝 요약 텍스트"])
                            
                            with tab1:
                                # 복사 버튼과 텍스트 영역
                                col_copy1, col_text1 = st.columns([1, 4])
                                
                                with col_copy1:
                                    if st.button("📋 전체 텍스트 복사", key="copy_full", type="secondary"):
                                        # JavaScript로 클립보드에 복사 (안전한 방식)
                                        import json
                                        safe_text = json.dumps(extractor.formatted_text)
                                        copy_js = f"""
                                        <script>
                                        const textToCopy = {safe_text};
                                        navigator.clipboard.writeText(textToCopy).then(function() {{
                                            alert('✅ 전체 텍스트가 클립보드에 복사되었습니다!');
                                        }}, function(err) {{
                                            // Fallback for older browsers
                                            const textArea = document.createElement('textarea');
                                            textArea.value = textToCopy;
                                            document.body.appendChild(textArea);
                                            textArea.select();
                                            document.execCommand('copy');
                                            document.body.removeChild(textArea);
                                            alert('✅ 전체 텍스트가 클립보드에 복사되었습니다!');
                                        }});
                                        </script>
                                        """
                                        components.html(copy_js, height=0)
                                
                                with col_text1:
                                    st.markdown("**전체 추출된 텍스트:**")
                                
                                st.text_area(
                                    "전체 텍스트",
                                    extractor.formatted_text,
                                    height=300,
                                    label_visibility="collapsed"
                                )
                                
                                # 전체 텍스트 정보
                                total_lines = len(extractor.formatted_text.split('\n'))
                                st.info(f"📊 전체 {total_lines}줄의 텍스트가 추출되었습니다.")
                            
                            with tab2:
                                # 복사 버튼과 텍스트 영역
                                col_copy2, col_text2 = st.columns([1, 4])
                                
                                with col_copy2:
                                    if st.button("📋 요약 텍스트 복사", key="copy_summary", type="secondary"):
                                        # JavaScript로 클립보드에 복사 (안전한 방식)
                                        import json
                                        safe_summary = json.dumps(summary_text)
                                        copy_js = f"""
                                        <script>
                                        const textToCopy = {safe_summary};
                                        navigator.clipboard.writeText(textToCopy).then(function() {{
                                            alert('✅ 요약 텍스트가 클립보드에 복사되었습니다!');
                                        }}, function(err) {{
                                            // Fallback for older browsers
                                            const textArea = document.createElement('textarea');
                                            textArea.value = textToCopy;
                                            document.body.appendChild(textArea);
                                            textArea.select();
                                            document.execCommand('copy');
                                            document.body.removeChild(textArea);
                                            alert('✅ 요약 텍스트가 클립보드에 복사되었습니다!');
                                        }});
                                        </script>
                                        """
                                        components.html(copy_js, height=0)
                                
                                with col_text2:
                                    st.markdown("**요약된 텍스트:**")
                                
                                st.text_area(
                                    "요약 텍스트",
                                    summary_text,
                                    height=200,
                                    label_visibility="collapsed"
                                )
                                
                                # 요약 텍스트 설명
                                st.info("📝 처음 5개와 마지막 5개 주요 구간을 요약했습니다.")
                            
                            # 복사 안내
                            st.markdown("---")
                            st.markdown("""
                            **💡 텍스트 복사 방법:**
                            
                            **🖱️ 간편한 방법:** 위의 **"📋 복사"** 버튼을 클릭하세요!
                            
                            **⌨️ 수동 방법:** 텍스트 박스 클릭 → **Ctrl+A** (전체 선택) → **Ctrl+C** (복사)
                            """)
                            
                            # 추가 정보
                            st.markdown("### 📊 추출 정보")
                            col_info1, col_info2, col_info3 = st.columns(3)
                            
                            with col_info1:
                                st.metric("추출된 자막", f"{len(extractor.transcript_data)}개")
                            
                            with col_info2:
                                text_length = len(extractor.formatted_text)
                                st.metric("텍스트 길이", f"{text_length:,}자")
                            
                            with col_info3:
                                word_count = len(extractor.formatted_text.split())
                                st.metric("단어 수", f"{word_count:,}개")
                    
                    else:
                        st.error("❌ 텍스트 추출에 실패했습니다. 비디오가 비공개이거나 자막/음성을 추출할 수 없습니다.")
                        
                except Exception as e:
                    progress_bar.progress(0)
                    status_text.text("")
                    st.error(f"❌ 오류가 발생했습니다: {str(e)}")
                    st.write("문제가 계속 발생하면 다른 비디오로 시도해보세요.")
            
            else:
                st.error("❌ 올바른 유튜브 URL을 입력해주세요.")
        else:
            st.warning("⚠️ 유튜브 URL을 입력해주세요.")

# 사용 예시
st.markdown("---")
st.markdown("### 💡 사용 예시")

example_col1, example_col2 = st.columns(2)

with example_col1:
    st.markdown("""
    **자막이 있는 비디오 (빠른 처리):**
    - TED 강의
    - 교육 콘텐츠  
    - 대형 채널의 공식 비디오
    - 뉴스나 다큐멘터리
    """)

with example_col2:
    st.markdown("""
    **자막이 없는 비디오 (음성 인식):**
    - 개인 브이로그
    - 팟캐스트
    - 강의 녹화본
    - 인터뷰 영상
    """)

# 푸터
st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: #666;">Made with ❤️ by YouTube Text Extractor | '
    '<a href="https://github.com/bcshine/youtube_texting" target="_blank">GitHub</a></p>',
    unsafe_allow_html=True
) 