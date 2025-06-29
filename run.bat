@echo off
chcp 65001
echo ================================
echo 유튜브 텍스트 추출 프로그램
echo ================================
echo.

echo 1. 명령줄 버전
echo 2. GUI 버전
echo 3. 자막 확인 도구
echo.
set /p choice="선택하세요 (1, 2 또는 3): "

if "%choice%"=="1" (
    echo 명령줄 버전을 실행합니다...
    python youtube_text_extractor.py
) else if "%choice%"=="2" (
    echo GUI 버전을 실행합니다...
    python gui_version.py
) else if "%choice%"=="3" (
    echo 자막 확인 도구를 실행합니다...
    python test_videos.py
) else (
    echo 잘못된 선택입니다.
    pause
)

pause 