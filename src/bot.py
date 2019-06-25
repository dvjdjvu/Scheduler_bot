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
            _str = ''
            _str += '/help - помощь\n'
            _str += '/start - начать работу\n'
            _str += '/add name_event time text - добавить напоминание. Формат времени 16:00\n'
            _str += '/on name_event - включить напоминание\n'
            _str += '/off name_event - отключить напоминание\n'
            _str += '/events - список напоминаний\n'
            _str += '/geo - взять локацию, для уточнения времени\n'
            
            self.bot.send_message(message.chat.id, _str)
        
        # Регистрация в системе
        @self.bot.message_handler(commands=['start'])
        def get_start(message):
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
            print('events', message.chat.id)
            self.events(message)
        
        # Удаляем напоминание
        @self.bot.message_handler(commands=['del'])
        def get_del(message):
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
            
                for men in self.mongo.coll.find({"id": message.chat.id}):
                    events = men.get('events', [])
                    for event in events:
                        if event['name'] == name :
                            events.remove(event)
                            self.mongo.coll.update({'id': message.chat.id}, {"$set": {'events': events}})
                            
                            self.bot.send_message(message.chat.id, 'Напоминания {} удалено'.format(name))
                            return
                        
                self.bot.send_message(message.chat.id, 'Напоминания {} нет'.format(name))
                        
                        
        # Локация пользователя
        @self.bot.message_handler(commands=['geo'])
        def get_geo(message):
            print('geo', message.chat.id)
            self.geoGet(message)
    
        @self.bot.message_handler(commands=['days'])
        def get_days(message):
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
            self.menu(message)
        
        @self.bot.callback_query_handler(func=lambda call: True)
        def query_handler(call):
            print(call.data)
            
            data = json.load(call.data)
            _id = call.message.chat.id
            
            if data['c'] == 'events' :
                self.events(call.message)
            elif data['c'] == 'new' :
                #self.bot.send_message(_id, text='Выберите дни напоминаний', reply_markup=markup)
                pass
            elif data['c'] == 'del' :
                self.menu_del(call.message)
            
                
        
        @self.bot.message_handler(content_types=['text'])
        def get_text(message):
            print('text', message.chat.id)
            
            if self.mongo.coll.find({"id": message.chat.id}).count() :
                for men in self.mongo.coll.find({"id": message.chat.id}):
                    self.bot.send_message(message.from_user.id, "Привет {}, используй /help ".format(men.get("first_name", '')))
            else :
                self.bot.send_message(message.from_user.id, "Ты ко мне не подключен, напиши /start")
          
    def __del__(self):
        self.threadTimer.do_run = False
        self.threadTimer.join()
    
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
        button_new = types.InlineKeyboardButton(text='Добавить новое', callback_data=json.dumps({'c': 'new'}))
        button_del = types.InlineKeyboardButton(text='Удалить', callback_data=json.dumps({'c': 'del'}))

        markup.add(button_events)
        markup.add(button_new)
        markup.add(button_del)
        self.bot.send_message(chat_id=message.chat.id, text='Выберите дни напоминаний', reply_markup=markup)
    
    def menu_del_keyb(self, message):
        markup = types.InlineKeyboardMarkup()
        
        for men in self.mongo.coll.find({"id": message.chat.id}):
            events = men.get('events', [])
            for event in events:
                #button = types.InlineKeyboardButton(text=event['name'], callback_data=json.dumps({'id': message.chat.id, 't': 'e'}))
                #markup.add(button)
                button = types.InlineKeyboardButton(text=event['name'], callback_data=json.dumps({'c': 'del', 'name': event['name']}))
                markup.add(button)
                
        return markup
    
    def menu_del(self, message):              
        self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text='Выберите напоминание для удаления', reply_markup=menu_del_keyb())
        #self.bot.send_message(chat_id=message.chat.id, text='Выберите напоминание для удаления', reply_markup=markup)
        
        
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
                    event['days'][day] = False
                        
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
                    event['status'] = False 
                    self.mongo.coll.update({'id': _id}, {"$set": {'events': events}})
                    
                    self.bot.send_message(_id, 'Отправка напоминания {} включена.'.format(name))
                    return 
    
    def days(self):
        markup = types.InlineKeyboardMarkup()
        button_Monday = types.InlineKeyboardButton(text='Понедельник', callback_data='Понедельник')
        button_Tuesday = types.InlineKeyboardButton(text='Вторник', callback_data='Вторник')
        button_Wednesday = types.InlineKeyboardButton(text='Среда', callback_data='Среда')
        button_Thursday = types.InlineKeyboardButton(text='Четверг', callback_data='Четверг')
        button_Friday = types.InlineKeyboardButton(text='Пятница', callback_data='Пятница')
        button_Saturday = types.InlineKeyboardButton(text='Суббота', callback_data='Суббота')
        button_Sunday = types.InlineKeyboardButton(text='Воскресенье', callback_data='Воскресенье')
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
            
