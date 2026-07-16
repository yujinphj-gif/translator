@echo off
REM 영어 번역 채팅 애플리케이션 실행 스크립트

REM 가상환경 활성화
if exist "venv" (
    call venv\Scripts\activate.bat
) else (
    echo 가상환경이 없습니다. setup.bat을 먼저 실행하세요.
    pause
    exit /b 1
)

REM .env 파일 확인
if not exist ".env" (
    echo .env 파일이 없습니다. setup.bat을 먼저 실행하세요.
    pause
    exit /b 1
)

echo ============================================
echo Flask 영어 번역 채팅 앱 실행 중...
echo ============================================
echo.
echo 브라우저에서 다음 주소로 접속하세요:
echo   http://localhost:5000
echo.
echo 앱을 종료하려면 Ctrl+C를 누르세요.
echo.

python app.py
