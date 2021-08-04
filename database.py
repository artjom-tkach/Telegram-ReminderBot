import mysql.connector
from mysql.connector import Error

config = {
  'user': 'root',
  'password': 'root',
  'host': 'localhost',
  'unix_socket': '/Applications/MAMP/tmp/mysql/mysql.sock',
  'database': 'reminders',
  'raise_on_warnings': True
}

def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(user = config['user'], password = config['password'], host = config['host'], port=8889, database=config['database'])
    except Error as e:
        print(f"The error '{e}' occurred")
    
    return connection

def insert(connection, cursor, sql, val):
    if is_connected(connection) != False:
        try:
            cursor.execute(sql, val)
            if cursor.lastrowid:
                connection.commit()
                return cursor.lastrowid
            else:
                return False
        except Error as error:
            print(error)
        finally:
            cursor.close()
            if is_connected(connection):
                connection.close()
    else:
        cursor.close()

def update(connection, cursor, sql, val):
    if is_connected(connection) != False:
        try:
            cursor.execute(sql, val)
            if cursor.rowcount == 1:
                connection.commit()
                return True
            else:
                return False
        except Error as error:
            print(error)
        finally:
            cursor.close()
            if is_connected(connection):
                connection.close()
    else:
        cursor.close()


def is_connected(connection):
    if connection != None: 
            if connection.is_connected(): return True
            return False;
    return False;

