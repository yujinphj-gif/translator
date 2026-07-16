# 빠른 시작 가이드

## 📋 사전 요구사항

- Windows / Mac / Linux
- Python 3.8 이상
- MSSQL Server 또는 SQL Server Express
- ODBC Driver 17 for SQL Server

## 🚀 설치 및 실행 (Windows)

### 방법 1: 자동 설치 (추천)

```bash
setup.bat
```

그 다음 `.env` 파일을 열어서 MSSQL 연결 정보를 수정하고 저장합니다.

```bash
run.bat
```

### 방법 2: 수동 설치

#### 1단계: 가상환경 생성

```bash
python -m venv venv
venv\Scripts\activate
```

#### 2단계: 의존성 설치

```bash
pip install -r requirements.txt
```

#### 3단계: 환경 변수 설정

`.env.example` 파일을 `.env`로 복사하고 수정합니다:

```bash
copy .env.example .env
```

`.env` 파일을 텍스트 에디터로 열어서 MSSQL 정보를 수정합니다:

```
MSSQL_SERVER=localhost
MSSQL_DATABASE=EnglishChatDB
MSSQL_USERNAME=sa
MSSQL_PASSWORD=YourPassword123!
```

#### 4단계: 앱 실행

```bash
python app.py
```

## 🌐 앱 접속

브라우저를 열어 `http://localhost:5000` 주소로 접속합니다.

## ⚙️ MSSQL 설정

### MSSQL Server Express 설치 (Windows)

1. [Microsoft SQL Server Express](https://www.microsoft.com/en-us/sql-server/sql-server-express) 다운로드
2. 설치 중 다음 설정 주의:
   - **인스턴스 이름**: SQLEXPRESS (기본값 또는 커스텀)
   - **인증 모드**: SQL Server 인증 + Windows 인증
   - **SA 암호**: 안전한 암호 설정

### ODBC Driver 설치

1. [ODBC Driver 17 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server) 다운로드
2. 설치 완료

### 데이터베이스 생성

SQL Server Management Studio 또는 명령줄에서:

```sql
CREATE DATABASE EnglishChatDB;
```

## 📱 사용법

1. **사용자 이름 입력**: 앱을 실행하면 사용자 이름 입력 모달이 나타납니다.
2. **언어 선택**: 한국어 또는 영어 선택
3. **채팅방 생성**: "+ 새 채팅방 만들기" 버튼 클릭
4. **채팅 시작**: 메시지 입력 후 전송

## 🌍 번역 기능 추가

기본적으로 번역 기능은 비활성화되어 있습니다. 번역을 사용하려면 다음 중 하나를 선택합니다:

### Google Translate API 사용

```bash
pip install google-cloud-translate
```

`.env` 파일에 추가:

```
TRANSLATOR_TYPE=google
GOOGLE_TRANSLATE_API_KEY=your-api-key
```

### Azure Translator 사용

```bash
pip install requests
```

`.env` 파일에 추가:

```
TRANSLATOR_TYPE=azure
AZURE_TRANSLATOR_KEY=your-key
AZURE_TRANSLATOR_ENDPOINT=https://api.cognitive.microsofttranslator.com
```

### 네이버 Papago 사용

`.env` 파일에 추가:

```
TRANSLATOR_TYPE=papago
PAPAGO_CLIENT_ID=your-client-id
PAPAGO_CLIENT_SECRET=your-client-secret
```

그 후 `app.py`의 `translate_text()` 함수를 수정하거나 `translator.py` 모듈을 활용합니다.

## 📁 프로젝트 구조

```
english_chat/
├── app.py              # Flask 메인 앱
├── database.py         # MSSQL 데이터베이스 모듈
├── config.py           # 설정 파일
├── translator.py       # 번역 서비스 모듈
├── requirements.txt    # Python 의존성
├── .env.example        # 환경 변수 템플릿
├── .env                # 실제 환경 변수 (git 무시)
├── setup.bat          # Windows 자동 설치
├── run.bat            # Windows 실행
├── README.md          # 자세한 문서
├── QUICKSTART.md      # 이 파일
├── templates/
│   └── index.html     # HTML 페이지
└── static/
    ├── style.css      # 스타일
    └── script.js      # JavaScript
```

## 🐛 트러블슈팅

### "MSSQL 연결 오류"

- MSSQL Server가 실행 중인지 확인
- `.env` 파일의 연결 정보 확인
- ODBC Driver 설치 확인

### "포트 5000이 이미 사용 중입니다"

```bash
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

또는 `app.py`에서 포트를 변경합니다:

```python
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001)
```

### "WebSocket 연결 오류"

- 방화벽 확인
- 브라우저 콘솔(F12)에서 오류 확인
- 개발자 도구에서 네트워크 탭 확인

## 📚 추가 리소스

- [Flask 공식 문서](https://flask.palletsprojects.com/)
- [Flask-SocketIO](https://python-socketio.readthedocs.io/)
- [pyodbc 문서](https://github.com/mkleehammer/pyodbc/wiki)
- [Socket.IO 클라이언트](https://socket.io/docs/v4/client-api/)

## 💡 팁

- 개발 중에는 `DEBUG=True`로 설정하여 자동 리로드 활용
- 프로덕션 배포 시에는 SECRET_KEY를 변경하세요
- HTTPS 사용 시 SSL 인증서 설정 필요

## 📝 라이선스

MIT License

---

**질문이 있으신가요?** README.md를 참고하거나 이슈를 등록해주세요.
