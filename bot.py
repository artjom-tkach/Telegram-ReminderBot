from os import error
import telebot
import config
import database
import re
import datetime
from bs4 import BeautifulSoup
from random import randrange
from telebot import types
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor


def minutes_stage_repetition(next_stage_repetition):
    return {
        1: 1,
        2: 1,
        3: 1,
        4: 1

        # 1: 15,
        # 2: 60,
        # 3: 180,
        # 4: 1440,
        # 5: 2880,
        # 6: 5760,
        # 7: 10080,
        # 8: 20160,
        # 9: 44640
    }.get(next_stage_repetition, None)

def my_job(array):
    global connection
    if database.is_connected(connection) == True: 
        next_stage_repetition = array['stage_repetition'] + 1
        minutes = minutes_stage_repetition(next_stage_repetition)
        cursor = connection.cursor(dictionary=True)
        if(minutes is None): 
            sql = "UPDATE Reminders SET is_finished = %s, next_repetition_at = %s WHERE id = %s"
            val = (1, None, array['id'])
            if database.update(connection, cursor, sql, val) == True:
                bot.send_message(array['chat_id'], 'Новое <b>последние</b> напоминание для повторения! Вы прошли весь алгоритм повторения #<b>' + str(array['id']) + '</b>! Ваша подпись напоминания: ' + array['material'] + ' ' + array['source'] + '. Больше вы не забудите выученный материал.')
            else:
                bot.send_message(array['chat_id'], 'Новое <b>последние</b> напоминание для повторения! Вы прошли весь алгоритм повторения #<b>' + str(array['id']) + '</b>! Ваша подпись напоминания: ' + array['material'] + ' ' + array['source'] + '. Больше вы не забудите выученный материал. Пожалуйста, если вы видите это сообщения, сообщите об этом <b>администратору</b>. Спасибо')
        else:
            next_repetition_at = array['next_repetition_at'] + datetime.timedelta(minutes=minutes)
            sql = "UPDATE Reminders SET stage_repetition = %s, next_repetition_at = %s WHERE id = %s"
            val = (next_stage_repetition, next_repetition_at, array['id'])
            if database.update(connection, cursor, sql, val) == True:
                print('-------------------')
                print("Success!")
                print(array['stage_repetition'])
                print(minutes)
                print(next_repetition_at)
                scheduler.add_job(my_job, 'date', run_date=next_repetition_at, args=[{
                'id': array['id'], 
                'chat_id': array['chat_id'],
                'material': array['material'],
                'source': array['source'],
                'username': array['username'],
                'stage_repetition': next_stage_repetition,
                'next_repetition_at': next_repetition_at
                 }])
                date = next_repetition_at.strftime('%m.%d.%Y')
                time = next_repetition_at.strftime('%H:%M')
                bot.send_message(array['chat_id'], 'Новое напоминание для повторения! Ваша подпись напоминания: ' + array['material'] + ' ' + array['source'] + '. Следующие напоминание для повторения <b>#' + str(array['id']) + '</b> - ' + date + ' в ' + time)
            else:
                print("Failed!")
            # cursor.close()
    else: 
        connection = database.create_connection()
        if database.is_connected(connection) == True:
            next_stage_repetition = array['stage_repetition'] + 1
            minutes = minutes_stage_repetition(next_stage_repetition)
            cursor = connection.cursor(dictionary=True)
            if(minutes is None): 
                sql = "UPDATE Reminders SET is_finished = %s, next_repetition_at = %s WHERE id = %s"
                val = (1, None, array['id'])
                if database.update(connection, cursor, sql, val) == True:
                    bot.send_message(array['chat_id'], 'Новое <b>последние</b> напоминание для повторения! Вы прошли весь алгоритм повторения #<b>' + str(array['id']) + '</b>! Ваша подпись напоминания: ' + array['material'] + ' ' + array['source'] + '. Больше вы не забудите выученный материал.')
                else:
                    bot.send_message(array['chat_id'], 'Новое <b>последние</b> напоминание для повторения! Вы прошли весь алгоритм повторения #<b>' + str(array['id']) + '</b>! Ваша подпись напоминания: ' + array['material'] + ' ' + array['source'] + '. Больше вы не забудите выученный материал. Пожалуйста, если вы видите это сообщения, сообщите об этом <b>администратору</b>. Спасибо')
            else:
                cursor = connection.cursor(dictionary=True)
                next_repetition_at = array['next_repetition_at'] + datetime.timedelta(minutes=minutes)
                sql = "UPDATE Reminders SET stage_repetition = %s, next_repetition_at = %s WHERE id = %s"
                val = (next_stage_repetition, next_repetition_at, array['id'])
                if database.update(connection, cursor, sql, val) == True:
                    print('-------------------')
                    print("Success!")
                    print(array['stage_repetition'])
                    print(minutes)
                    print(next_repetition_at)
                    scheduler.add_job(my_job, 'date', run_date=next_repetition_at, args=[{
                    'id': array['id'], 
                    'chat_id': array['chat_id'],
                    'username': array['username'],
                    'material': array['material'],
                    'source': array['source'],
                    'stage_repetition': next_stage_repetition,
                    'next_repetition_at': next_repetition_at,
                    }])
                    date = next_repetition_at.strftime('%m.%d.%Y')
                    time = next_repetition_at.strftime('%H:%M')
                    print(next_repetition_at)
                    bot.send_message(array['chat_id'], 'Новое напоминание для повторения! Ваша подпись напоминания: ' + array['material'] + ' ' + array['source'] + '. Следующие напоминание для повторения <b>#' + str(array['id']) + '</b> - ' + date + ' в ' + time)
                else:
                    print("Failed!")
                # cursor.close()
        else:
            print("Fail!")
    if database.is_connected(connection):
            connection.close()
    
