@echo off
chcp 65001
echo ================================
echo 유튜브 텍스트 추출 프로그램 설치
echo ================================
echo.

echo Python 버전 확인 중...
python --version
if errorlevel 1 (
    echo.
    echo 오류: Python이 설치되어 있지 않습니다.
    echo Python 3.7 이상을 설치해주세요.
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo 필요한 라이브러리를 설치합니다...
echo.

echo pip 업그레이드 중...
python -m pip install --upgrade pip

echo.
echo 필요한 라이브러리 설치 중...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo 오류: 라이브러리 설치에 실패했습니다.
    echo 인터넷 연결을 확인하고 다시 시도해주세요.
    pause
    exit /b 1
) else (
    echo.
    echo ================================
    echo 설치가 완료되었습니다!
    echo ================================
    echo.
    echo 프로그램을 실행하려면 run.bat 파일을 실행하세요.
    echo.
)

pause 