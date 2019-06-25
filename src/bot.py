#!/usr/bin/python3
#-*- coding: utf-8 -*-

import sys
sys.path.append('../token')

import mongo
import pytz
from tzwhere import tzwhere
import datetime
from threading import Thread
import sched, time
import telebot
from telebot import types
import mongo
import ShedulerToken
import json
import re

from telegram.ext import Updater, Filters
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

'''
menu_level = 'main_menu'

main_menu_message = 'Меню:'
events_menu_message = 'Напоминания:'
add_menu_message = 'Введите имя нового напоминания:'
del_menu_message = 'Выберите напоминание которое хотите удалить:'

Mongo = mongo.mongo()

############################# Menu #########################################
def menu_handler(bot, update):
    global menu_level
    menu_level = 'main_menu'
    
    update.message.reply_text(main_menu_message, reply_markup=main_menu_keyboard())

def text_handler(bot, update):
    global menu_level
    print(menu_level, update.message.text)
    if menu_lvel == 'add_menu' :
        bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id, text=add_menu_message)

def main_menu(bot, update):
    global menu_level
    menu_level = 'main_menu'
    query = update.callback_query
    bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id, text=main_menu_message, reply_markup=main_menu_keyboard())

def location_menu(bot, update):
    global menu_level
    print('location_menu')
    menu_level = 'location_menu'

def events_menu(bot, update):
    global menu_level
    menu_level = 'events_menu'
    
    query = update.callback_query
    
    if not Mongo.coll.find({"id": query.message.chat_id}).count() :
        return
    
    for men in Mongo.coll.find({"id": query.message.chat_id}):
        events = men.get('events', [])
        _str = events_menu_message + "\n"
        for event in events:
            _str += "'{}' Время: '{}' Сообщение: '{}'\n".format(event['name'], event['time'], event['text'])
    
    bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id, text=_str, reply_markup=events_menu_keyboard())

def add_menu(bot, update):
    global menu_level
    menu_level = 'add_menu'
    query = update.callback_query
    #bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id, text=add_menu_message, reply_markup=add_menu_keyboard())
    bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id, text=add_menu_message)
    #menu_level = 'add_menu_get_name'

def del_menu(bot, update):
    global menu_level
    menu_level = 'del_menu'
    query = update.callback_query
    
    for men in Mongo.coll.find({"id": query.message.chat_id}):
        events = men.get('events', [])
        _str = events_menu_message + "\n"
        for event in events:
            _str += "'{}' Время: '{}' Сообщение: '{}'\n".format(event['name'], event['time'], event['text'])
    
    bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id, text=del_menu_message, reply_markup=del_menu_keyboard())

def first_submenu(bot, update):
    pass

def second_submenu(bot, update):
    pass

def third_submenu(bot, update):
    pass

############################ Keyboards #########################################
def main_menu_keyboard():
    keyboard = [[InlineKeyboardButton('Ваши напоминания', callback_data='events')],
                [InlineKeyboardButton('Добавить новое', callback_data='add')],
                [InlineKeyboardButton('Удалить', callback_data='del')],
                [InlineKeyboardButton('Передать время', callback_data='location')]]
    return InlineKeyboardMarkup(keyboard)

def events_menu_keyboard():
    keyboard = [[InlineKeyboardButton('Меню', callback_data='main')]]
    return InlineKeyboardMarkup(keyboard)

def add_menu_keyboard():
    keyboard = [[InlineKeyboardButton('Меню', callback_data='main')]]
    return InlineKeyboardMarkup(keyboard)

def del_menu_keyboard():
    keyboard = [[InlineKeyboardButton('Submenu 3-1', callback_data='m3_1')],
                [InlineKeyboardButton('Submenu 3-2', callback_data='m3_2')],
                [InlineKeyboardButton('Меню', callback_data='main')]]
    return InlineKeyboardMarkup(keyboard)

updater = Updater(ShedulerToken.token)

updater.dispatcher.add_handler(CommandHandler(['start', 'menu'], menu_handler))
updater.dispatcher.add_handler(MessageHandler(Filters.text, text_handler))
updater.dispatcher.add_handler(CallbackQueryHandler(main_menu, pattern='main'))
updater.dispatcher.add_handler(CallbackQueryHandler(events_menu, pattern='events'))
updater.dispatcher.add_handler(CallbackQueryHandler(add_menu, pattern='add'))
updater.dispatcher.add_handler(CallbackQueryHandler(del_menu, pattern='del'))
updater.dispatcher.add_handler(CallbackQueryHandler(first_submenu, pattern='m1_1'))
updater.dispatcher.add_handler(CallbackQueryHandler(second_submenu, pattern='m2_1'))
updater.dispatcher.add_handler(CallbackQueryHandler(third_submenu, pattern='m3_1'))
updater.dispatcher.add_handler(CallbackQueryHandler(location_menu, pattern='location'))

updater.start_polling()

'''
class Sheduler():
    
    menu_new_status = ''
    event_new = {}
    
    def __init__(self):
        self.bot = telebot.TeleBot(ShedulerToken.token)
        
        self.mongo = mongo.mongo()
        
        self.threadTimer = Thread(target=self.send_message, args=("Напоминание!",))
        
        for men in self.mongo.coll.find():
            print(men)        
        
        # удаляем все документы коллекции
        #self.mongo.coll.remove({})        
        
        # Помощь
        @self.bot.message_handler(commands=['help'])
        def help(message):
            self.menu_clear()
            
            _str = ''
            _str += '/help - помощь\n'
            _str += '/start - начать работу\n'
            _str += '/add name_event time text - добавить напоминание. Формат времени 16:00\n'
            _str += '/on name_event - включить напоминание\n'
            _str += '/on name_event date_number - включить напоминание в дни недели\n'
            _str += '/off name_event - отключить напоминание\n'
            _str += '/off name_event date_number - выключить напоминание в дни недели\n'
            _str += '/events - список напоминаний\n'
            _str += '/geo - взять локацию, для уточнения времени\n'
            
            _str += '\n'
            _str += '/menu - эксперементальная версия с кнопками управления\n'
            
            self.bot.send_message(message.chat.id, _str)
        
        # Регистрация в системе
        @self.bot.message_handler(commands=['start'])
        def get_start(message):
            self.menu_clear()
            
            print('start', message.chat.id)
            
            if not self.mongo.coll.find({"id": message.chat.id}).count() :
                
                self.bot.send_message(message.chat.id, 'Добро пожаловать! Я бот напоминалка.')
                self.bot.send_message(message.chat.id, 'Для помощи используй /help')
                
                self.new(message)
            #else :
            #    self.bot.send_message(message.chat.id, 'Ты уже подключен.')
                
            #    for men in self.mongo.coll.find({"id": message.chat.id}):
            #        if not men.get('timezone_offset', None) :
            #            self.geoGet(message)
        
        # Добавить напоминание
        @self.bot.message_handler(commands=['add'])
        def get_add(message):
            self.menu_clear()
            
            print('add', message.chat.id)
            
            if not self.mongo.coll.find({"id": message.chat.id}).count() :
                self.new(message)
            
            args = message.text.split(' ')
            print(len(args))
            if len(args) <= 3 :
                self.bot.send_message(message.chat.id, 'Формат команды: /add имя_события время(14:15) напоминание')
            else :
                text = ''
                for i in range(len(args) - 3) :
                    text += args[i + 3] + ' '
                
                name = args[1]
                time = args[2]
                
                # Добавляем новое напоминание.
                self.add(message.chat.id, name, time, text)
                
            print(self.mongo.coll.find({"id": message.chat.id}).count())
            for men in self.mongo.coll.find({"id": message.chat.id}):
                print(men)
        
        # Включаем напоминание по имени.
        @self.bot.message_handler(commands=['on'])
        def get_on(message):
            self.menu_clear()
            
            print('on', message.chat.id)
            
            if not self.mongo.coll.find({"id": message.chat.id}).count() :
                self.bot.send_message(message.chat.id, 'Вы не зарегистрированы.')
                return
                
            args = message.text.split(' ')
            print(len(args))
            if len(args) <= 1 :
                self.bot.send_message(message.chat.id, 'Формат команды: /on имя_события')
            elif len(args) <= 2 :
                name = args[1]
                    
                self.days_on(message.chat.id, name)
            else :
                name = args[1]
            
                for i in range(len(args) - 2) :    
                    self.day_on(message.chat.id, name, args[i + 2])
        
        # Выключаем напоминание по имени.
        @self.bot.message_handler(commands=['off'])
        def get_off(message):
            self.menu_clear()
            
            print('off', message.chat.id)
            
            if not self.mongo.coll.find({"id": message.chat.id}).count() :
                self.bot.send_message(message.chat.id, 'Вы не зарегистрированы.')
                return
                
            args = message.text.split(' ')
            print(len(args))
            if len(args) <= 1 :
                self.bot.send_message(message.chat.id, 'Формат команды: /off имя_события')
            elif len(args) <= 2 :
                name = args[1]
                
                self.days_off(message.chat.id, name)
            else :
                name = args[1]
                
                for i in range(len(args) - 2) :    
                    self.day_off(message.chat.id, name, args[i + 2])
                
        # Список напоминаний пользователя
        @self.bot.message_handler(commands=['events'])
        def get_events(message):
            self.menu_clear()
            
            print('events', message.chat.id)
            self.events(message)
        
        # Удаляем напоминание
        @self.bot.message_handler(commands=['del'])
        def get_del(message):
            self.menu_clear()
            
            print('del', message.chat.id)
            
            if not self.mongo.coll.find({"id": message.chat.id}).count() :
                self.bot.send_message(message.chat.id, 'Вы не зарегистрированы.')
                return
                
            args = message.text.split(' ')
            print(len(args))
            if len(args) <= 1 :
                self.bot.send_message(message.chat.id, 'Формат команды: /off имя_события')
            else :
                name = args[1]
                
                self.del_event(message, name)
                        
        # Локация пользователя
        @self.bot.message_handler(commands=['geo'])
        def get_geo(message):
            self.menu_clear()
            
            print('geo', message.chat.id)
            self.geoGet(message)
    
        @self.bot.message_handler(commands=['days'])
        def get_days(message):
            self.menu_clear()
            
            print('days', message.chat.id)
            
            if not self.mongo.coll.find({"id": message.chat.id}).count() :
                self.bot.send_message(message.chat.id, 'Вы не зарегистрированы.')
                return

            markup = types.InlineKeyboardMarkup()
            
            for men in self.mongo.coll.find({"id": message.chat.id}):
                events = men.get('events', [])
                for event in events:
                    button = types.InlineKeyboardButton(text=event['name'], callback_data=json.dumps({'id': message.chat.id, 't': 'e'}))
                    markup.add(button)
                    
            self.bot.send_message(chat_id=message.chat.id, text='Ваши события', reply_markup=markup)
            #self.bot.register_next_step_handler(message, self.process_step)
            
            
        @self.bot.message_handler(commands=['menu'])
        def menu(message):
            self.menu_clear()
            
            self.menu(message)
        
        @self.bot.callback_query_handler(func=lambda call: True)
        def query_handler(call):
            print(call.data)
            
            data = json.loads(call.data)
            _id = call.message.chat.id
            
            if data['c'] == 'events' :
                self.events(call.message)
            elif data['c'] == 'new' :
                self.bot.send_message(_id, text='Напишите название нового напоминания')
                self.menu_new_status = 'get_name'
            elif data['c'] == 'del' :
                
                name = data.get('name')
                if name :
                    self.del_event(call.message, name)
                
                self.menu_del(call.message)
            elif data['c'] == 'menu' :
                self.menu(call.message)
                    
        
        @self.bot.message_handler(content_types=['text'])
        def get_text(message):
            print('text', message.chat.id, self.menu_new_status)
            
            if self.menu_new_status == 'get_name' :
                self.event_new['name'] = message.text
            
                self.menu_new_status = 'get_time'
                self.bot.send_message(message.chat.id, "Напишите время нового напоминания(формат: 17:15)")
                
                print(self.event_new, self.menu_new_status)
            elif self.menu_new_status == 'get_time' :
                if re.search(r'^\d{2,2}\:\d{2,2}$', message.text):
                    self.event_new['time'] = message.text
                    
                    self.bot.send_message(message.chat.id, "Выберите дни напоминаний")
                    self.menu_new_status = 'get_days'
                else :
                    self.bot.send_message(message.chat.id, "Время {} некорректно".format(message.text))
                    
                print(self.event_new)
            elif self.menu_new_status == 'get_days' :
                
                self.days(message)
                
                #self.event_new = {}
                #self.menu_new_status = ''
                #pass
            else :
                self.bot.send_message(message.from_user.id, "Привет {}, используй /help ".format(men.get("first_name", '')))
                
            '''
            if self.mongo.coll.find({"id": message.chat.id}).count() :
                for men in self.mongo.coll.find({"id": message.chat.id}):
                    self.bot.send_message(message.from_user.id, "Привет {}, используй /help ".format(men.get("first_name", '')))
            else :
                self.bot.send_message(message.from_user.id, "Ты ко мне не подключен, напиши /start")
            '''
          
    def __del__(self):
        self.threadTimer.do_run = False
        self.threadTimer.join()
    
    def menu_clear(self):
        self.event_new = {}
        self.menu_new_status = ''        
    
    def del_event(self, message, name):
        for men in self.mongo.coll.find({"id": message.chat.id}):
            events = men.get('events', [])
            for event in events:
                if event['name'] == name :
                    events.remove(event)
                    self.mongo.coll.update({'id': message.chat.id}, {"$set": {'events': events}})
                    
                    self.bot.send_message(message.chat.id, 'Напоминания {} удалено'.format(name))
                    return
                
        self.bot.send_message(message.chat.id, 'Напоминания {} нет'.format(name))
    
    def events(self, message) :
        if not self.mongo.coll.find({"id": message.chat.id}).count() :
            self.bot.send_message(message.chat.id, 'Вы не зарегистрированы.')
            return
        
        for men in self.mongo.coll.find({"id": message.chat.id}):
            events = men.get('events', [])
            _str = "Список событий:\n"
            for event in events:
                _str += "{}: Время - '{}' Дни - '{}' Сообщение - '{}'\n".format(event['name'], event['time'], event.get('days', ''), event['text'])
                print(event)
                
            self.bot.send_message(message.chat.id, _str[:-1])
    
    def menu(self, message):
        markup = types.InlineKeyboardMarkup()
        button_events = types.InlineKeyboardButton(text='Ваши напоминания', callback_data=json.dumps({'c': 'events'}))
        button_new = types.InlineKeyboardButton(text='Добавить', callback_data=json.dumps({'c': 'new'}))
        button_change = types.InlineKeyboardButton(text='Изменить', callback_data=json.dumps({'c': 'change'}))
        button_del = types.InlineKeyboardButton(text='Удалить', callback_data=json.dumps({'c': 'del'}))

        markup.add(button_events)
        markup.add(button_new)
        markup.add(button_change)
        markup.add(button_del)
        self.bot.send_message(chat_id=message.chat.id, text='Главное меню', reply_markup=markup)
    
    def menu_del_keyb(self, message):
        markup = types.InlineKeyboardMarkup()
        
        for men in self.mongo.coll.find({"id": message.chat.id}):
            events = men.get('events', [])
            for event in events:
                #button = types.InlineKeyboardButton(text=event['name'], callback_data=json.dumps({'id': message.chat.id, 't': 'e'}))
                #markup.add(button)
                button = types.InlineKeyboardButton(text=event['name'], callback_data=json.dumps({'c': 'del', 'name': event['name']}))
                markup.add(button)
        
        button = types.InlineKeyboardButton(text='Меню', callback_data=json.dumps({'c': 'menu'}))
        markup.add(button)
        
        return markup
    
    def menu_del(self, message):              
        #self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text='Выберите напоминание для удаления', reply_markup=self.menu_del_keyb(message))
        self.bot.send_message(chat_id=message.chat.id, text='Выберите напоминание для удаления', reply_markup=self.menu_del_keyb(message))
        
        
    def day_off(self, _id, name, day):                
        for men in self.mongo.coll.find({"id": _id}):
            events = men.get('events', [])
            for event in events:
                if event['name'] == name :
                    event['days'][day] = False
                        
                    self.mongo.coll.update({'id': _id}, {"$set": {'events': events}})
                    
                    self.bot.send_message(_id, 'Отправка напоминания {} в день №{} выключена.'.format(name, day))
                    return
    
    def day_on(self, _id, name, day):
        for men in self.mongo.coll.find({"id": _id}):
            events = men.get('events', [])
            for event in events:
                if event['name'] == name :
                    event['days'][day] = True
                        
                    self.mongo.coll.update({'id': _id}, {"$set": {'events': events}})
                    
                    self.bot.send_message(_id, 'Отправка напоминания {} в день №{} включена.'.format(name, day))
                    return
    
    def days_off(self, _id, name):
        for men in self.mongo.coll.find({"id": _id}):
            events = men.get('events', [])
            for event in events:
                if event['name'] == name :
                    event['status'] = False 
                    self.mongo.coll.update({'id': _id}, {"$set": {'events': events}})
                    
                    self.bot.send_message(_id, 'Отправка напоминания {} выключена.'.format(name))
                    return
    
    def days_on(self, _id, name):
        for men in self.mongo.coll.find({"id": _id}):
            events = men.get('events', [])
            for event in events:
                if event['name'] == name :
                    event['status'] = True 
                    self.mongo.coll.update({'id': _id}, {"$set": {'events': events}})
                    
                    self.bot.send_message(_id, 'Отправка напоминания {} включена.'.format(name))
                    return 
    
    def days(self, message):
        markup = types.InlineKeyboardMarkup()
        button_Monday = types.InlineKeyboardButton(text='Понедельник', callback_data=json.dumps({'c': 'add_day', 'day': 1}))
        button_Tuesday = types.InlineKeyboardButton(text='Вторник', callback_data=json.dumps({'c': 'add_day', 'day': 2}))
        button_Wednesday = types.InlineKeyboardButton(text='Среда', callback_data=json.dumps({'c': 'add_day', 'day': 3}))
        button_Thursday = types.InlineKeyboardButton(text='Четверг', callback_data=json.dumps({'c': 'add_day', 'day': 4}))
        button_Friday = types.InlineKeyboardButton(text='Пятница', callback_data=json.dumps({'c': 'add_day', 'day': 5}))
        button_Saturday = types.InlineKeyboardButton(text='Суббота', callback_data=json.dumps({'c': 'add_day', 'day': 6}))
        button_Sunday = types.InlineKeyboardButton(text='Воскресенье', callback_data=json.dumps({'c': 'add_day', 'day': 7}))
        markup.add(button_Monday, button_Tuesday, button_Wednesday)
        markup.add(button_Thursday, button_Friday)
        markup.add(button_Saturday, button_Sunday)
        self.bot.send_message(chat_id=message.chat.id, text='Выберите дни недели напоминания', reply_markup=markup)
    
    def process_step(self, message):
        chat_id = message.chat.id
        print(message.text)
        if message.text == '1':
            pass
        else:
            pass
        
        #call.data = json.loads(call.data)
        
    def run(self):
        self.threadTimer.start()
        
        self.bot.polling(none_stop=True, interval=0)
    
    def new(self, message):
        self.mongo.coll.save({'id': message.chat.id, 'first_name': message.from_user.first_name, 'last_name': message.from_user.last_name, "status": True})    
        self.geoGet(message)
    
    def add(self, _id, name, time, text):
        for men in self.mongo.coll.find({"id": _id}):
            if not men.get('timezone_offset', None) :
                self.bot.send_message(_id, 'Отправьте своё местоположение для уточнения вашей временной зоны')
                    
            events = men.get('events', [])

            if self.find(events, name) == False :
                # Создаем новое событие
                event = {}
                event['name'] = name
                event['time'] = time
                event['text'] = text
                #event['status'] = True 
                event['days'] = {'1': True, '2': True, '3': True, '4': True, '5': True, '6': True, '7': True}
                        
                events.append(event)
                
                print(events)
            
                self.mongo.coll.update({'id': _id}, {"$set": {'events': events}})                
                self.bot.send_message(_id, 'Напоминание {} добавлено'.format(name))
            else : 
                self.bot.send_message(_id, 'Напоминание {} уже существует'.format(name))
    
    # Поиск события по имени
    def find(self, events, name):
        flag = False
        # Ищем событие по имени
        for event in events:
            print('event', event)
            if event['name'] == name :
                return True
                
        return False
    
    # Включить/выключить день напоминания
    def day_change(self, events, name, day, val = False):
        for event in events:
            if event['name'] == name :
                event['days'][day] = val
                    
        return events
    
    def geoGet(self, message):
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
        keyboard.add(button_geo)
        self.bot.send_message(message.chat.id, "Отправьте своё местоположение для уточнения вашей временной зоны", reply_markup=keyboard)
    
    def send_message(self, message) :
        
        while True:
        
            for men in self.mongo.coll.find():
                timezone_offset = men.get('timezone_offset', None)
                
                events = men.get('events', [])
                for event in events:
                    _time_user = ''
                    _time = event.get('time', None)
                    if _time and timezone_offset:
                        now = datetime.datetime.now()
                
                        if timezone_offset :
                            _time_user = (now + datetime.timedelta(hours=int(timezone_offset.split(':')[0]), minutes=int(timezone_offset.split(':')[1]))).strftime('%H:%M')
                        else :
                            _time_user = _time
                        
                        #print(_time, _time_user)
                        
                        if _time == _time_user and event['status'] and event['days'][str(now.weekday() + 1)] == True:
                            self.bot.send_message(men['id'], event['text'])
                
            time.sleep(45)
            
