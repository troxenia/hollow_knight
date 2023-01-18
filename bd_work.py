# Импорт библиотеки
import sqlite3


class BdController:
    def __init__(self, name):
        # Подключение к БД
        self.con = sqlite3.connect(name)
        # Создание курсора
        self.cur = self.con.cursor()

    def make_user(self, login, password):
        if not login or not password:
            return False
        if self.cur.execute("""SELECT nick FROM players WHERE nick = ?""", (login, )).fetchone():
            # self.cur.execute("""DELETE FROM players WHERE nick = ?""", (login, ))
            self.cur.execute("""UPDATE players 
SET nick = ?,
    password = ?,
    score = 0,
    levels = '0,0,0,0,0'
WHERE nick = ?""", (login, password, login))
        else:
            self.cur.execute("""INSERT INTO players(nick,password) VALUES(?, ?)""", (login, password))
        self.save_results()
        return True

    def save_results(self):
        self.con.commit()

    def close(self):
        self.con.close()
