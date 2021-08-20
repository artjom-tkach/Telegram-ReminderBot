from lib import config
# Модуль конфига
import mysql.connector
from mysql.connector import Error


# Модули для базы данных

class DataBase:
    config = config.CONFIG_DATABASE
    connection = None
    cursor = None

    def __init__(self):
        self.createСonnection()

    def __del__(self):
        self.closeConnection()

    def createСonnection(self):
        try:
            self.connection = mysql.connector.connect(**self.config)
            self.cursor = self.connection.cursor(dictionary=True)
            # Создание подключения, курсора
        except Error as e:
            print(f"The error '{e}' occurred")

    def isConnected(self):
        if self.connection is not None:
            return self.connection.is_connected()
        return False

    def closeConnection(self):
        if self.connection is not None:
            self.connection.close()
        if self.cursor is not None:
            self.cursor.close()

    def commit(self):
        self.connection.commit()

    def insert(self, sql, data):
        if self.isConnected():
            try:
                self.cursor.execute(sql, data)
                self.commit()
                insertID = self.cursor.lastrowid
                if insertID:
                    return insertID
                # Возвращаем id вставленной записи
            except Error as error:
                print(error)
        return False

    def update(self, sql, data):
        if self.isConnected():
            try:
                self.cursor.execute(sql, data)
                self.commit()
                if self.cursor.rowcount == 1:
                    return True
            except Error as error:
                print(error)
        return False

    def select(self, sql, data):
        if self.isConnected():
            try:
                self.cursor.execute(sql, data)
                fetchAll = self.cursor.fetchall()
                if fetchAll:
                    return fetchAll
            except Error as error:
                print(error)
        return False
