import sqlite3
import time
from config import DB_NAME

class NoteService:
    def __init__(self):
        self.db_name = DB_NAME

    def init(self):
        connection = sqlite3.connect(self.db_name)
        connection.cursor().execute("""
CREATE TABLE IF NOT EXISTS Notes (
    note_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    title CHAR(200),
    content CHAR(4500),
    created_at INTEGER NOT NULL,
    updated_at INTEGER,
    is_deleted INTEGER,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE RESTRICT
);
        """)  # note_id CHAR
        connection.commit()
        connection.close()

    def add(self, note_dto):
        connection = sqlite3.connect(self.db_name)
        connection.cursor().execute("""
INSERT INTO Notes(user_id,title,content,created_at, updated_at)
VALUES(?, ?, ?, ?, ?)
        """, note_dto.to_model()[:-1])
        connection.commit()
        connection.close()

    def get_all(self, user_id):
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        cursor.execute("""
            SELECT
                user_id, 
                title, 
                content,
                created_at,
                updated_at,
                note_id
            FROM 
                Notes 
            WHERE 
                (is_deleted IS NULL OR is_deleted = 0)
                AND user_id = ?""", (user_id,))
        data = cursor.fetchall()
        connection.close()
        result = []
        for row in data:
            result.append(NoteDto.from_model(row))
        print(result)
        return result

    def delete(self, note_id,tg_id):
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        cursor.execute('UPDATE Notes SET is_deleted = 1 WHERE note_id=? AND user_id=?', (note_id,tg_id))
        connection.commit()
        connection.close()

    def update(self, note):
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        cursor.execute(
            'UPDATE Notes set user_id = ?, title = ?, content = ?, created_at = ?, updated_at =? WHERE note_id =?',
            note.to_model())
        connection.commit()
        connection.close()

    def get_note(self, note_id):
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        cursor.execute('SELECT user_id, title, content, created_at, updated_at, note_id from Notes WHERE note_id=?',
                       (note_id,))
        data = cursor.fetchall()
        row = data[0]
        note = NoteDto.from_model(row)
        connection.close()
        return note


class NoteDto:
    def __init__(self, user_id, title, content, created_at=None, updated_at=None, note_id=None):
        self.note_id = note_id
        self.user_id = user_id
        self.title = title
        self.content = content
        if created_at == None:
            created_at = round(time.time())
        self.created_at = created_at
        self.updated_at = updated_at

    def to_model(self):  # для работы с бд для запроса эскуль
        return (self.user_id, self.title, self.content, self.created_at, self.updated_at, self.note_id)

    @staticmethod
    def from_model(row):  # принимает шо высрала база
        return NoteDto(row[0], row[1], row[2], row[3], row[4], row[5])


    def print(self):
        print(f"{self.note_id} ({self.title}): {self.content}")

    def print_content(self):
        print(self.content)
