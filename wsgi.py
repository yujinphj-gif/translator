"""
Flask 앱의 엔트리 포인트 커스텀 예제
필요에 따라 수정하여 사용할 수 있습니다.
"""

# app.py 대신 wsgi.py 사용하는 경우를 위한 래퍼
from app import app, socketio

if __name__ == '__main__':
    # 프로덕션 환경
    # gunicorn --worker-class eventlet -w 1 wsgi:app
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=False,
        use_reloader=False
    )
