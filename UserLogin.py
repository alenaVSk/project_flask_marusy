import sqlite3
import time
import math
import connect_db as con_db
from flask import flash


def getUser(user_id):  # получение данных по ID пользователя из таблицы users
    conn = con_db.get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT * FROM users WHERE id = {user_id} LIMIT 1")
        res = cur.fetchone()
        conn.close()
        if not res:
            print("Пользователь не найден")
            return False

        return res
    except sqlite3.Error as e:
        print("Ошибка получения данных из БД " + str(e))

    return False


class UserLogin:
    def fromDB(self, user_id):
        self.__user = getUser(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.__user['id'])

    def name_id(self):
        return str(self.__user['name'])

    def email_id(self):
        return str(self.__user['email'])


def getUserByEmail(email):  # получение данных по email пользователя из таблицы users
    conn = con_db.get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT * FROM users WHERE email = '{email}' LIMIT 1")
        res = cur.fetchone()
        conn.close()
        if not res:
            print("Пользователь не найден")
            return False

        return res
    except sqlite3.Error as e:
        print("Ошибка получения данных из БД " + str(e))

        return False


def addUser(name, email, hpsw):  # добавление пользователя в БД по уникальному email
    conn = con_db.get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT COUNT() as `count` FROM users WHERE email LIKE '{email}'")
        res = cur.fetchone()
        if res['count'] > 0:
            flash('Пользователь с таким email уже существует')
            return False

        tm = math.floor(time.time())
        cur.execute('INSERT INTO users VALUES (NULL, ?, ?, ?, ?)', (name, email, hpsw, tm))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        flash('Ошибка добавления пользователя в базу данных '+str(e))
        return False
    return True
