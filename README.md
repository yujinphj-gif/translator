# 영어 번역 채팅 애플리케이션

Flask와 MSSQL을 사용하는 실시간 영어 번역 채팅 애플리케이션입니다.

## 기능

- ✅ 실시간 채팅 (WebSocket 기반)
- ✅ 자동 번역 (한국어 ↔ 영어)
- ✅ 다중 채팅방 지원
- ✅ 사용자 입력 표시
- ✅ 메시지 저장 (MSSQL)
- ✅ 반응형 UI (모바일 최적화)
- ✅ 시스템 메시지 (입장/퇴장)

## 설치

### 사전 요구사항

- Python 3.8+
- MSSQL Server (로컬 또는 원격)
- ODBC Driver 17 for SQL Server

### 1단계: 환경 설정

```bash
cd english_chat
```

### 2단계: 가상환경 생성 (권장)

```bash
python -m venv venv
venv\Scripts\activate
```

### 3단계: 의존성 설치

```bash
pip install -r requirements.txt
```

### 4단계: 환경 변수 설정

`.env.example` 파일을 `.env`로 복사하고 MSSQL 연결 정보를 수정하세요:

```bash
cp .env.example .env
```

`.env` 파일 수정:

```
MSSQL_SERVER=localhost
MSSQL_DATABASE=EnglishChatDB
MSSQL_USERNAME=sa
MSSQL_PASSWORD=YourPassword123!
MSSQL_DRIVER={ODBC Driver 17 for SQL Server}
```

### 5단계: 데이터베이스 생성

MSSQL에서 데이터베이스 생성:

```sql
CREATE DATABASE EnglishChatDB;
```

### 6단계: 애플리케이션 실행

```bash
python app.py
```

브라우저에서 `http://localhost:5000` 접속

## 사용법

1. **사용자 이름 입력**: 앱 시작 시 사용자 이름을 입력합니다.
2. **언어 선택**: 한국어 또는 영어를 선택합니다.
3. **채팅방 생성 또는 입장**: 새로운 채팅방을 만들거나 기존 채팅방에 입장합니다.
4. **메시지 전송**: 메시지를 입력하고 전송하면 자동으로 번역됩니다.

## 프로젝트 구조

```
english_chat/
├── app.py                 # Flask 메인 애플리케이션
├── database.py            # MSSQL 데이터베이스 연결 및 쿼리
├── requirements.txt       # Python 의존성
├── .env.example          # 환경 변수 템플릿
├── README.md             # 이 파일
├── templates/
│   └── index.html        # 메인 HTML 페이지
└── static/
    ├── style.css         # 스타일시트
    └── script.js         # 클라이언트 JavaScript
```

## 데이터베이스 스키마

### ChatRooms 테이블
- `room_id`: 채팅방 ID (기본키)
- `room_name`: 채팅방 이름
- `language`: 채팅방 기본 언어
- `created_at`: 생성 시간
- `updated_at`: 수정 시간

### Messages 테이블
- `message_id`: 메시지 ID (기본키)
- `room_id`: 채팅방 ID (외래키)
- `username`: 사용자 이름
- `message`: 메시지 내용
- `language`: 메시지 언어
- `translated`: 번역된 메시지
- `created_at`: 생성 시간

### Users 테이블
- `user_id`: 사용자 ID (기본키)
- `username`: 사용자 이름
- `email`: 이메일
- `created_at`: 생성 시간

### RoomParticipants 테이블
- `participant_id`: 참여자 ID (기본키)
- `room_id`: 채팅방 ID (외래키)
- `username`: 사용자 이름
- `joined_at`: 입장 시간
- `left_at`: 퇴장 시간

## API 엔드포인트

### REST API

- `GET /api/rooms` - 모든 채팅방 조회
- `POST /api/rooms` - 새 채팅방 생성
- `GET /api/rooms/<room_id>/messages` - 채팅방 메시지 조회
- `POST /api/translate` - 텍스트 번역

### WebSocket 이벤트

- `connect` - 서버 연결
- `disconnect` - 서버 연결 해제
- `join_room` - 채팅방 입장
- `leave_room` - 채팅방 퇴장
- `send_message` - 메시지 전송
- `typing` - 사용자가 입력 중
- `new_message` - 새 메시지 수신
- `user_joined` - 사용자 입장
- `user_left` - 사용자 퇴장
- `user_typing` - 사용자 입력 중

## 번역 기능 추가

현재는 메시지를 그대로 반환합니다. 실제 번역을 위해 다음 중 하나를 사용할 수 있습니다:

### Google Translate API

```bash
pip install google-cloud-translate
```

```python
from google.cloud import translate_v2

def translate_text(text, target_language):
    translate_client = translate_v2.Client()
    result = translate_client.translate_text(
        source_language_code='ko' if target_language == 'en' else 'en',
        target_language_code=target_language,
        contents=[text]
    )
    return result['translations'][0]['translatedText']
```

### Azure Translator

```bash
pip install requests
```

```python
import requests

def translate_text(text, target_language):
    key = os.getenv('AZURE_TRANSLATOR_KEY')
    endpoint = os.getenv('AZURE_TRANSLATOR_ENDPOINT')
    
    headers = {
        'Ocp-Apim-Subscription-Key': key,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }
    
    params = {
        'api-version': '3.0',
        'from': 'ko' if target_language == 'en' else 'en',
        'to': target_language
    }
    
    body = [{'text': text}]
    
    request = requests.post(
        endpoint + '/translate',
        params=params,
        headers=headers,
        json=body
    )
    
    response = request.json()
    return response[0]['translations'][0]['text']
```

## 트러블슈팅

### MSSQL 연결 오류

1. MSSQL Server가 실행 중인지 확인하세요.
2. 연결 정보(.env)가 올바른지 확인하세요.
3. ODBC Driver가 설치되어 있는지 확인하세요.

### WebSocket 연결 오류

1. 방화벽에서 포트 5000이 열려있는지 확인하세요.
2. 브라우저 콘솔에서 오류 메시지를 확인하세요.

## 라이선스

MIT License

## 작성자

Your Name
