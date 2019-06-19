#!/usr/bin/python3
#-*- coding: utf-8 -*-

import sys
sys.path.append('../token')

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

class Sheduler():
    
    def __init__(self, _mongo):
        self.bot = telebot.TeleBot(ShedulerToken.token)
        
        self.mongo = _mongo
        
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
            _str += '/add name_event time text - добавить напоминание\n'
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
                
                self.bot.send_message(message.chat.id, 'Привет, ты подключился ко мне. Я бот будильник!')
                self.bot.send_message(message.chat.id, 'Для помощи используй /help')
                
                self.save(message)
            else :
                self.bot.send_message(message.chat.id, 'Ты уже подключен.')
                
                for men in self.mongo.coll.find({"id": message.chat.id}):
                    if not men.get('timezone_offset', None) :
                        self.geoGet(message)
        
        # Добавить напоминание
        @self.bot.message_handler(commands=['add'])
        def get_add(message):
            print('add', message.chat.id)
            
            if not self.mongo.coll.find({"id": message.chat.id}).count() :
                self.save(message)
            
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
                
                for men in self.mongo.coll.find({"id": message.chat.id}):
                    if not men.get('timezone_offset', None) :
                        self.bot.send_message(message.chat.id, 'Передайте свою локацию для уточнения вашей временной зоны')
                    
                    events = men.get('events', [])
                    
                    flag = False
                    # Ищем событие по имени
                    for event in events:
                        print('event', event)
                        if event['name'] == name :
                            event['name'] = name
                            event['time'] = time
                            event['text'] = text
                            event['status'] = True
                            
                            flag = True
                    
                    # Создаем новое событие
                    if flag == False :
                        event = {}
                        event['name'] = name
                        event['time'] = time
                        event['text'] = text
                        event['status'] = True 
                        
                        events.append(event)
                    
                    print(events)
                        
                    self.mongo.coll.update({'id': message.chat.id}, {"$set": {'events': events}})
                
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
            else :
                name = args[1]
            
                for men in self.mongo.coll.find({"id": message.chat.id}):
                    events = men.get('events', [])
                    for event in events:
                        if event['name'] == name :
                            event['status'] = True 
                            self.mongo.coll.update({'id': message.chat.id}, {"$set": {'events': events}})
                            
                            self.bot.send_message(message.chat.id, 'Отправка напоминания {} включена.'.format(name))
                            break
        
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
            else :
                name = args[1]
            
                for men in self.mongo.coll.find({"id": message.chat.id}):
                    events = men.get('events', [])
                    for event in events:
                        if event['name'] == name :
                            event['status'] = False 
                            self.mongo.coll.update({'id': message.chat.id}, {"$set": {'events': events}})
                            
                            self.bot.send_message(message.chat.id, 'Отправка напоминания {} выключена.'.format(name))
                            break
                
        # Список напоминаний пользователя
        @self.bot.message_handler(commands=['events'])
        def get_events(message):
            print('events', message.chat.id)
            
            if not self.mongo.coll.find({"id": message.chat.id}).count() :
                self.bot.send_message(message.chat.id, 'Вы не зарегистрированы.')
                return
            
            for men in self.mongo.coll.find({"id": message.chat.id}):
                events = men.get('events', [])
                _str = "Список событий:\n"
                for event in events:
                    _str += "'{}' Время: '{}' Сообщение: '{}'\n".format(event['name'], event['time'], event['text'])
                    print(event)
                self.bot.send_message(message.chat.id, _str[:-1])
        
        # Удаляем информацию из базы
        @self.bot.message_handler(commands=['del'])
        def get_del(message):
            print('del', message.chat.id)
            
            self.mongo.coll.remove({"id": message.chat.id})
            
            self.bot.send_message(message.chat.id, 'Всего доброго.')
            
            for men in self.mongo.coll.find({"id": message.chat.id}):
                print(men)            
        
        # Локация пользователя
        @self.bot.message_handler(commands=['geo'])
        def get_geo(message):
            print('geo', message.chat.id)
            self.geoGet(message)
    
        # Локация пользователя
        @self.bot.message_handler(content_types=['location'])
        def get_location(message):
            print('location', message.chat.id)
            ##
            #  Берем временную зону пользователя.
            ##
            tz = tzwhere.tzwhere()
            timezone_str = tz.tzNameAt(message.location.latitude, message.location.longitude)            
            
            timezone = pytz.timezone(timezone_str)
            
            #print(timezone, timezone.utcoffset(datetime.datetime.now()))
            timezone_offset = str(timezone.utcoffset(datetime.datetime.now()))
            
            self.mongo.coll.update({"id": message.chat.id}, {"$set": {"latitude": message.location.latitude, "longitude": message.location.longitude, "timezone_offset": timezone_offset}})
            
            self.bot.send_message(message.from_user.id, "Ваше местоположение и временная зона: {} {}".format(timezone_str, timezone_offset))
            
            #for men in self.mongo.coll.find({"id": message.chat.id}):
            #    print(men)
        
        @self.bot.message_handler(commands=['days'])
        def get_days(message):
            print('days', message.chat.id)
            
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('1', '2') #Имена кнопок
            msg = self.bot.reply_to(message, 'Test text', reply_markup=markup)
            self.bot.register_next_step_handler(msg, self.process_step)
            
        @self.bot.message_handler(content_types=['text'])
        def get_text(message):
            print('text', message.chat.id)
            
            if self.mongo.coll.find({"id": message.chat.id}).count() :
                for men in self.mongo.coll.find({"id": message.chat.id}):
                    self.bot.send_message(message.from_user.id, "Привет {}, используй /help ".format(men.get("first_name", '')))
            else :
                self.bot.send_message(message.from_user.id, "Ты ко мне не п        одключен, напиши /start")
          
    def __del__(self):
        self.threadTimer.do_run = False
        self.threadTimer.join()
    
    def process_step(message):
        chat_id = message.chat.id
        print(message.text)
        if message.text == '1':
            pass
        else:
            pass
    
    def run(self):
        self.threadTimer.start()
        
        self.bot.polling(none_stop=True, interval=0)
    
    def save(self, message):
        self.mongo.coll.save({'id': message.chat.id, 'first_name': message.from_user.first_name, 'last_name': message.from_user.last_name, "status": True})
        
        self.geoGet(message)
    
    def geoGet(self, message):
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
        keyboard.add(button_geo)
        self.bot.send_message(message.chat.id, "Привет, нажми на кнопку и передай мне свое местоположение для уточнения твоего времени", reply_markup=keyboard)
    
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
                        
                        if _time == _time_user :
                            self.bot.send_message(men['id'], event['text'])
                
            time.sleep(45)
