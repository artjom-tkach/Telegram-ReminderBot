import telebot
from telebot import types
# Модуль бота
from lib import database_class
# Модуль базы данных
from lib import scheduler_class
# Модуль scheduler
from lib import config
# Модуль конфига
import re
# Модуль регулярного выражения
from bs4 import BeautifulSoup
# Модуль, для удаления специальных символов
import datetime


# Модуль даты и времени

class Bot:
    BOT = None
    # Экземляр бота
    DATABASE = None
    # Экземпляр базы данных
    SCHEDULER = None
    # Экземпляр scheduler
    stageRepetition = 0
    # Текущая стадия повторения
    markup = None
    # Клавиатура бота
    userData = {}
    # Сюда будут сохраняться, данные полученные от пользователя

    # Информационные сообщения для бота
    messageRepetitionInterval = 'Добавить новый интервал повторения'
    messageWhatMaterial = 'Какой материал вы изучили? Пример: я изучил новые слова.'
    messageWhatSource = 'Где находится этот материал? Пример: в словаре, на 42 странице.'
    messageInvalidMaterial = ' (минимум 5 символов)'
    messageInvalidSource = ' (минимум 5 символов)'
    messageTaskCancel = 'Задача успешно отменена.'
    messageAddRemind = 'Напоминание с интервалом повторения успешно добавлено! Ваша подпись напоминания: {0}, {1}. Следующие напоминание для повторения №<b>{2}</b> - {3} в {4}.'
    messageRemind = 'Новое напоминание для повторения №<b>{0}</b>! Ваша подпись напоминания: {1}, {2} ({3} стадия повторения). Следующие напоминание для повторения - {4} в {5}'
    messageLastRemind = 'Новое <b>последние</b> напоминание для повторения! Вы прошли весь алгоритм повторения №<b>{0}</b>! Ваша подпись напоминания: {1}, {2}. Больше вы не забудите выученный <b>материал</b>.'
    messageAddRemindError = 'Произошла ошибка с добавлением напоминания! Если ошибка повторяется, пожалуйста обратитесь к администратору - @artyom_tk.'
    messageRemindError = 'Новое напоминание для повторения! Произошла ошибка с напоминанием №<b>{0}</b>. Ваша подпись напоминания: {1}, {2} ({3} стадия повторения). Пожалуйста, обратитесь к администратору - @artyom_tk.'
    messageProgramWord = 'Это программное словосочетание. Пожалуйста, укажите другое. (чтобы отменить задание - /cancel)'
    welcomeMessage = 'Добро пожаловать, {0.first_name}! Вы можете увидеть, как работает метод <b>повторения изученного нового материала</b>, и сколько процентов выученного материала сохраняется в памяти, с использованием метода повторения немецкого ученого Германа Эббингауза.';
    pathWelcomeImg = 'images/welcome.jpg'
    unknownCommand = 'Я еще не решил, что ответить 🤔'
    messageProgramIsNotWorking = 'Бот пока не работает. Попробуйте позже.'

    def __init__(self):
        self.BOT = telebot.TeleBot(config.TOKEN, parse_mode='HTML')
        self.DATABASE = database_class.DataBase()
        self.SCHEDULER = scheduler_class.Scheduler()

        self.setKeyboard()
        self.setHandler()
        self.setPolling()
        # Подключаем клавиатуру(разметку), handlers, polling для боту

    def setKeyboard(self):
        # Клавиатура(разметка) бота
        self.markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttonRepetitionInterval = types.KeyboardButton(self.messageRepetitionInterval)
        self.markup.add(buttonRepetitionInterval)

    def setHandler(self):
        # Handlers бота
        @self.BOT.message_handler(commands=['start'])
        def welcome(message):
            self.BOT.send_photo(message.chat.id,
                                open(self.pathWelcomeImg, 'rb'),
                                self.welcomeMessage.format(message.from_user),
                                reply_markup=self.markup
                                )

        # Приветствие пользователя!
        @self.BOT.message_handler(content_types=['text'])
        def hanglerMessage(message):
            if message.chat.type == 'private':
                self.isWhatCommand(message)
                # Смотрим, какую команду выполнить

    def checkMessageMaterial(self, message):
        material = self.htmlSpecialChars(message.text)
        isProgramWord = self.isProgramWord(message)
        isCancel = self.isCancel(message)
        if (len(material) >= 5) and (isProgramWord is False) and (isCancel is False):
            self.userData['material'] = material
            # Создания массива userData
            self.sendMessageWhatSource(message)
        else:
            if isCancel is False:
                self.sendMessageWhatMaterial(message, True)
        # Получаем материал и проверяем его (проверяем, не запрограммированы ли слова, которые приходят)

    def checkSourceMaterial(self, message):
        source = self.htmlSpecialChars(message.text)
        isProgramWord = self.isProgramWord(message)
        isCancel = self.isCancel(message)
        if (len(source) >= 5) and (isProgramWord is False) and (isCancel is False):
            self.userData['username'] = message.from_user.username
            self.userData['source'] = source
            self.userData['stage_repetition'] = 1
            # Стадия повторения
            self.userData['created_at'] = datetime.datetime.now()
            # Определям текущее время
            self.userData['next_repetition_at'] = self.userData['created_at'] + datetime.timedelta(
                minutes=
                self.getMinuteNextStageRepetition(self.userData['stage_repetition']))
            # Определяем в какое время, будет следующее напоминание (получаем время, на данной стадии)
            # Создания массива userData
            insertID = self.insertRemind()
            if insertID:
                self.userData['id'] = insertID
                self.userData['chat_id'] = message.chat.id,
                self.userData['chat_id'] = int(self.userData['chat_id'][0])
                date = self.userData['next_repetition_at'].strftime('%m.%d.%Y')
                time = self.userData['next_repetition_at'].strftime('%H:%M')
                # Получаем текстовый вид даты
                self.BOT.send_message(message.chat.id,
                                      self.messageAddRemind.format(self.userData['material'], self.userData['source'],
                                                                   self.userData['id'], date,
                                                                   time))
                # Отправляем сообщение о новой задаче
                self.addJob(self.userData)
                self.userData = {}
                # Добавляем задачу
                # Очищаем массив
            else:
                self.BOT.send_message(message.chat.id, self.messageAddRemindError)

            # Добавления напоминания в базу данных (проверка, что есть insertID)
        else:
            if isCancel is False:
                self.sendMessageWhatSource(message, True)
        # Получаем источник и проверяем его (проверяем, не запрограммированы ли слова, которые приходят)

    def addJob(self, data):
        self.SCHEDULER.scheduler.add_job(self.remindJob, 'date', run_date=data['next_repetition_at'],
                                         args=[data])
        # Добавляем задачу

    def remindJob(self, args):
        minuteNextStageRepetition = self.getMinuteNextStageRepetition(args['stage_repetition'] + 1)
        isFinished = 0
        if minuteNextStageRepetition is None:
            args['next_repetition_at'] = None
            isFinished = 1
        else:
            args['stage_repetition'] = args['stage_repetition'] + 1
            # Добавляем +1 к стадии
            args['next_repetition_at'] = args['next_repetition_at'] + datetime.timedelta(
                minutes=minuteNextStageRepetition)
        # Получаем, сколько времени нужно добавить (в зависимости от стадии, если последняя, записуем NULL)
        sql = "UPDATE Reminders SET stage_repetition = %s, next_repetition_at = %s, is_finished = %s WHERE id = %s"
        data = (args['stage_repetition'], args['next_repetition_at'], isFinished, args['id'])
        if self.DATABASE.update(sql, data):
            if isFinished == 1:
                self.BOT.send_message(args['chat_id'],
                                      self.messageLastRemind.format(args['id'], args['material'],
                                                                    args['source']))
            else:
                date = args['next_repetition_at'].strftime('%m.%d.%Y')
                time = args['next_repetition_at'].strftime('%H:%M')
                self.BOT.send_message(args['chat_id'],
                                      self.messageRemind.format(args['id'], args['material'],
                                                                args['source'], args['stage_repetition'] - 1,
                                                                date, time))
                self.addJob(args)
        else:
            self.BOT.send_message(args['chat_id'],
                                  self.messageRemindError.format(args['id'], args['material'],
                                                                 args['source'], args['stage_repetition'],
                                                                 ))

    def insertRemind(self):
        sql = "INSERT INTO `Reminders` (`username`, `material`, `source`, " \
              "`stage_repetition`, `created_at`, `next_repetition_at`) VALUES (%s, %s, %s, %s, %s, %s)"
        data = (self.userData['username'], self.userData['material'], self.userData['source'],
                self.userData['stage_repetition'],
                self.userData['created_at'], self.userData['next_repetition_at'])
        return self.DATABASE.insert(sql, data)
        # Добавления напоминания в базу данных

    def sendMessageWhatMaterial(self, message, invalid=False):
        invalidMessage = ''
        if invalid:
            invalidMessage = self.messageInvalidMaterial
        material = self.BOT.send_message(message.chat.id, self.messageWhatMaterial + invalidMessage)
        # Если передан invalid параметр, выводим сообщение с ошибкой
        self.BOT.register_next_step_handler(material, self.checkMessageMaterial)

    # Отправляем сообщение

    def sendMessageWhatSource(self, message, invalid=False):
        invalidMessage = ''
        if invalid:
            invalidMessage = self.messageInvalidSource
        # Если передан invalid параметр, выводим сообщение с ошибкой
        material = self.BOT.send_message(message.chat.id, self.messageWhatSource + invalidMessage)
        self.BOT.register_next_step_handler(material, self.checkSourceMaterial)
        # Отправляем сообщение

    def isWhatCommand(self, message):
        if self.allConnected(message):
            if message.text == self.messageRepetitionInterval:
                self.sendMessageWhatMaterial(message)
            # Спрашиваем какой материал изучен
            else:
                self.BOT.send_message(message.chat.id, self.unknownCommand)
                # Неизвестная команда

    def isProgramWord(self, message):
        if message.text == self.messageRepetitionInterval:
            self.BOT.send_message(message.chat.id, self.messageProgramWord)
        else:
            if message.text == '/start':
                self.BOT.send_message(message.chat.id, self.messageProgramWord)
            else:
                return False
        # Узнаем, запрограммировано, ли слово

    def isCancel(self, message):
        if message.text == '/cancel':
            self.BOT.send_message(message.chat.id, self.messageTaskCancel)
        else:
            return False

        # Узнаем, слово, команда?

    def setPolling(self):
        try:
            # self.BOT.polling(none_stop=True)
            self.BOT.polling()
        except Exception as e:
            print(e)
            # time.sleep(15)

    def getMinuteNextStageRepetition(self, stageRepetition):
        return {
            1: 15,
            2: 60,
            3: 180,
            4: 1440,
            5: 2880,
            6: 5760,
            7: 10080,
            8: 20160,
            9: 44640
        }.get(stageRepetition, None)

    def allConnected(self, message):
        if (self.DATABASE.isConnected()) and self.SCHEDULER.error == 0:
            return True
        self.BOT.send_message(message.chat.id, self.messageProgramIsNotWorking)
        return False

    # Проверяем на подлючение, если нет выдаем ошибку

    def htmlSpecialChars(self, data):
        if isinstance(data, str):
            return re.sub(r'\s+', ' ', BeautifulSoup(data, 'html.parser').get_text().strip())
            # Экранируем данные