bot  = telebot.TeleBot(config.TOKEN, parse_mode='HTML')

jobstores = {
    'default': MemoryJobStore()
}
executors = {
       'default': ThreadPoolExecutor(20),
        'processpool': ProcessPoolExecutor(10)
}
job_defaults = {
        'coalesce': True, #The accumulated task only runs once
        'max_instances': 1000, #Support 1000 concurrent instances
        'misfire_grace_time': 600 # 600 seconds task timeout fault tolerance
}
scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults)

# Connect to database
connection = database.create_connection()
# Start scheduler
error_scheduler = 0
try:
    scheduler.start()
    error_scheduler = 0
except SystemExit:
    error_scheduler = 1
    print("Scheduler did not started")
    
remind_info = {}

# Information message
message_button_repetition_interval = 'Добавить новый интервал повторения';
welcome_message = 'Добро пожаловать, {0.first_name}! Вы можете увидеть, как работает метод <b>повторения изученного нового материала</b>, и сколько процентов выученного материала сохраняется в памяти, с использованием метода повторения немецкого ученого Германа Эббингауза.';
message_unknown_command = 'Я еще не решил, что ответить 🤔'
path_to_welcome_img = 'images/welcome.jpg'

# Bot Keyboard
markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
randomB = types.KeyboardButton(message_button_repetition_interval)
markup.add(randomB)

def html_special_chars(array):
    print ('-------------------------------')
    for key in array:
        if isinstance(array[key], datetime.datetime) or isinstance(array[key], int):
            val = array[key]
        else:
            val = re.sub(r'\s+', ' ', BeautifulSoup(array[key], 'html.parser').get_text())
        print(array[key], type(array[key]), key)
        array.update({key : val})
    print ('-------------------------------')

# Bot handler
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_photo(message.chat.id,
    open(path_to_welcome_img, 'rb'),
    welcome_message
    .format(message.from_user), reply_markup=markup
    )

@bot.message_handler(content_types=['text'])

def message_keyboard_button(message):
    if message.chat.type == 'private':
            if message.text == message_button_repetition_interval:
                global connection
                if database.is_connected(connection) == True: 
                    msg = bot.send_message(message.chat.id, 'Какой материал вы изучили? Пример: я изучил новые слова.')
                    bot.register_next_step_handler(msg, get_material)
                else: 
                    connection = database.create_connection()
                    if database.is_connected(connection) == True:
                        msg = bot.send_message(message.chat.id, 'Какой материал вы изучили? Пример: я изучил новые слова.')
                        bot.register_next_step_handler(msg, get_material)
                    else:
                        bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте позже!')
            else:
                bot.send_message(message.chat.id, message_unknown_command)

def get_material(message):
    global connection
    if database.is_connected(connection) == True: 
        remind_info['material'] = message.text;
        msg = bot.send_message(message.chat.id, 'Где вы изучили материал? Пример: в своем словаре, на <b>42</b> странице.')
        bot.register_next_step_handler(msg, get_source)
    else: 
        connection = database.create_connection()
        if database.is_connected(connection) == True:
            remind_info['material'] = message.text;
            msg = bot.send_message(message.chat.id, 'Где вы изучили материал? Пример: в своем словаре, на <b>42</b> странице.')
            bot.register_next_step_handler(msg, get_source)
        else:
            bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте позже!')

