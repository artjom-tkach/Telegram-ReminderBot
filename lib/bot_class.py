import telebot
from telebot import types
# Модуль бота
from lib import database_class
# Модуль базы данных
from lib import scheduler_class
# Модуль scheduler
from lib import config
# Модуль конфига
import time
# Модуль sleep
import re
# Модуль регулярного выражения
import datetime
import pytz
# Модуль даты и времени


class Bot:
    BOT = None
    # Экземляр бота
    DATABASE = None
    # Экземпляр базы данных
    SCHEDULER = None
    # Экземпляр scheduler
    markup = None
    # Клавиатура бота
    userData = {}
    # Сюда будут сохраняться, данные полученные от пользователя

    # Информационные сообщения для бота
    messageRepetitionInterval = 'Добавить новый интервал повторения'
    messageWhatMaterial = '{0} \nКакой материал вы изучили? \nПример: я изучил новые слова. (минимум 5 символов)'
    messageWhatSource = '{0} \nГде находится этот материал? \nПример: в словаре, на 42 странице. (минимум 5 символов)'
    messageWhatStageRepetition = '{0} \nКакую стадию повторения вы завершили? \nЕсли вы только изучили материал, отправьте 0. (от 0 до 8)'
    messageTaskCancel = 'Задача успешно отменена.'
    messageAddRemind = 'Напоминание с интервалом повторения успешно добавлено! (№<b>{0}</b>) \nВаша подпись напоминания: {1}, {2}. \nСледующие напоминание для повторения №<b>{3}</b> прийдет через {4} - {5} в {6} (будет {7} стадия повторения).'
    messageRemind = 'Новое напоминание для повторения №<b>{0}</b>! \nВаша подпись напоминания: {1}, {2}. ({3} стадия повторения) \nКак только вы повторили данный материал, нажмите <b>кнопку</b> подтверждения.'
    messageLastRemind = 'Вы прошли все стадии повторения напоминания №<b>{0}</b>! \nВаша подпись напоминания: {1}, {2}. \nПродолжайте совершенствоваться и учиться чему-то новому, теперь вы не забудете выученный материал.'
    messageRemindConfirm = 'Напоминание <b>№{0}</b> успешно подтверждено. ({1} стадия повторения) \nВаша подпись напоминания: {2}, {3}. \nСледующее напоминание прийдет через {4} - {5} в {6} (будет {7} стадия повторения)'
    messageRemindConfirmAlert = 'Напоминание №{0} подтверждено \n ({1} стадия)'
    messageAddRemindError = 'Произошла ошибка с добавлением напоминания! \nЕсли ошибка повторяется, пожалуйста обратитесь к администратору - @artyom_tk.'
    messageRemindError = 'Новое напоминание для повторения! \nПроизошла ошибка с напоминанием №<b>{0}</b>. \nВаша подпись напоминания: {1}, {2} ({3} стадия повторения). \nПожалуйста, обратитесь к администратору - @artyom_tk.'
    messageRemindConfirmError = 'Произошла ошибка с подтверждением напоминания №{0}. Пожалуйста, попробуйте еще. \nЕсли ошибка повторяется, обратитесь к администратору - @artyom_tk.'
    messageProgramWord = 'Это программное словосочетание. Пожалуйста, укажите другое. (чтобы отменить задание - /cancel)'
    messageCancel = 'Чтобы отменить задание - /cancel'
    welcomeMessage = 'Добро пожаловать, {0.first_name}! Вы можете увидеть, как работает метод <b>повторения изученного нового материала</b>, и сколько процентов выученного материала сохраняется в памяти, с использованием метода повторения немецкого ученого Германа Эббингауза.'
    messageRepetitionScheme = 'Ознакомьтесь со схемой повторения нового материала. Вы должно строго следовать <b>интервалам повторения</b>, чтобы вы смогли запомнить выученный материал навсегда.'
    pathWelcomeImg = 'images/welcome.jpg'
    pathRepetitionScheme = 'images/repetition-scheme.jpg'
    unknownCommand = 'Я еще не решил, что ответить 🤔'
    messageProgramIsNotWorking = 'Бот пока не работает. Попробуйте позже.'

    def __init__(self):
        self.BOT = telebot.TeleBot(config.TOKEN_BOT, parse_mode='HTML')
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
            self.BOT.send_photo(
                message.chat.id,
                open(self.pathWelcomeImg, 'rb'),
                self.welcomeMessage.format(message.from_user),
            )

            self.BOT.send_photo(
                message.chat.id,
                open(self.pathRepetitionScheme, 'rb'),
                self.messageRepetitionScheme,
                reply_markup=self.markup
            )

        # Приветствие пользователя!
        # Отправляем изображения (схема повторения материала)

        @self.BOT.message_handler(content_types=['text'])
        def hanglerMessage(message):
            if message.chat.type == 'private':
                self.isWhatCommand(message)
                # Смотрим, какую команду выполнить

        @self.BOT.callback_query_handler(func=lambda call: True)
        def handlerButton(call):
            try:
                if call.message:
                    if self.isInteger(call.data):
                        sql = "SELECT * FROM reminders WHERE id = %s"
                        data = (call.data,)
                        rows = self.DATABASE.select(sql, data)
                        if rows:
                            array = {}
                            for row in rows:
                                array["id"] = row[0]
                                array["username"] = row[1]
                                array["material"] = row[2]
                                array["source"] = row[3]
                                array["chat_id"] = row[4]
                                array["stage_repetition"] = row[5]
                                array["is_finished"] = row[6]
                                array["created_at"] = row[7]
                                array["next_repetition_at"] = row[8]
                            # Перебираем данные и создаем новый массив
                            minuteNextStageRepetition = self.getMinuteStageRepetition(array['stage_repetition'] + 1)
                            # Проверяем на последнюю стадию
                            if minuteNextStageRepetition is not None:
                                array['next_repetition_at'] = datetime.datetime.now(self.setTimezone()) \
                                                              + datetime.timedelta(minutes=minuteNextStageRepetition)
                                # Получаем дату, следующего напоминания
                                sql = "UPDATE reminders SET next_repetition_at = %s WHERE id = %s"
                                data = (array['next_repetition_at'], array['id'])
                                if self.DATABASE.update(sql, data):
                                    # Записуем в бд новое время напоминания
                                    date = array['next_repetition_at'].strftime('%m.%d.%Y')
                                    time = array['next_repetition_at'].strftime('%H:%M')
                                    timeInterval = self.getTimeIntervalStageRepetition(array['stage_repetition'] + 1)
                                    # Получаем текстовый вид даты (+1)
                                    # Получаем интервал времени словами
                                    self.BOT.delete_message(
                                        chat_id=call.message.chat.id,
                                        message_id=call.message.message_id
                                    )
                                    # Удаляем сообщение
                                    self.BOT.send_message(call.message.chat.id, text=self.messageRemindConfirm.format(
                                        array['id'], array['stage_repetition'], array['material'],
                                        array['source'], timeInterval,
                                        date, time, array['stage_repetition'] + 1
                                        # (+1)
                                    ), reply_markup=None)
                                    self.BOT.answer_callback_query(
                                        callback_query_id=call.id, show_alert=True,
                                        text=self.messageRemindConfirmAlert.format(
                                            array['id'], array['stage_repetition']
                                        ))
                                    # Отправляем сообщения + alert
                                    self.addJob(array)
                                    # Новое напоминание
                                else:
                                    self.BOT.answer_callback_query(
                                        callback_query_id=call.id, show_alert=True,
                                        text=self.messageRemindConfirmError.format(
                                            array['id']
                                        ))
                                #  Показываем ошибку
                            else:
                                self.BOT.delete_message(
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id
                                )
                                self.remindJob(array)
                                # Новое напоминание
                        else:
                            self.BOT.answer_callback_query(
                                callback_query_id=call.id, show_alert=True,
                                text=self.messageRemindConfirmError.format(
                                    call.data
                                ))
                        # Показываем ошибку

                    # Проверка на целое число

            except Exception as e:
                print(repr(e))

            # Ловим исключение

    def setPolling(self):
        try:
            self.BOT.polling(none_stop=True)
        except Exception as e:
            print(e)
            time.sleep(15)

    def checkMessageMaterial(self, message):
        material = self.htmlSpecialChars(message.text)
        isProgramWord = self.isProgramWord(message)
        isCancelWord = self.isCancelWord(message)
        if (len(material) >= 5) and (isProgramWord is False) and (isCancelWord is False):
            self.userData['material'] = material.lower()  # нижний регистр
            # Создания массива userData
            self.sendMessageWhatSource(message)
            # Отправка следующего сообщения
        else:
            if isCancelWord is False:
                self.sendMessageWhatMaterial(message)
        # Получаем материал и проверяем его (проверяем, не запрограммированы ли слова, которые приходят)

    def checkSourceMaterial(self, message):
        source = self.htmlSpecialChars(message.text)
        isProgramWord = self.isProgramWord(message)
        isCancelWord = self.isCancelWord(message)
        if (len(source) >= 5) and (isProgramWord is False) and (isCancelWord is False):
            self.userData['source'] = source.lower()  # нижний регистр
            # Создания массива userData
            self.sendMessageWhatStageRepetition(message)
            # Отправка следующего сообщения
        else:
            if isCancelWord is False:
                self.sendMessageWhatSource(message)
        # Получаем источник и проверяем его (проверяем, не запрограммированы ли слова, которые приходят)

    def checkStageRepetition(self, message):
        arrayStages = {"0", "1", "2", "3", "4", "5", "6", "7", "8"}
        stageRepetition = self.htmlSpecialChars(message.text)
        isProgramWord = self.isProgramWord(message)
        isCancelWord = self.isCancelWord(message)
        if (stageRepetition in arrayStages) and (isProgramWord is False) and (isCancelWord is False):
            stageRepetition = int(stageRepetition)
            self.userData['stage_repetition'] = stageRepetition
            stageRepetition += 1
            # Стадия повторения (+1)
            self.userData['username'] = message.from_user.username
            # логин пользователя
            self.userData['chat_id'] = message.chat.id
            self.userData['created_at'] = datetime.datetime.now(self.setTimezone())
            # Определям текущее время (дата создания)
            self.userData['next_repetition_at'] = self.userData['created_at'] + datetime.timedelta(
                minutes=
                self.getMinuteStageRepetition(stageRepetition))
            # Определяем в какое время, будет следующее напоминание (получаем время, на данной стадии)
            # Создания массива userData
            insertID = self.insertRemind()
            # Добавляем напоминание в базу данных
            if insertID:
                self.userData['id'] = insertID
                # Получаем ID вставленной записи
                date = self.userData['next_repetition_at'].strftime('%m.%d.%Y')
                time = self.userData['next_repetition_at'].strftime('%H:%M')
                # Получаем текстовый вид даты
                timeInterval = self.getTimeIntervalStageRepetition(stageRepetition)
                # Получаем промежуток (через какое время, прийдет напоминание)
                self.BOT.send_message(message.chat.id,
                                      self.messageAddRemind.format(self.userData['id'],
                                                                   self.userData['material'], self.userData['source'],
                                                                   self.userData['id'], timeInterval,
                                                                   date, time,
                                                                   stageRepetition))
                # Отправляем сообщение о новой задаче
                self.addJob(self.userData)
                self.userData = {}
                # Добавляем задачу
                # Очищаем массив
            else:
                self.BOT.send_message(message.chat.id, self.messageAddRemindError)
            # Добавления напоминания в базу данных (проверка, что есть insertID)
        else:
            if isCancelWord is False:
                self.sendMessageWhatStageRepetition(message)

    def sendMessageWhatMaterial(self, message):
        material = self.BOT.send_message(message.chat.id, self.messageWhatMaterial.format(self.messageCancel))
        self.BOT.register_next_step_handler(material, self.checkMessageMaterial)
        # Отправляем сообщение и проверяем ввод данных (материал)

    def sendMessageWhatSource(self, message):
        source = self.BOT.send_message(message.chat.id, self.messageWhatSource.format(self.messageCancel))
        self.BOT.register_next_step_handler(source, self.checkSourceMaterial)
        # Отправляем сообщение и проверяем ввод данных (источник материала)

    def sendMessageWhatStageRepetition(self, message):
        stageRepetition = self.BOT.send_message(message.chat.id,
                                                self.messageWhatStageRepetition.format(self.messageCancel))
        self.BOT.register_next_step_handler(stageRepetition, self.checkStageRepetition)

    def addJob(self, data):
        self.SCHEDULER.scheduler.add_job(self.remindJob, 'date', run_date=data['next_repetition_at'],
                                         args=[data])
        # Добавляем задачу

    def remindJob(self, args):
        minuteNextStageRepetition = self.getMinuteStageRepetition(args['stage_repetition'] + 1)
        isFinished = False
        # Определяем, последнее ли напоминание
        if minuteNextStageRepetition is not None:
            args['stage_repetition'] = args['stage_repetition'] + 1
        else:
            isFinished = True

        args['next_repetition_at'] = None
        sql = "UPDATE reminders SET stage_repetition = %s, is_finished = %s, next_repetition_at = %s WHERE id = %s"
        data = (args['stage_repetition'], isFinished, args['next_repetition_at'], args['id'])
        if self.DATABASE.update(sql, data):
            if isFinished == 0:
                markup = types.InlineKeyboardMarkup(row_width=2)
                button = types.InlineKeyboardButton(
                    "Подтвердить №{0} ({1} стадия)".format(args['id'], args['stage_repetition']),
                    callback_data=args['id'])
                # Создаем кнопку для сообщения
                # Передаем в callback - id напоминания
                markup.add(button)
                self.BOT.send_message(args['chat_id'], self.messageRemind.format(
                    args['id'], args['material'], args['source'],
                    args['stage_repetition']
                ), reply_markup=markup)
                # Отправляем сообщение
            else:
                self.BOT.send_message(args['chat_id'], self.messageLastRemind.format(
                    args['id'], args['material'],
                    args['source']
                ))
        else:
            self.BOT.send_message(args['chat_id'], self.messageRemindError.format(
                args['id'], args['material'],
                args['source'], args['stage_repetition']
            ))

    def insertRemind(self):
        sql = "INSERT INTO reminders (username, material, source, " \
              "chat_id, stage_repetition, created_at, next_repetition_at) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;"
        data = (self.userData['username'], self.userData['material'], self.userData['source'],
                self.userData['chat_id'], self.userData['stage_repetition'],
                self.userData['created_at'], self.userData['next_repetition_at'])
        return self.DATABASE.insert(sql, data)

    # Добавления напоминания в базу данных

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
            # Ошибка - (запрограммированое слово)
        else:
            return False
        return True
        # Узнаем, запрограммировано, ли слово

    def isCancelWord(self, message):
        if message.text == '/cancel':
            self.BOT.send_message(message.chat.id, self.messageTaskCancel)
        else:
            return False
        return True
        # Узнаем, что команда не отмена задачи

    def getMinuteStageRepetition(self, stageRepetition):
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

    def getTimeIntervalStageRepetition(self, stageRepetition):
        return {
            1: '15 минут',
            2: '1 час',
            3: '3 часа',
            4: '1 день',
            5: '2 дня',
            6: '4 дня',
            7: '7 дней',
            8: '14 дней',
            9: '1 месяц'
        }.get(stageRepetition, None)

    def htmlSpecialChars(self, data):
        if isinstance(data, str):
            return re.sub(r'\s+', ' ',
                          data.replace("&", "&amp;").
                          replace('"', "&quot;").
                          replace("<", "&lt;").
                          replace(">", "&gt;"))

        # Экранируем данные

    def isInteger(self, data):
        try:
            int(data)
            return True
        except ValueError:
            return False

    # Проверяем на целое число

    def setTimezone(self):
        return pytz.timezone(config.TIMEZONE)

    def allConnected(self, message):
        if (self.DATABASE.isConnected()) and self.SCHEDULER.error == 0:
            return True
        self.BOT.send_message(message.chat.id, self.messageProgramIsNotWorking)
        return False

        # Проверяем на подлючение, если нет выдаем ошибку
