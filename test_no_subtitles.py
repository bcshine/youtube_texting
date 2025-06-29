#!/usr/bin/env python
# -*- coding: utf-8 -*-

from youtube_text_extractor import YouTubeTextExtractor

def test_no_subtitles():
    """자막이 없는 비디오로 음성 인식 테스트"""
    # 이전에 자막이 비활성화되어 실패했던 URL
    test_url = "https://www.youtube.com/watch?v=QhgpZyDQ-vY"
    
    print("=== 음성 인식 테스트 (자막 없는 비디오) ===")
    print(f"테스트 URL: {test_url}")
    print("⚠️  이 테스트는 시간이 걸릴 수 있습니다 (음성 인식 과정)")
    print()
    
    extractor = YouTubeTextExtractor()
    
    try:
        success = extractor.process_youtube_url(test_url)
        if success:
            print("🎉 음성 인식 성공! 자막이 없어도 텍스트 추출이 완료되었습니다!")
            
            # 처음 5개 항목 미리보기
            if extractor.transcript_data:
                print("\n📝 음성 인식으로 추출된 텍스트:")
                print("-" * 40)
                
                for i, item in enumerate(extractor.transcript_data[:5]):
                    if hasattr(item, 'text'):
                        text = item.text
                        start_time = item.start
                    else:
                        text = item['text']
                        start_time = item['start']
                    
                    minutes = int(start_time // 60)
                    seconds = int(start_time % 60)
                    print(f"[{minutes:02d}:{seconds:02d}] {text}")
                
                print(f"... (총 {len(extractor.transcript_data)}개 구간)")
                print("\n💾 HTML 파일도 자동으로 저장되었습니다!")
        else:
            print("❌ 음성 인식 실패")
            print("💡 FFmpeg가 설치되어 있는지 확인해주세요")
            
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_no_subtitles() 