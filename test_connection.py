"""
MSSQL 연결 테스트 스크립트
이 스크립트로 데이터베이스 연결을 확인하세요.
"""

import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

# MSSQL 설정
server = os.getenv('MSSQL_SERVER', 'localhost')
database = os.getenv('MSSQL_DATABASE', 'EnglishChatDB')
driver = os.getenv('MSSQL_DRIVER', '{ODBC Driver 17 for SQL Server}')

print("=" * 60)
print("MSSQL 연결 테스트 (Windows 인증)")
print("=" * 60)
print(f"서버: {server}")
print(f"데이터베이스: {database}")
print(f"드라이버: {driver}")
print()

# 테스트 1: 서버 연결 (데이터베이스 선택하지 않음)
print("[1/3] 서버 연결 테스트...")
try:
    conn_string = f'Driver={driver};Server={server};Trusted_Connection=yes'
    conn = pyodbc.connect(conn_string, timeout=5)
    print("✓ 서버 연결 성공!")
    conn.close()
except Exception as e:
    print(f"✗ 서버 연결 실패:")
    print(f"  {str(e)}")
    print()
    print("해결 방법:")
    print("1. MSSQL Server가 실행 중인지 확인하세요")
    print("   Get-Service MSSQL* | Select Status, Name")
    print()
    print("2. TCP/IP 프로토콜이 활성화되어 있는지 확인하세요")
    print("   Windows 검색 > 'SQL Server Configuration Manager'")
    print("   > 'SQL Server 네트워크 구성' > 'MSSQLSERVER 프로토콜'")
    print("   > 'TCP/IP' 활성화")
    print()
    print("3. MSSQL 서비스 재시작")
    print("   Restart-Service MSSQLSERVER")
    print()
    exit(1)

# 테스트 2: 데이터베이스 생성
print("[2/3] 데이터베이스 생성 테스트...")
try:
    conn_string = f'Driver={driver};Server={server};Trusted_Connection=yes'
    conn = pyodbc.connect(conn_string)
    conn.autocommit = True  # 각 문을 자동 커밋
    cursor = conn.cursor()
    
    # 데이터베이스가 이미 존재하는지 확인
    cursor.execute(f"SELECT name FROM sys.databases WHERE name = '{database}'")
    if cursor.fetchone():
        print(f"✓ 데이터베이스 '{database}' 이미 존재합니다")
    else:
        print(f"✓ 데이터베이스 '{database}' 생성 중...")
        cursor.execute(f"CREATE DATABASE [{database}]")
        print(f"✓ 데이터베이스 '{database}' 생성 완료!")
    
    conn.close()
except Exception as e:
    print(f"✗ 데이터베이스 생성 실패:")
    print(f"  {str(e)}")
    exit(1)

# 테스트 3: 데이터베이스 연결
print("[3/3] 데이터베이스 연결 테스트...")
try:
    conn_string = f'Driver={driver};Server={server};Database={database};Trusted_Connection=yes'
    conn = pyodbc.connect(conn_string)
    print(f"✓ 데이터베이스 '{database}' 연결 성공!")
    
    cursor = conn.cursor()
    cursor.execute("SELECT @@VERSION")
    version = cursor.fetchone()[0]
    print(f"  SQL Server 버전: {version.split(',')[0]}")
    
    conn.close()
except Exception as e:
    print(f"✗ 데이터베이스 연결 실패:")
    print(f"  {str(e)}")
    exit(1)

print()
print("=" * 60)
print("✓ 모든 테스트 통과!")
print("=" * 60)
print()
print("다음 단계:")
print("  1. python app.py 를 실행하세요")
print("  2. 브라우저에서 http://localhost:5000 접속하세요")
