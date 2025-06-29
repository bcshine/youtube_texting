#!/usr/bin/env python
# -*- coding: utf-8 -*-

from youtube_text_extractor import YouTubeTextExtractor

def test_speech_recognition():
    """음성 인식 기능 테스트"""
    print("=== 음성 인식 기능 테스트 ===")
    
    # 자막이 없는 짧은 테스트 비디오 URL 추천
    test_urls = [
        "https://www.youtube.com/watch?v=QhgpZyDQ-vY",  # 사용자가 테스트한 URL
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Astley - Never Gonna Give You Up
    ]
    
    print("테스트할 비디오 URL을 선택하거나 직접 입력하세요:")
    print("1. 테스트용 짧은 비디오")
    print("2. 직접 URL 입력")
    
    choice = input("선택하세요 (1 또는 2): ").strip()
    
    if choice == '1':
        url = test_urls[0]
        print(f"선택된 URL: {url}")
    elif choice == '2':
        url = input("유튜브 URL을 입력하세요: ").strip()
    else:
        print("잘못된 선택입니다.")
        return
    
    if not url:
        print("URL을 입력해주세요.")
        return
    
    print("\n" + "="*50)
    print("음성 인식 테스트를 시작합니다...")
    print("⚠️  처음 실행 시 Whisper 모델을 다운로드하므로 시간이 걸릴 수 있습니다.")
    print("="*50)
    
    extractor = YouTubeTextExtractor()
    
    # 비디오 ID 추출
    video_id = extractor.extract_video_id(url)
    if not video_id:
        print("❌ 올바른 유튜브 URL이 아닙니다.")
        return
    
    # 비디오 정보 가져오기
    extractor.get_video_info(video_id)
    print(f"🎬 비디오: {extractor.video_info.get('title', '제목 없음')}")
    print(f"📺 채널: {extractor.video_info.get('channel', '정보 없음')}")
    
    # 먼저 자막 확인
    print("\n1단계: 자막 확인 중...")
    has_subtitles = extractor.extract_transcript(video_id)
    
    if has_subtitles:
        print("✅ 자막을 찾았습니다! 자막을 사용합니다.")
    else:
        print("📢 자막이 없습니다. 음성 인식을 시작합니다...")
        
        # 음성 인식 시도
        success = extractor.extract_audio_and_transcribe(video_id)
        
        if success:
            print("🎉 음성 인식 성공!")
        else:
            print("❌ 음성 인식 실패")
            return
    
    # 결과 출력
    if extractor.transcript_data:
        print(f"\n📝 추출된 텍스트 ({len(extractor.transcript_data)}개 구간):")
        print("-" * 30)
        
        for i, item in enumerate(extractor.transcript_data[:5]):  # 처음 5개만 표시
            # 객체 타입에 따라 다른 접근 방식 사용
            if hasattr(item, 'text'):
                text = item.text
                start_time = item.start
            else:
                text = item['text']
                start_time = item['start']
            
            minutes = int(start_time // 60)
            seconds = int(start_time % 60)
            print(f"[{minutes:02d}:{seconds:02d}] {text}")
        
        if len(extractor.transcript_data) > 5:
            print(f"... (총 {len(extractor.transcript_data)}개 구간 중 5개만 표시)")
        
        # HTML 파일 저장 여부 확인
        save_html = input("\nHTML 파일로 저장하시겠습니까? (y/n): ").strip().lower()
        if save_html == 'y':
            extractor.format_transcript()
            output_file = f"speech_recognition_test_{video_id}.html"
            saved_file = extractor.save_to_html(output_file)
            print(f"💾 저장 완료: {saved_file}")
    else:
        print("❌ 텍스트를 추출할 수 없었습니다.")

if __name__ == "__main__":
    test_speech_recognition() 