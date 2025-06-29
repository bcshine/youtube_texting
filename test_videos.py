#!/usr/bin/env python
# -*- coding: utf-8 -*-

from youtube_text_extractor import YouTubeTextExtractor

def test_videos_with_subtitles():
    """자막이 있는 테스트용 비디오 URL들"""
    test_urls = [
        {
            'url': 'https://www.youtube.com/watch?v=jNQXAC9IVRw',
            'title': 'TED 강의 - 자막이 보통 있음',
            'description': '대부분의 TED 강의는 다국어 자막을 제공합니다'
        },
        {
            'url': 'https://www.youtube.com/watch?v=8S0FDjFBj8o',
            'title': 'YouTube 공식 채널 영상',
            'description': '대규모 채널의 영상들은 자막이 있는 경우가 많습니다'
        },
        {
            'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'title': '유명한 뮤직비디오',
            'description': '인기 뮤직비디오들은 자동 생성 자막이 있습니다'
        }
    ]
    return test_urls

def check_video_subtitles(url):
    """비디오에 자막이 있는지 미리 확인"""
    print(f"비디오 자막 상태 확인 중: {url}")
    
    extractor = YouTubeTextExtractor()
    video_id = extractor.extract_video_id(url)
    
    if not video_id:
        print("❌ 올바르지 않은 유튜브 URL입니다.")
        return False
    
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        manually_created = []
        auto_generated = []
        
        for transcript in transcript_list:
            if transcript.is_generated:
                auto_generated.append(transcript)
            else:
                manually_created.append(transcript)
        
        print(f"\n📋 자막 정보:")
        print(f"   비디오 ID: {video_id}")
        
        if manually_created:
            print(f"   ✅ 수동 작성된 자막: {len(manually_created)}개")
            for t in manually_created:
                print(f"      - {t.language} ({t.language_code})")
        
        if auto_generated:
            print(f"   🤖 자동 생성된 자막: {len(auto_generated)}개")
            for t in auto_generated:
                print(f"      - {t.language} ({t.language_code})")
        
        if manually_created or auto_generated:
            print("   ✅ 이 비디오는 텍스트 추출이 가능합니다!")
            return True
        else:
            print("   ❌ 이 비디오에는 자막이 없습니다.")
            return False
            
    except Exception as e:
        print(f"   ❌ 자막 확인 실패: {e}")
        if "Subtitles are disabled" in str(e):
            print("   📝 이 비디오는 자막이 비활성화되어 있습니다.")
        elif "Private video" in str(e):
            print("   🔒 비공개 비디오입니다.")
        return False

def main():
    print("=== 유튜브 자막 확인 도구 ===\n")
    
    while True:
        print("1. 비디오 URL 자막 상태 확인")
        print("2. 자막이 있는 테스트 비디오 목록 보기") 
        print("3. 종료")
        
        choice = input("\n선택하세요 (1-3): ").strip()
        
        if choice == '1':
            url = input("\n유튜브 URL을 입력하세요: ").strip()
            if url:
                check_video_subtitles(url)
            print("-" * 50)
            
        elif choice == '2':
            print("\n📺 자막이 있는 테스트 비디오들:")
            test_videos = test_videos_with_subtitles()
            
            for i, video in enumerate(test_videos, 1):
                print(f"\n{i}. {video['title']}")
                print(f"   URL: {video['url']}")
                print(f"   설명: {video['description']}")
            
            print("\n이 비디오들 중 하나를 프로그램에서 테스트해보세요!")
            print("-" * 50)
            
        elif choice == '3':
            print("프로그램을 종료합니다.")
            break
            
        else:
            print("올바른 번호를 선택해주세요.")
            
if __name__ == "__main__":
    main() 