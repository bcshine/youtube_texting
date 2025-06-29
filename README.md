# 유튜브 텍스트 추출 프로그램

유튜브 비디오의 자막을 추출하여 읽기 쉬운 HTML 형태로 저장하는 프로그램입니다.

## 주요 기능

- ✅ 유튜브 URL에서 자막 자동 추출
- ✅ **자막이 없어도 음성 인식으로 텍스트 추출** (새 기능!)
- ✅ 한국어/영어 자막 우선 지원
- ✅ OpenAI Whisper 기반 고품질 음성 인식
- ✅ 대화 내용을 항목별로 분류 (인사말, 주요 내용, 질문과 답변, 마무리)
- ✅ 타임스탬프와 함께 텍스트 정리
- ✅ 아름다운 HTML 파일로 저장
- ✅ 비디오 정보 (제목, 채널, 추출일시) 포함

## 설치 방법

1. **Python 설치 확인**
   ```bash
   python --version
   ```
   (Python 3.7 이상 필요)

2. **FFmpeg 설치** (음성 인식에 필요)
   - **Windows**: [FFmpeg 다운로드](https://ffmpeg.org/download.html#build-windows)에서 다운로드 후 PATH에 추가
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt update && sudo apt install ffmpeg`

3. **필요한 라이브러리 설치**
   ```bash
   pip install -r requirements.txt
   ```
   
   또는 간편하게:
   ```bash
   install.bat  # Windows용 자동 설치
   ```

## 사용 방법

### 기본 사용법
```bash
python youtube_text_extractor.py
```

프로그램을 실행하면 유튜브 URL 입력을 요청합니다.

### 지원하는 URL 형식
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `https://www.youtube.com/live/VIDEO_ID`

### 사용 예시
```
=== 유튜브 텍스트 추출 프로그램 ===

유튜브 URL을 입력하세요 (종료하려면 'q' 입력): https://www.youtube.com/watch?v=example
유튜브 URL 처리 중: https://www.youtube.com/watch?v=example
비디오 ID: example
비디오 제목: 예시 비디오
자막 추출 완료: 150개 항목
HTML 파일 저장 완료: 예시-비디오_example.html
✅ 텍스트 추출 및 HTML 파일 생성이 완료되었습니다!
```

## 출력 파일 형식

생성되는 HTML 파일에는 다음 내용이 포함됩니다:

1. **비디오 정보**
   - 제목
   - 채널명
   - 비디오 ID
   - 추출 일시

2. **항목별 분류**
   - 인사말
   - 주요 내용
   - 질문과 답변
   - 마무리

3. **전체 텍스트**
   - 타임스탬프와 함께 전체 자막

## 주의사항

🎉 **새로운 기능**: 자막이 없는 비디오에서도 음성 인식으로 텍스트 추출이 가능합니다!

## 작동 방식
1. **자막 우선**: 먼저 유튜브 자막(수동/자동)을 찾습니다
2. **음성 인식 대체**: 자막이 없으면 OpenAI Whisper로 음성을 텍스트로 변환합니다
3. **고품질 결과**: 한국어, 영어 등 다양한 언어를 정확하게 인식합니다

## 주의사항
- 비공개 또는 제한된 비디오는 처리할 수 없습니다
- **음성 인식은 시간이 걸릴 수 있습니다** (비디오 길이에 따라 1-10분)
- 음성이 명확하지 않으면 인식 정확도가 떨어질 수 있습니다
- 네트워크 연결이 필요합니다
- FFmpeg가 설치되어 있어야 합니다

### 자막이 있는 비디오 찾기

다음과 같은 비디오들은 보통 자막이 있습니다:
- 📚 교육 콘텐츠 (TED 강의, 온라인 강의 등)
- 🎬 대형 채널의 공식 비디오
- 🎵 인기 뮤직비디오 (자동 생성 자막)
- 📺 뉴스나 다큐멘터리

### 자막 상태 미리 확인하기

비디오에 자막이 있는지 미리 확인하려면:
```bash
python test_videos.py
```

## 문제 해결

### 자막을 찾을 수 없다는 오류가 발생하는 경우:
- 해당 비디오에 자막이 없을 수 있습니다.
- 비디오가 비공개이거나 제한되어 있을 수 있습니다.

### 라이브러리 설치 오류가 발생하는 경우:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 기타 오류:
- Python 버전을 확인해주세요 (3.7 이상 필요)
- 인터넷 연결을 확인해주세요

## 개발 정보

- Python 3.7+
- 주요 라이브러리: yt-dlp, youtube-transcript-api
- 출력 형식: HTML (UTF-8 인코딩)

---

문제가 있거나 개선 사항이 있으면 언제든 알려주세요! 