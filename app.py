import os
import re
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime
from database import Database
from deep_translator import GoogleTranslator

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Database 초기화
db = Database()

# 활성 채팅방 저장 (메모리): room_key -> [{username, sid, language}]
active_rooms = {}

LANGUAGE_LABELS = {
    'ko': '한국어',
    'en': '영어',
    'ja': '일본어',
    'tl': '필리핀어',
    'id': '인도네시아어',
    'vi': '베트남어'
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    """모든 채팅방 목록 조회"""
    try:
        rooms = db.get_all_rooms()
        return jsonify({'success': True, 'rooms': rooms})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/rooms', methods=['POST'])
def create_room():
    """새 채팅방 생성"""
    try:
        data = request.json
        room_name = data.get('room_name')
        language = data.get('language', 'Korean')  # Korean or English
        
        if not room_name:
            return jsonify({'success': False, 'error': 'Room name required'}), 400
        
        room_id = db.create_room(room_name, language)
        return jsonify({'success': True, 'room_id': room_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/rooms/<int:room_id>', methods=['DELETE'])
def delete_room(room_id):
    """채팅방 삭제"""
    try:
        db.delete_room(room_id)
        active_rooms.pop(f'room_{room_id}', None)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/rooms/<int:room_id>/messages', methods=['GET'])
def get_messages(room_id):
    """채팅방 메시지 조회 (my_lang 파라미터로 번역 언어 지정)"""
    try:
        my_lang = request.args.get('my_lang', 'ko')
        messages = db.get_messages(room_id)
        for msg in messages:
            src = msg.get('language') or 'auto'
            actual_src = 'ko' if is_korean_text(msg['message']) else src
            try:
                t = translate_text(msg['message'], actual_src, my_lang)
                # 번역 결과가 원문과 같으면 생략
                msg['translated'] = None if (t and t.strip() == msg['message'].strip()) else t
            except Exception:
                msg['translated'] = None
            msg['target_language_code'] = my_lang
            msg['target_language'] = LANGUAGE_LABELS.get(my_lang, my_lang)
        return jsonify({'success': True, 'messages': messages})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/translate', methods=['POST'])
def translate():
    """간단한 번역 API (구글 Translate API 또는 다른 서비스 사용 가능)"""
    try:
        data = request.json
        text = data.get('text')
        target_language = data.get('target_language', 'en')
        
        if not text:
            return jsonify({'success': False, 'error': 'Text required'}), 400
        
        # 실제 번역은 Google Translate API, Azure Translator 등 사용
        # 여기서는 간단한 예제
        translated_text = translate_text(text, target_language)
        
        return jsonify({'success': True, 'translated': translated_text})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# WebSocket 이벤트
@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    print(f'Client disconnected: {sid}')
    for room_key in list(active_rooms.keys()):
        active_rooms[room_key] = [u for u in active_rooms[room_key] if u['sid'] != sid]

@socketio.on('join_room')
def on_join(data):
    """채팅방 입장"""
    room_id = data['room_id']
    username = data['username']
    my_language = data.get('my_language', 'ko')
    print(f'[JOIN] {username} joined room_{room_id} | my_language={my_language}')

    join_room(f'room_{room_id}')

    if f'room_{room_id}' not in active_rooms:
        active_rooms[f'room_{room_id}'] = []

    # 동일 sid 중복 방지
    active_rooms[f'room_{room_id}'] = [u for u in active_rooms[f'room_{room_id}'] if u['sid'] != request.sid]
    active_rooms[f'room_{room_id}'].append({
        'username': username,
        'sid': request.sid,
        'language': my_language
    })

    emit('user_joined', {
        'username': username,
        'message': f'{username}님이 입장했습니다.'
    }, room=f'room_{room_id}')

@socketio.on('leave_room')
def on_leave(data):
    """채팅방 퇴장"""
    room_id = data['room_id']
    username = data['username']
    
    leave_room(f'room_{room_id}')
    
    if f'room_{room_id}' in active_rooms:
        active_rooms[f'room_{room_id}'] = [
            u for u in active_rooms[f'room_{room_id}']
            if u['sid'] != request.sid
        ]
    
    emit('user_left', {
        'username': username,
        'message': f'{username}님이 퇴장했습니다.'
    }, room=f'room_{room_id}')

@socketio.on('send_message')
def on_send_message(data):
    """메시지 전송 - 수신자마다 각자 언어로 번역"""
    room_id = data['room_id']
    username = data['username']
    message = data['message']
    source_language = data.get('language', 'auto')

    room_key = f'room_{room_id}'
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        # DB에는 원문만 저장
        msg_id = db.save_message(room_id, username, message, source_language, None)

        sender_sid = request.sid
        # 보낸 사람이 채팅창에서 선택한 번역 언어 (본인 화면용)
        sender_target_lang = data.get('target_language', 'ko')

        users = active_rooms.get(room_key, [])
        print(f"[MSG] '{message}' | src={source_language} | sender_target={sender_target_lang} | users={[(u['username'], u['language'], u['sid'][:6]) for u in users]}")

        if not users:
            # active_rooms가 비어있으면 socket.io 룸 전체에 기본 번역으로 브로드캐스트
            print(f"[FALLBACK] active_rooms empty, broadcasting to room {room_key}")
            try:
                actual_src = 'ko' if is_korean_text(message) else source_language
                translated = translate_text(message, actual_src, sender_target_lang)
                print(f"[FALLBACK] translated='{translated}'")
                if translated and translated.strip() == message.strip():
                    translated = None
            except Exception as e:
                print(f"[FALLBACK] translation error: {e}")
                translated = None
            socketio.emit('new_message', {
                'id': msg_id,
                'username': username,
                'message': message,
                'language': source_language,
                'translated': translated,
                'target_language_code': sender_target_lang,
                'target_language': LANGUAGE_LABELS.get(sender_target_lang, sender_target_lang),
                'timestamp': timestamp,
                'created_at': timestamp,
            }, to=room_key)
        else:
            for user in users:
                # 본인: 채팅창의 언어 선택(번역언어)으로 번역
                # 상대방: 각자의 my_language로 번역
                if user['sid'] == sender_sid:
                    target_lang = sender_target_lang
                else:
                    target_lang = user.get('language', 'ko')

                try:
                    # 한국어면 명시적으로 'ko'로 지정 (auto 감지 불안정)
                    actual_src = 'ko' if is_korean_text(message) else source_language
                    translated = translate_text(message, actual_src, target_lang)
                    print(f"[TRANS] '{message}' | {actual_src}->{target_lang} | result='{translated}'")
                    # 번역 결과가 원문과 같으면 (같은 언어) 표시 생략
                    if translated and translated.strip() == message.strip():
                        translated = None
                except Exception as e:
                    print(f"[TRANS ERROR] {e}")
                    translated = None

                socketio.emit('new_message', {
                    'id': msg_id,
                    'username': username,
                    'message': message,
                    'language': source_language,
                    'translated': translated,
                    'target_language_code': target_lang,
                    'target_language': LANGUAGE_LABELS.get(target_lang, target_lang),
                    'timestamp': timestamp,
                    'created_at': timestamp,
                }, to=user['sid'])

    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('typing')
def on_typing(data):
    """입력 중 표시"""
    room_id = data['room_id']
    username = data['username']
    
    emit('user_typing', {
        'username': username
    }, room=f'room_{room_id}', skip_sid=request.sid)

def is_korean_text(text):
    korean_pattern = re.compile(r'[가-힣]')
    return bool(korean_pattern.search(text))


def detect_foreign_language(text):
    if re.search(r'[\u3040-\u30ff\u31f0-\u31ff\u4e00-\u9faf]', text):
        return 'ja'
    if re.search(r'[\u0e00-\u0e7f]', text):
        return 'vi'
    return 'auto'


def translate_text(text, source_language, target_language):
    """유진번역을 사용한 번역"""
    print(f"[translate_text] '{text}' | {source_language} -> {target_language}")
    try:
        translator = GoogleTranslator(source=source_language, target=target_language)
        result = translator.translate(text)
        print(f"[translate_text] result='{result}'")
        return result
    except Exception as e:
        print(f"[translate_text] ERROR: {e}")
        return text  # 번역 실패 시 원본 반환

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    db.init_db()
    # Toggle the auto-reloader with the USE_RELOADER environment variable.
    # Accepts: '1', 'true', 'yes' (case-insensitive) to enable; anything else disables.
    use_reloader = os.environ.get('USE_RELOADER', '0').lower() in ('1', 'true', 'yes')
    debug_env = os.environ.get('FLASK_DEBUG', '1').lower()
    debug = debug_env in ('1', 'true', 'yes')
    port = int(os.environ.get('PORT', 5000))
    app.logger.info(f'Running with use_reloader={use_reloader}, debug={debug}, port={port}')
    socketio.run(app, debug=debug, host='0.0.0.0', port=port, use_reloader=use_reloader)
