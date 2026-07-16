@echo off
REM 영어 번역 채팅 애플리케이션 설정 스크립트

echo ============================================
echo Flask 영어 번역 채팅 앱 설정
echo ============================================
echo.

REM 가상환경 확인
if not exist "venv" (
    echo [1/4] 가상환경 생성 중...
    python -m venv venv
    call venv\Scripts\activate.bat
) else (
    echo [1/4] 가상환경 활성화 중...
    call venv\Scripts\activate.bat
)

echo [2/4] 의존성 설치 중...
pip install -r requirements.txt

REM .env 파일 확인
if not exist ".env" (
    echo [3/4] .env 파일 생성 중...
    copy .env.example .env
    echo.
    echo !!! .env 파일을 생성했습니다 !!!
    echo !!! .env 파일을 열어서 MSSQL 연결 정보를 수정하세요 !!!
    echo.
    pause
) else (
    echo [3/4] .env 파일이 이미 존재합니다.
)

echo [4/4] 설정 완료!
echo.
echo 시작하려면 다음 명령어를 실행하세요:
echo   python app.py
echo.
echo 또는 run.bat을 실행하세요.
echo.
pause