def get_source(message):
    global connection
    if database.is_connected(connection) == True: 
        remind_info['source'] = message.text;
        remind_info['username'] = message.from_user.username
        remind_info['stage_repetition'] = 1
        remind_info['next_stage_repetition'] = remind_info['stage_repetition'] + 1
        remind_info['created_at']  = datetime.datetime.now()
        minutes = minutes_stage_repetition(remind_info['next_stage_repetition'])
        remind_info['next_repetition_at'] = remind_info['created_at'] + datetime.timedelta(minutes=minutes)
        html_special_chars(remind_info)
        cursor = connection.cursor(dictionary=True)
        sql = "INSERT INTO Reminders (username, material, source, stage_repetition, created_at, next_repetition_at) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (remind_info['username'], remind_info['material'], remind_info['source'], remind_info['stage_repetition'], remind_info['created_at'], remind_info['next_repetition_at'])
        response = database.insert(connection, cursor, sql, val)
        if isinstance(response, int):
            if error_scheduler == 0:
                remind_info['id'] = response
                scheduler.add_job(my_job, 'date', run_date=remind_info['next_repetition_at'], args=[{
                'id': remind_info['id'], 
                'username': remind_info['username'],
                'material': remind_info['material'],
                'source': remind_info['source'],
                'chat_id': message.chat.id,
                'stage_repetition': remind_info['stage_repetition'],
                'next_repetition_at': remind_info['next_repetition_at']
                 }])
                date = remind_info['next_repetition_at'].strftime('%m.%d.%Y')
                time = remind_info['next_repetition_at'].strftime('%H:%M')
                bot.send_message(message.chat.id, 'Напоминание с интервалом повторения успешно добавлено! Ваша подпись напоминания: ' + remind_info['material'] + ' ' + remind_info['source'] + '. Следующие напоминание для повторения <b>#' + str(remind_info['id']) + '</b> - ' + date + ' в ' + time)
                # bot.send_message(message.chat.id, 'Напоминание с интервалом повторения успешно добавлено!<br>Cтадия повторения: <b>' + str(remind_info['stage_repetition'] + 1) + '</b> состоится в ' + str(remind_info['next_repetition_at']))
            else:
                cursor.execute("DELETE FROM Reminders WHERE id = %s", (response))
                bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте еще!')
            # scheduler.add_job(my_job, 'date', run_date=remind_info['next_repetition_at'], args=[{'int': randrange(10)}])
        else:
             bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте еще!')
    else:
        connection = database.create_connection()
        if database.is_connected(connection) == True:
            remind_info['source'] = message.text;
            remind_info['username'] = message.from_user.username
            remind_info['stage_repetition'] = 1
            remind_info['next_stage_repetition'] = remind_info['stage_repetition'] + 1
            minutes = minutes_stage_repetition(remind_info['next_stage_repetition'])
            remind_info['created_at']  = datetime.datetime.now()
            remind_info['next_repetition_at'] = remind_info['created_at'] + datetime.timedelta(minutes=minutes)
            html_special_chars(remind_info)
            cursor = connection.cursor(dictionary=True)
            sql = "INSERT INTO Reminders (username, material, source, stage_repetition, created_at, next_repetition_at) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (remind_info['username'], remind_info['material'], remind_info['source'], remind_info['stage_repetition'], remind_info['created_at'], remind_info['next_repetition_at'])
            response = database.insert(connection, cursor, sql, val)
            if isinstance(response, int):
                if error_scheduler == 0:
                    remind_info['id'] = response
                    scheduler.add_job(my_job, 'date', run_date=remind_info['next_repetition_at'], args=[{
                    'id': remind_info['id'], 
                    'username': remind_info['username'],
                    'material': remind_info['material'],
                    'source': remind_info['source'],
                    'chat_id': message.chat.id,
                    'stage_repetition': remind_info['stage_repetition'],
                    'next_repetition_at': remind_info['next_repetition_at']
                    }])
                    date = remind_info['next_repetition_at'].strftime('%m.%d.%Y')
                    time = remind_info['next_repetition_at'].strftime('%H:%M')
                    bot.send_message(message.chat.id, 'Напоминание с интервалом повторения успешно добавлено! Ваша подпись напоминания: ' + remind_info['material'] + ' ' + remind_info['source'] + '. Следующие напоминание для повторения <b>#' + str(remind_info['id']) + '</b> - ' + date + ' в ' + time)
                    # bot.send_message(message.chat.id, 'Напоминание с интервалом повторения успешно добавлено!<br>Cтадия повторения: <b>' + str(remind_info['stage_repetition'] + 1) + '</b> состоится в ' + str(remind_info['next_repetition_at']))
                else:
                    cursor.execute("DELETE FROM Reminders WHERE id = %s", (response))
                    bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте еще!')
                # scheduler.add_job(my_job, 'date', run_date=remind_info['next_repetition_at'], args=[{'int': randrange(10)}])
            else:
                bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте еще!')
        # bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте еще!')
        if database.is_connected(connection):
            connection.close()
        # cursor.close()
        # Too working code 
        # cursor = connection.cursor(dictionary=True)
        # current_datetime = datetime.now()
        # sql = "INSERT INTO Reminders (material, source, created_at) VALUES (%s, %s, %s)"
        # val = (remind_info['material'], remind_info['source'], current_datetime)
        # cursor.execute(sql, val)
        # connection.commit()
        # if cursor.rowcount:
        # bot.send_message(message.chat.id, 'Напоминание успешно добавлено!')
        # else:
        # bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте еще!')
        # Too working code 
if database.is_connected(connection):
            connection.close()
# Close database connection
# RUN
bot.polling(none_stop=True)