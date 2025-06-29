import re
import os
import json
import tempfile
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import yt_dlp


class YouTubeTextExtractor:
    def __init__(self):
        self.video_info = {}
        self.transcript_data = []
        self.formatted_text = ""
        self.use_speech_recognition = True  # 음성 인식 사용 여부
        
    def extract_video_id(self, url):
        """유튜브 URL에서 비디오 ID 추출"""
        # 다양한 유튜브 URL 형식 지원
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/live\/([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def get_video_info(self, video_id):
        """비디오 정보 가져오기"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f'https://www.youtube.com/watch?v={video_id}', download=False)
                
                self.video_info = {
                    'title': info.get('title', '제목 없음'),
                    'channel': info.get('uploader', '채널 없음'),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'upload_date': info.get('upload_date', ''),
                    'description': info.get('description', ''),
                    'video_id': video_id
                }
                
        except Exception as e:
            print(f"비디오 정보 가져오기 실패: {e}")
            self.video_info = {'title': '정보 없음', 'channel': '정보 없음', 'video_id': video_id}
    
    def extract_transcript(self, video_id):
        """자막 추출"""
        try:
            # 자막 목록 가져오기
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # 사용 가능한 자막 정보 수집
            available_transcripts = []
            manually_created = []
            auto_generated = []
            
            for transcript in transcript_list:
                lang_info = {
                    'language_code': transcript.language_code,
                    'language': transcript.language,
                    'is_generated': transcript.is_generated,
                    'is_translatable': transcript.is_translatable
                }
                available_transcripts.append(lang_info)
                
                if transcript.is_generated:
                    auto_generated.append(transcript)
                else:
                    manually_created.append(transcript)
            
            print(f"사용 가능한 자막: {len(available_transcripts)}개")
            for trans in available_transcripts:
                status = "자동생성" if trans['is_generated'] else "수동작성"
                print(f"  - {trans['language']} ({trans['language_code']}) - {status}")
            
            # 자막 선택 우선순위
            transcript = None
            
            # 1. 수동 작성된 한국어 자막
            korean_manual = [t for t in manually_created if t.language_code == 'ko']
            if korean_manual:
                transcript = korean_manual[0]
                print("수동 작성된 한국어 자막을 사용합니다.")
            
            # 2. 수동 작성된 영어 자막
            elif manually_created:
                english_manual = [t for t in manually_created if t.language_code == 'en']
                if english_manual:
                    transcript = english_manual[0]
                    print("수동 작성된 영어 자막을 사용합니다.")
                else:
                    transcript = manually_created[0]
                    print(f"수동 작성된 {manually_created[0].language} 자막을 사용합니다.")
            
            # 3. 자동 생성된 한국어 자막
            elif auto_generated:
                korean_auto = [t for t in auto_generated if t.language_code == 'ko']
                if korean_auto:
                    transcript = korean_auto[0]
                    print("자동 생성된 한국어 자막을 사용합니다.")
                else:
                    # 4. 자동 생성된 영어 자막
                    english_auto = [t for t in auto_generated if t.language_code in ['en', 'en-US', 'en-GB']]
                    if english_auto:
                        transcript = english_auto[0]
                        print("자동 생성된 영어 자막을 사용합니다.")
                    else:
                        # 5. 첫 번째 사용 가능한 자막
                        transcript = auto_generated[0]
                        print(f"자동 생성된 {auto_generated[0].language} 자막을 사용합니다.")
            
            if transcript:
                self.transcript_data = transcript.fetch()
                print(f"자막 추출 완료: {len(self.transcript_data)}개 항목")
                return True
            else:
                print("사용 가능한 자막이 없습니다.")
                return False
            
        except Exception as e:
            error_msg = str(e)
            print(f"자막 추출 실패: {e}")
            
            # 구체적인 에러 메시지 제공
            if "Could not retrieve a transcript" in error_msg:
                if "Subtitles are disabled" in error_msg:
                    print("❌ 이 비디오는 자막이 비활성화되어 있습니다.")
                elif "No transcripts found" in error_msg:
                    print("❌ 이 비디오에는 자막이 없습니다.")
                else:
                    print("❌ 자막을 가져올 수 없습니다. 비디오가 비공개이거나 제한되어 있을 수 있습니다.")
            elif "Private video" in error_msg:
                print("❌ 비공개 비디오입니다.")
            elif "Video unavailable" in error_msg:
                print("❌ 비디오를 사용할 수 없습니다.")
            else:
                print("❌ 알 수 없는 오류가 발생했습니다.")
                
            return False
    
    def extract_audio_and_transcribe(self, video_id):
        """오디오 추출 후 음성 인식으로 텍스트 변환"""
        if not self.use_speech_recognition:
            return False
            
        try:
            print("자막이 없으므로 음성 인식을 시도합니다...")
            print("⚠️  이 과정은 비디오 길이에 따라 시간이 오래 걸릴 수 있습니다.")
            
            # Whisper 모듈 동적 임포트
            try:
                import whisper
            except ImportError:
                print("❌ Whisper가 설치되지 않았습니다. 다음 명령어로 설치해주세요:")
                print("pip install openai-whisper")
                return False
            
            # 임시 디렉토리 생성
            temp_dir = tempfile.mkdtemp()
            audio_file = os.path.join(temp_dir, f"{video_id}.wav")
            
            try:
                print("오디오 다운로드 중...")
                
                # yt-dlp로 오디오만 추출
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(temp_dir, f"{video_id}.%(ext)s"),
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'wav',
                        'preferredquality': '192',
                    }],
                    'quiet': True,
                    'no_warnings': True,
                }
                
                url = f'https://www.youtube.com/watch?v={video_id}'
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                # 오디오 파일 확인
                if not os.path.exists(audio_file):
                    # 다른 확장자로 생성된 경우 찾기
                    for file in os.listdir(temp_dir):
                        if file.startswith(video_id) and file.endswith('.wav'):
                            audio_file = os.path.join(temp_dir, file)
                            break
                    else:
                        print("❌ 오디오 파일 다운로드에 실패했습니다.")
                        return False
                
                print("음성 인식 중... (시간이 걸릴 수 있습니다)")
                
                # Whisper 모델 로드 (base 모델 사용 - 속도와 정확도의 균형)
                model = whisper.load_model("base")
                
                # 음성 인식 실행
                result = model.transcribe(audio_file, language='ko')  # 한국어 우선
                
                # 결과를 transcript_data 형식으로 변환
                self.transcript_data = []
                
                if 'segments' in result:
                    for segment in result['segments']:
                        # Whisper 결과를 딕셔너리 형태로 통일
                        self.transcript_data.append({
                            'text': segment['text'].strip(),
                            'start': segment['start'],
                            'duration': segment['end'] - segment['start']
                        })
                else:
                    # segments가 없는 경우 전체 텍스트를 하나의 항목으로
                    self.transcript_data.append({
                        'text': result['text'].strip(),
                        'start': 0.0,
                        'duration': 0.0
                    })
                
                print(f"음성 인식 완료: {len(self.transcript_data)}개 구간 인식됨")
                return True
                
            finally:
                # 임시 파일 정리
                try:
                    if os.path.exists(audio_file):
                        os.remove(audio_file)
                    for file in os.listdir(temp_dir):
                        file_path = os.path.join(temp_dir, file)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                    os.rmdir(temp_dir)
                except:
                    pass  # 파일 정리 실패해도 계속 진행
                    
        except Exception as e:
            print(f"음성 인식 실패: {e}")
            return False
    
    def format_transcript(self):
        """자막을 읽기 쉽게 포맷팅"""
        if not self.transcript_data:
            return "자막을 찾을 수 없습니다."
        
        formatted_lines = []
        current_paragraph = []
        
        for entry in self.transcript_data:
            # YouTube Transcript API 객체는 딕셔너리 또는 속성 접근 방식을 사용
            if hasattr(entry, 'text'):
                text = entry.text.strip()
                start_time = entry.start
            else:
                text = entry['text'].strip()
                start_time = entry['start']
            
            # 시간을 분:초 형식으로 변환
            minutes = int(start_time // 60)
            seconds = int(start_time % 60)
            time_str = f"{minutes:02d}:{seconds:02d}"
            
            # 문장 단위로 그룹화
            if text and not text.startswith('['):  # 자막 태그 제외
                current_paragraph.append(f"[{time_str}] {text}")
                
                # 문장이 끝나면 문단 나누기
                if text.endswith(('.', '!', '?', '다', '요', '까', '네')):
                    if current_paragraph:
                        formatted_lines.append(' '.join(current_paragraph))
                        current_paragraph = []
        
        # 남은 텍스트 추가
        if current_paragraph:
            formatted_lines.append(' '.join(current_paragraph))
        
        self.formatted_text = '\n\n'.join(formatted_lines)
        return self.formatted_text
    
    def categorize_content(self):
        """내용을 카테고리별로 분류"""
        if not self.formatted_text:
            return {}
        
        categories = {
            '인사말': [],
            '주요 내용': [],
            '질문과 답변': [],
            '마무리': [],
            '기타': []
        }
        
        paragraphs = self.formatted_text.split('\n\n')
        
        for i, paragraph in enumerate(paragraphs):
            # 간단한 분류 로직
            if i == 0 or '안녕' in paragraph or '시작' in paragraph:
                categories['인사말'].append(paragraph)
            elif '질문' in paragraph or '답변' in paragraph or '?' in paragraph:
                categories['질문과 답변'].append(paragraph)
            elif i >= len(paragraphs) - 2 or '마무리' in paragraph or '감사' in paragraph:
                categories['마무리'].append(paragraph)
            else:
                categories['주요 내용'].append(paragraph)
        
        return categories
    
    def save_to_html(self, output_file='youtube_transcript.html'):
        """HTML 파일로 저장"""
        categories = self.categorize_content()
        
        html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.video_info.get('title', '유튜브 텍스트 추출')}</title>
    <style>
        body {{
            font-family: 'Noto Sans KR', Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            background-color: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            border-bottom: 2px solid #e74c3c;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .video-info {{
            background: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .category {{
            margin-bottom: 30px;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }}
        .category h2 {{
            color: #2c3e50;
            margin-bottom: 15px;
        }}
        .paragraph {{
            background: #f8f9fa;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 5px;
            border-left: 3px solid #3498db;
        }}
        .timestamp {{
            color: #e74c3c;
            font-weight: bold;
        }}
        .full-text {{
            border-top: 2px solid #95a5a6;
            padding-top: 20px;
            margin-top: 30px;
        }}
        .full-text h2 {{
            color: #2c3e50;
        }}
        .full-text-content {{
            background: #f1f2f6;
            padding: 20px;
            border-radius: 5px;
            white-space: pre-line;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>유튜브 텍스트 추출</h1>
            <div class="video-info">
                <h3>{self.video_info.get('title', '제목 없음')}</h3>
                <p><strong>채널:</strong> {self.video_info.get('channel', '정보 없음')}</p>
                <p><strong>비디오 ID:</strong> {self.video_info.get('video_id', '')}</p>
                <p><strong>추출 일시:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </div>
        
        <div class="categories">
"""
        
        # 카테고리별 내용 추가
        for category, paragraphs in categories.items():
            if paragraphs:
                html_content += f"""
            <div class="category">
                <h2>{category}</h2>
"""
                for paragraph in paragraphs:
                    # 타임스탬프 하이라이트
                    highlighted = re.sub(r'\[(\d{2}:\d{2})\]', r'<span class="timestamp">[\1]</span>', paragraph)
                    html_content += f'                <div class="paragraph">{highlighted}</div>\n'
                
                html_content += "            </div>\n"
        
        # 전체 텍스트 추가
        html_content += f"""
        </div>
        
        <div class="full-text">
            <h2>전체 텍스트</h2>
            <div class="full-text-content">{self.formatted_text}</div>
        </div>
    </div>
</body>
</html>
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_file
    
    def process_youtube_url(self, url, output_file=None):
        """유튜브 URL 처리 메인 함수"""
        print(f"유튜브 URL 처리 중: {url}")
        
        # 비디오 ID 추출
        video_id = self.extract_video_id(url)
        if not video_id:
            print("올바른 유튜브 URL이 아닙니다.")
            return False
        
        print(f"비디오 ID: {video_id}")
        
        # 비디오 정보 가져오기
        self.get_video_info(video_id)
        print(f"비디오 제목: {self.video_info.get('title')}")
        
        # 자막 추출 시도
        transcript_success = self.extract_transcript(video_id)
        
        # 자막이 없으면 음성 인식 시도
        if not transcript_success:
            print("\n자막을 찾을 수 없습니다. 음성 인식을 시도합니다...")
            if not self.extract_audio_and_transcribe(video_id):
                print("❌ 자막 추출과 음성 인식 모두 실패했습니다.")
                print("💡 다음을 확인해보세요:")
                print("   - 비디오에 음성이 있는지 확인")
                print("   - 비디오가 너무 길지 않은지 확인 (긴 비디오는 시간이 오래 걸림)")
                print("   - FFmpeg가 설치되어 있는지 확인")
                return False
            else:
                print("✅ 음성 인식으로 텍스트 추출 성공!")
        
        print(f"자막 추출 완료: {len(self.transcript_data)}개 항목")
        
        # 텍스트 포맷팅
        self.format_transcript()
        
        # HTML 파일로 저장
        if not output_file:
            # 안전한 파일명 생성
            safe_title = re.sub(r'[^\w\s-]', '', self.video_info.get('title', 'youtube_transcript'))
            safe_title = re.sub(r'[-\s]+', '-', safe_title)[:50]
            output_file = f"{safe_title}_{video_id}.html"
        
        saved_file = self.save_to_html(output_file)
        print(f"HTML 파일 저장 완료: {saved_file}")
        
        return True


def main():
    extractor = YouTubeTextExtractor()
    
    print("=== 유튜브 텍스트 추출 프로그램 ===")
    print()
    
    while True:
        url = input("유튜브 URL을 입력하세요 (종료하려면 'q' 입력): ").strip()
        
        if url.lower() == 'q':
            print("프로그램을 종료합니다.")
            break
        
        if not url:
            print("URL을 입력해주세요.")
            continue
        
        try:
            success = extractor.process_youtube_url(url)
            if success:
                print("✅ 텍스트 추출 및 HTML 파일 생성이 완료되었습니다!")
            else:
                print("❌ 텍스트 추출에 실패했습니다.")
        except Exception as e:
            print(f"오류 발생: {e}")
        
        print("-" * 50)


if __name__ == "__main__":
    main() 