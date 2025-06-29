#!/usr/bin/env python
# -*- coding: utf-8 -*-

from youtube_text_extractor import YouTubeTextExtractor

def quick_test():
    """빠른 테스트"""
    # 이전에 오류가 발생했던 URL로 테스트
    test_url = "https://www.youtube.com/watch?v=pA6OdXQLCss"
    
    print("=== 빠른 테스트 ===")
    print(f"테스트 URL: {test_url}")
    print()
    
    extractor = YouTubeTextExtractor()
    
    try:
        success = extractor.process_youtube_url(test_url)
        if success:
            print("🎉 성공! 텍스트 추출이 완료되었습니다!")
            
            # 처음 3개 항목 미리보기
            if extractor.transcript_data:
                print("\n📝 추출된 텍스트 미리보기:")
                print("-" * 40)
                
                for i, item in enumerate(extractor.transcript_data[:3]):
                    if hasattr(item, 'text'):
                        text = item.text
                        start_time = item.start
                    else:
                        text = item['text']
                        start_time = item['start']
                    
                    minutes = int(start_time // 60)
                    seconds = int(start_time % 60)
                    print(f"[{minutes:02d}:{seconds:02d}] {text}")
                
                print(f"... (총 {len(extractor.transcript_data)}개 항목)")
        else:
            print("❌ 텍스트 추출에 실패했습니다.")
            
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    quick_test() 