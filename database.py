import pymssql
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.server = os.getenv('MSSQL_SERVER', 'localhost')
        self.database = os.getenv('MSSQL_DATABASE', 'EnglishChatDB')
        self.username = os.getenv('MSSQL_USERNAME', 'sa')
        self.password = os.getenv('MSSQL_PASSWORD', '')

    def get_connection(self):
        try:
            conn = pymssql.connect(
                server=self.server,
                user=self.username,
                password=self.password,
                database=self.database,
                charset='UTF-8'
            )
            conn.autocommit(True)
            return conn
        except Exception as e:
            print(f'Database connection error: {e}')
            raise

    def init_db(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ChatRooms')
                CREATE TABLE ChatRooms (
                    room_id INT PRIMARY KEY IDENTITY(1,1),
                    room_name NVARCHAR(100) NOT NULL,
                    language NVARCHAR(50) DEFAULT 'Korean',
                    created_at DATETIME DEFAULT GETDATE(),
                    updated_at DATETIME DEFAULT GETDATE()
                )
            ''')

            cursor.execute('''
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Messages')
                CREATE TABLE Messages (
                    message_id INT PRIMARY KEY IDENTITY(1,1),
                    room_id INT NOT NULL,
                    username NVARCHAR(100) NOT NULL,
                    message NVARCHAR(MAX) NOT NULL,
                    language NVARCHAR(50) DEFAULT 'ko',
                    translated NVARCHAR(MAX),
                    created_at DATETIME DEFAULT GETDATE(),
                    FOREIGN KEY (room_id) REFERENCES ChatRooms(room_id) ON DELETE CASCADE
                )
            ''')

            cursor.execute('''
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Users')
                CREATE TABLE Users (
                    user_id INT PRIMARY KEY IDENTITY(1,1),
                    username NVARCHAR(100) NOT NULL UNIQUE,
                    email NVARCHAR(100),
                    created_at DATETIME DEFAULT GETDATE()
                )
            ''')

            cursor.execute('''
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'RoomParticipants')
                CREATE TABLE RoomParticipants (
                    participant_id INT PRIMARY KEY IDENTITY(1,1),
                    room_id INT NOT NULL,
                    username NVARCHAR(100) NOT NULL,
                    joined_at DATETIME DEFAULT GETDATE(),
                    left_at DATETIME,
                    FOREIGN KEY (room_id) REFERENCES ChatRooms(room_id) ON DELETE CASCADE
                )
            ''')

            conn.commit()
            print('Database tables created successfully')
        except Exception as e:
            print(f'Database initialization error: {e}')
            raise

    def get_all_rooms(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT room_id, room_name, language, created_at FROM ChatRooms ORDER BY created_at DESC')
            rooms = []
            for row in cursor.fetchall():
                rooms.append({
                    'room_id': row[0],
                    'room_name': row[1],
                    'language': row[2],
                    'created_at': row[3].isoformat() if row[3] else None
                })
            return rooms
        except Exception as e:
            print(f'Error getting rooms: {e}')
            raise

    def create_room(self, room_name, language='Korean'):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO ChatRooms (room_name, language) VALUES (%s, %s)',
                (room_name, language)
            )
            cursor.execute('SELECT @@IDENTITY')
            room_id = cursor.fetchone()[0]
            return int(room_id)
        except Exception as e:
            print(f'Error creating room: {e}')
            raise

    def delete_room(self, room_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM ChatRooms WHERE room_id = %s', (room_id,))
        except Exception as e:
            print(f'Error deleting room: {e}')
            raise

    def save_message(self, room_id, username, message, language='ko', translated=None):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO Messages (room_id, username, message, language, translated) VALUES (%s, %s, %s, %s, %s)',
                (room_id, username, message, language, translated)
            )
            cursor.execute('SELECT @@IDENTITY')
            message_id = cursor.fetchone()[0]
            return int(message_id)
        except Exception as e:
            print(f'Error saving message: {e}')
            raise

    def get_messages(self, room_id, limit=100):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                f'SELECT TOP {limit} message_id, username, message, language, translated, created_at FROM Messages WHERE room_id = %s ORDER BY created_at DESC',
                (room_id,)
            )
            messages = []
            for row in cursor.fetchall():
                messages.append({
                    'message_id': row[0],
                    'username': row[1],
                    'message': row[2],
                    'language': row[3],
                    'translated': row[4],
                    'created_at': row[5].isoformat() if row[5] else None
                })
            return list(reversed(messages))
        except Exception as e:
            print(f'Error getting messages: {e}')
            raise

    def add_room_participant(self, room_id, username):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO RoomParticipants (room_id, username) VALUES (%s, %s)',
                (room_id, username)
            )
        except Exception as e:
            print(f'Error adding participant: {e}')
            raise

    def remove_room_participant(self, room_id, username):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE RoomParticipants SET left_at = GETDATE() WHERE room_id = %s AND username = %s',
                (room_id, username)
            )
        except Exception as e:
            print(f'Error removing participant: {e}')
            raise
