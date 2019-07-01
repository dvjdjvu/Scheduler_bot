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
            self.menu_clear(message.chat.id)
            
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
            self.menu_clear(message.chat.id)
            
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
            self.menu_clear(message.chat.id)
            
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
                self.add(message.chat.id, name, time, text, self.event_new['days'])
                
            print(self.mongo.coll.find({"id": message.chat.id}).count())
            for men in self.mongo.coll.find({"id": message.chat.id}):
                print(men)
        
        # Включаем напоминание по имени.
        @self.bot.message_handler(commands=['on'])
        def get_on(message):
            self.menu_clear(message.chat.id)
            
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
            self.menu_clear(message.chat.id)
            
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
            self.menu_clear(message.chat.id)
            
            print('events', message.chat.id)
            self.events(message)
        
        # Удаляем напоминание
        @self.bot.message_handler(commands=['del'])
        def get_del(message):
            self.menu_clear(message.chat.id)
            
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
            self.menu_clear(message.chat.id)
            
            print('geo', message.chat.id)
            self.geoGet(message)
    
        @self.bot.message_handler(commands=['days'])
        def get_days(message):
            self.menu_clear(message.chat.id)
            
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
            
        @self.bot.message_handler(commands=['menu'])
        def menu(message):
            self.menu_clear(message.chat.id)
            
            self.menu(message)
        
        @self.bot.callback_query_handler(func=lambda call: True)
        def query_handler(call):
            print(call.data)
            
            data = json.loads(call.data)
            _id = call.message.chat.id
            
            men = self.mongo.coll.find_one({"id": _id})
            if not men :
                return             
            
            if data['c'] == 'events' :
                self.events(call.message)
            elif data['c'] == 'new' :
                self.bot.send_message(_id, text='Напишите название нового напоминания')
                
                men['event_new']['menu_new_status'] = 'get_name'
                self.mongo.coll.update({'id': _id}, {"$set": {'event_new': men['event_new']}})
                    
            elif data['c'] == 'del' :
                
                name = data.get('name')
                if name :
                    self.del_event(call.message, name)
                
                self.menu_del(call.message)
            elif data['c'] == 'menu' :
                self.menu(call.message)
            elif data['c'] == 'add_day' :                
                men['event_new']['days'][data['day']] = not men['event_new']['days'][data['day']]
                self.mongo.coll.update({'id': _id}, {"$set": {'event_new': men['event_new']}})
                
                self.add(_id, men['event_new']['name'], men['event_new']['time'], men['event_new']['text'], men['event_new']['days'])
                
                self.days(call.message)
            elif data['c'] == 'change' :
                name = data.get('name')
                if name :
                    men['event_new']['name'] = name
                    men['event_new']['menu_new_status'] = 'get_time'
                    self.mongo.coll.update({'id': _id}, {"$set": {'event_new': men['event_new']}})                
                    
                    self.bot.send_message(_id, "Введите время напоминания(формат: 17:15)")
                else:
                    self.menu_change(call.message)
            elif data['c'] == 'geo' :
                self.menu_clear(_id)
                
                print('geo', _id)
                self.geoGet(call.message)                
        
        @self.bot.message_handler(content_types=['text'])
        def get_text(message):
            print('text', message.chat.id)
            
            men = self.mongo.coll.find_one({"id": message.chat.id})
            if not men :
                return
            
            if men['event_new']['menu_new_status'] == 'get_name' :
                men['event_new']['name'] = message.text
                men['event_new']['menu_new_status'] = 'get_time'
                self.mongo.coll.update({'id': message.chat.id}, {"$set": {'event_new': men['event_new']}})                
                
                self.bot.send_message(message.chat.id, "Введите время напоминания(формат: 17:15)")
                
            elif men['event_new']['menu_new_status'] == 'get_time' :
                if re.search(r'^\d{2,2}\:\d{2,2}$', message.text):
                    men['event_new']['time'] = message.text
                    men['event_new']['menu_new_status'] = 'get_text'
                    self.mongo.coll.update({'id': message.chat.id}, {"$set": {'event_new': men['event_new']}})
                    
                    self.bot.send_message(message.chat.id, "Напишите текст напоминания")
                    
                else :
                    self.bot.send_message(message.chat.id, "Время {} некорректно".format(message.text))
                    
            elif men['event_new']['menu_new_status'] == 'get_text' :
                men['event_new']['text'] = message.text
                men['event_new']['menu_new_status'] = ''
                self.mongo.coll.update({'id': message.chat.id}, {"$set": {'event_new': men['event_new']}})
                
                self.add(message.chat.id, men['event_new']['name'], men['event_new']['time'], men['event_new']['text'], men['event_new']['days'])
                
                self.days(message)
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
    
    def menu_clear(self, _id):
        men = self.mongo.coll.find_one({"id": _id})
        if men :
            event_new = {}
            event_new['days'] = {'1': True, '2': True, '3': True, '4': True, '5': True, '6': True, '7': True}
            menu_new_status = ''
                        
            self.mongo.coll.update({'id': _id}, {"$set": {'event_new': event_new, 'menu_new_status': menu_new_status}})
            
        
    
    def del_event(self, message, name):
        men = self.mongo.coll.find_one({"id": message.chat.id})
        if men :
            events = men.get('events', [])
            for event in events:
                if event['name'] == name :
                    events.remove(event)
                    self.mongo.coll.update({'id': message.chat.id}, {"$set": {'events': events}})
                    
                    #self.bot.send_message(message.chat.id, 'Напоминания {} удалено'.format(name))
                    self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text='Напоминания {} удалено'.format(name))#, reply_markup=markup)
                    return
                
        #self.bot.send_message(message.chat.id, 'Напоминания {} нет'.format(name))
        self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text='Напоминания {} нет'.format(name))#, reply_markup=markup)
    
    def events(self, message) :
        markup = types.InlineKeyboardMarkup()
        markup.add(self.menu_button())
        
        men = self.mongo.coll.find_one({"id": message.chat.id})
        if men :
            events = men.get('events', [])
            if len(events) == 0 :
                self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text='У вас нет напоминаний', reply_markup=markup)
                return
                
            _str = "Список напоминаний:\n"
            for event in events:
                _str += "Напоминание {}: в - '{}' по - '{}'\n".format(event['name'], event['time'], self.event_day_str(event.get('days', '')))
                print(event)
                
            self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=_str[:-1], reply_markup=markup)
        else :
            self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text='Вы не зарегистрированы', reply_markup=markup)
            #self.bot.send_message(message.chat.id, 'Вы не зарегистрированы')
    
    def event_day_str(self, days):
        _str = ''
        for day, v in days.items():
            if v == True :
                if day == '1' :
                    _str += 'Пн'
                elif day == '2' :
                    _str += 'Вт'
                elif day == '3' :
                    _str += 'Ср'
                elif day == '4' :
                    _str += 'Чт'
                elif day == '5' :
                    _str += 'Пт'
                elif day == '6' :
                    _str += 'Сб'
                elif day == '7' :
                    _str += 'Вс'
                    
                _str += ' '
                
        return _str
    
    def menu(self, message):
        men = self.mongo.coll.find_one({"id": message.chat.id})
        if men :
            if not men.get('timezone_offset', None) :
                self.bot.send_message(message.chat.id, 'Отправьте своё местоположение для уточнения вашей временной зоны')
        
        markup = types.InlineKeyboardMarkup()
        button_events = types.InlineKeyboardButton(text='Ваши напоминания', callback_data=json.dumps({'c': 'events'}))
        button_new = types.InlineKeyboardButton(text='Добавить', callback_data=json.dumps({'c': 'new'}))
        button_change = types.InlineKeyboardButton(text='Изменить', callback_data=json.dumps({'c': 'change'}))
        button_del = types.InlineKeyboardButton(text='Удалить', callback_data=json.dumps({'c': 'del'}))
        button_del = types.InlineKeyboardButton(text='Уточнить время', callback_data=json.dumps({'c': 'geo'}))

        markup.add(button_events)
        markup.add(button_new)
        markup.add(button_change)
        markup.add(button_del)
        
        print('message.message_id', message.message_id)
        
        try :
            self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text='Главное меню', reply_markup=markup)
        except Exception as e :
            self.bot.send_message(chat_id=message.chat.id, text='Главное меню', reply_markup=markup)
    
    def menu_button(self) :
        return types.InlineKeyboardButton(text='Меню', callback_data=json.dumps({'c': 'menu'}))
    
    def menu_events_keyb(self, message, event_text):
        markup = types.InlineKeyboardMarkup()
        
        men = self.mongo.coll.find_one({"id": message.chat.id})
        if men :
            events = men.get('events', [])
            for event in events:
                button = types.InlineKeyboardButton(text=event['name'], callback_data=json.dumps({'c': event_text, 'name': event['name']}))
                markup.add(button)
        
        markup.add(self.menu_button())
        
        return markup
    
    def menu_del(self, message):              
        self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, 
                                   text='Выберите напоминание для удаления', reply_markup=self.menu_events_keyb(message, 'del'))

    def menu_change(self, message):              
        self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, 
                                   text='Выберите напоминание для редактирования', reply_markup=self.menu_events_keyb(message, 'change'))
        
    def day_off(self, _id, name, day):                
        men = self.mongo.coll.find_one({"id": _id})
        if men :
            events = men.get('events', [])
            for event in events:
                if event['name'] == name :
                    event['days'][day] = False
                        
                    self.mongo.coll.update({'id': _id}, {"$set": {'events': events}})
                    
                    self.bot.send_message(_id, 'Отправка напоминания {} в день №{} выключена.'.format(name, day))
                    return
    
    def day_on(self, _id, name, day):
        men = self.mongo.coll.find_one({"id": _id})
        if men :
            events = men.get('events', [])
            for event in events:
                if event['name'] == name :
                    event['days'][day] = True
                        
                    self.mongo.coll.update({'id': _id}, {"$set": {'events': events}})
                    
                    self.bot.send_message(_id, 'Отправка напоминания {} в день №{} включена.'.format(name, day))
                    return
    
    def days_off(self, _id, name):
        men = self.mongo.coll.find_one({"id": _id})
        if men :
            events = men.get('events', [])
            for event in events:
                if event['name'] == name :
                    event['status'] = False 
                    self.mongo.coll.update({'id': _id}, {"$set": {'events': events}})
                    
                    self.bot.send_message(_id, 'Отправка напоминания {} выключена.'.format(name))
                    return
    
    def days_on(self, _id, name):
        men = self.mongo.coll.find_one({"id": _id})
        if men :
            events = men.get('events', [])
            for event in events:
                if event['name'] == name :
                    event['status'] = True 
                    self.mongo.coll.update({'id': _id}, {"$set": {'events': events}})
                    
                    self.bot.send_message(_id, 'Отправка напоминания {} включена.'.format(name))
                    return 
    
    def days(self, message):
        men = self.mongo.coll.find_one({"id": message.chat.id})
        if not men :
            return
        
        markup = types.InlineKeyboardMarkup()
        button_Monday = types.InlineKeyboardButton(text='Понедельник', callback_data=json.dumps({'c': 'add_day', 'day': '1'}))
        button_Tuesday = types.InlineKeyboardButton(text='Вторник', callback_data=json.dumps({'c': 'add_day', 'day': '2'}))
        button_Wednesday = types.InlineKeyboardButton(text='Среда', callback_data=json.dumps({'c': 'add_day', 'day': '3'}))
        button_Thursday = types.InlineKeyboardButton(text='Четверг', callback_data=json.dumps({'c': 'add_day', 'day': '4'}))
        button_Friday = types.InlineKeyboardButton(text='Пятница', callback_data=json.dumps({'c': 'add_day', 'day': '5'}))
        button_Saturday = types.InlineKeyboardButton(text='Суббота', callback_data=json.dumps({'c': 'add_day', 'day': '6'}))
        button_Sunday = types.InlineKeyboardButton(text='Воскресенье', callback_data=json.dumps({'c': 'add_day', 'day': '7'}))
        
        button_Monday_check = types.InlineKeyboardButton(text=str(men['event_new']['days']['1']), callback_data=json.dumps({'c': 'add_day', 'day': '1'}))
        button_Tuesday_check = types.InlineKeyboardButton(text=str(men['event_new']['days']['2']), callback_data=json.dumps({'c': 'add_day', 'day': '2'}))
        button_Wednesday_check = types.InlineKeyboardButton(text=str(men['event_new']['days']['3']), callback_data=json.dumps({'c': 'add_day', 'day': '3'}))
        button_Thursday_check = types.InlineKeyboardButton(text=str(men['event_new']['days']['4']), callback_data=json.dumps({'c': 'add_day', 'day': '4'}))
        button_Friday_check = types.InlineKeyboardButton(text=str(men['event_new']['days']['5']), callback_data=json.dumps({'c': 'add_day', 'day': '5'}))
        button_Saturday_check = types.InlineKeyboardButton(text=str(men['event_new']['days']['6']), callback_data=json.dumps({'c': 'add_day', 'day': '6'}))
        button_Sunday_check = types.InlineKeyboardButton(text=str(men['event_new']['days']['7']), callback_data=json.dumps({'c': 'add_day', 'day': '7'}))
        
        markup.add(button_Monday, button_Monday_check)
        markup.add(button_Tuesday, button_Tuesday_check)
        markup.add(button_Wednesday, button_Wednesday_check)
        markup.add(button_Thursday, button_Thursday_check)
        markup.add(button_Friday, button_Friday_check)
        markup.add(button_Saturday, button_Saturday_check)
        markup.add(button_Sunday, button_Sunday_check)
        
        markup.add(self.menu_button())
        
        try :
            self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text='Выберите дни напоминаний', reply_markup=markup)
        except Exception as e :
            self.bot.send_message(chat_id=message.chat.id, text='Выберите дни напоминаний', reply_markup=markup)
        
    def run(self):
        self.threadTimer.start()
        
        self.bot.polling(none_stop=True, interval=0)
    
    def new(self, message):
        
        self.mongo.coll.save({'id': message.chat.id, 
                              'first_name': message.from_user.first_name, 
                              'last_name': message.from_user.last_name, 
                              'status': True,
                              'menu_new_status': '',
                              'event_new': {}})    
        self.geoGet(message)
    
    def add(self, _id, name, time, text, days = {}):
        men = self.mongo.coll.find_one({"id": _id})
        if men :    
            events = men.get('events', [])

            if self.find(events, name) == False :
                # Создаем новое событие
                event = {}
                event['name'] = name
                event['time'] = time
                event['text'] = text
                event['days'] = days
                #event['status'] = True 
                        
                events.append(event)
                
                print(events)
            
                self.mongo.coll.update({'id': _id}, {"$set": {'events': events}})
                self.bot.send_message(_id, 'Напоминание {} добавлено'.format(name))
            else : 
                for event in events:
                    if event['name'] == name :
                        event['name'] = name
                        event['time'] = time
                        event['text'] = text
                        event['days'] = days
                        #event['status'] = True                        
                                      
                        self.mongo.coll.update({'id': _id}, {"$set": {'events': events}})
                        #self.bot.send_message(_id, 'Напоминание {} уже существует'.format(name))
    
    # Поиск события по имени
    def find(self, events, name):
        flag = False
        # Ищем событие по имени
        for event in events:
            #print('event', event)
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
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
        markup.add(button_geo)
        
        #self.bot.send_message(message.chat.id, "Отправьте своё местоположение для уточнения вашей временной зоны", reply_markup=markup)
        
        try :
            self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text='Отправьте своё местоположение для уточнения вашей временной зоны', reply_markup=markup)
        except Exception as e :
            self.bot.send_message(message.chat.id, "Отправьте своё местоположение для уточнения вашей временной зоны", reply_markup=markup)
    
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
                        
                        if _time == _time_user and event.get('status', True) and event['days'][str(now.weekday() + 1)] == True:
                            self.bot.send_message(men['id'], event['text'])
                
            time.sleep(45)
            
