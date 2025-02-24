import sqlite3
import time
from config import DB_NAME

class UserService:
    def __init__(self):
        self.db_name= DB_NAME

    def init(self):  # нициализация таблички пользователей
        connection = sqlite3.connect(self.db_name)
        connection.cursor().execute("""CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_id INTEGER NOT NULL,
        username CHAR,
        created_at INTEGER,
        state CHAR NOT NULL,
        json_data CHAR
        );
        """)
        connection.commit()
        connection.close()

# ЗДЕСЬ БЫЛ chec

    def add(self, user):  # tg_id,username,created_at,state,json_data
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        cursor.execute("""INSERT INTO Users(
        tg_id,username,state,json_data, created_at)
        VALUES(?, ?, ?, ?, ?)  
        """, user.to_model()[:-1]) # срезаем user_id, спецом пихнули его в конец
        connection.commit()
        connection.close()

    def check(self,tg_id):
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(1) FROM Users WHERE tg_id= ?",(tg_id,))
        result = cursor.fetchall()
        connection.close()
        return result[0][0]


    def get(self,tg_id):
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        cursor.execute("SELECT tg_id, username, state, json_data, created_at, user_id FROM Users WHERE tg_id = ? LIMIT 1", (tg_id,))
        result = cursor.fetchall()
        connection.close()
        return UserDto.from_model(result[0])



    def update(self,user): # state + json
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        cursor.execute("UPDATE Users SET tg_id = ?, username = ?, state = ?, json_data = ?, created_at = ? WHERE user_id=?", user.to_model())
        connection.commit()
        connection.close()


class UserDto:
    def __init__(self, tg_id,username,state="start",json_data=None, created_at = None, user_id = None):
        self.tg_id = tg_id
        self.username = username
        if created_at == None:
            created_at = round(time.time())
        self.created_at = created_at
        self.state = state
        self.json_data = json_data
        self.user_id = user_id


    def to_model(self): #для работы с бд для запроса эскуль
        return (self.tg_id, self.username, self.state, self.json_data, self.created_at, self.user_id)

    @staticmethod
    def from_model(row): #принимает то что из базы ряд и возвращает дтошкуу
        return UserDto(row[0],row[1],row[2],row[3],row[4],row[5])