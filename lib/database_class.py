from lib import config
# Модуль конфига
import psycopg2
from psycopg2 import Error


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
            self.connection = psycopg2.connect(
                dbname=self.config['database'],
                user=self.config['user'],
                password=self.config['password'],
                host=self.config['host'],
                port=self.config['port']
            )
            self.cursor = self.connection.cursor()
            # Создание подключения, курсора
        except Error as e:
            print(f"The error '{e}' occurred")

    def isConnected(self):
        if (self.connection is not None) and (self.cursor is not None):
            return True
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
                insertID = self.cursor.fetchone()[0]
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
