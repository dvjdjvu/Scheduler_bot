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
import mongo
import SvetaEyesToken
import json
import re

class SvetaEyes():
    
    def __init__(self, _mongo):
        self.bot = telebot.TeleBot(SvetaEyesToken.token)
        
        self.mongo = _mongo
        
        self.threadTimer = Thread(target=self.send_message, args=("Напоминание!",))
        
        for men in self.mongo.coll.find():
            print(men)        
        
        # удаляем все документы коллекции
        #self.mongo.coll.remove({})        
        
        # Регистрация в системе
        @self.bot.message_handler(commands=['start'])
        def get_start(message):
            print('start', message.chat.id)
            
            if not self.mongo.coll.find({"id": message.chat.id}).count() :
                
                self.bot.send_message(message.chat.id, 'Привет, ты подключился ко мне.')
                self.bot.send_message(message.chat.id, 'Пришли мне свое местоположение, что бы я узнал твое время.')
                
                self.save(message)
            else :
                self.bot.send_message(message.chat.id, 'Ты уже подключен.')
                
            for men in self.mongo.coll.find({"id": message.chat.id}):
                print(men)
        
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
                
                
                #self.mongo.coll.update({'id': message.chat.id}, {"$set": {'time': time, 'text': text, "status": True}})
                
                for men in self.mongo.coll.find({"id": message.chat.id}):
                    events = men.get('events', [])
                    
                    flag = False
                    # Ищем событие по имени
                    for event in events:
                        if event['name'] == name :
                            event['time'] = time
                            event['text'] = text
                            event['status'] = True
                            
                            flag = True
                    
                    # Создаем новое событие
                    if flag == False :
                        event = {}
                        event['time'] = time
                        event['text'] = text
                        event['status'] = True 
                        
                        events.append(event)
                    
                    print(events)
                        
                    self.mongo.coll.update({'id': message.chat.id}, {"$set": {'events': events}})
                
            print(self.mongo.coll.find({"id": message.chat.id}).count())
            for men in self.mongo.coll.find({"id": message.chat.id}):
                print(men)
        
        # Прекращаем слать напоминания
        @self.bot.message_handler(commands=['stop'])
        def get_stop(message):
            print('stop', message.chat.id)
            
            if not self.mongo.coll.find({"id": message.chat.id}).count() :
                self.save(message)
                
            self.mongo.coll.update({"id": message.chat.id}, {"$set": {"status": False}})
            
            self.bot.send_message(message.chat.id, 'Отправка напоминаний остановлена.')
            
            for men in self.mongo.coll.find({"id": message.chat.id}):
                print(men)
                
        # Список напоминаний пользователя
        @self.bot.message_handler(commands=['events'])
        def get_stop(message):
            print('events', message.chat.id)
            
            if not self.mongo.coll.find({"id": message.chat.id}).count() :
                self.bot.send_message(message.chat.id, 'Вы не зарегистрированы.')
                return
            
            self.bot.send_message(message.chat.id, 'Список событий:')
            for men in self.mongo.coll.find({"id": message.chat.id}):
                events = men.get('events', [])
                for event in events:
                    print(event)
        
        # Удаляем информацию из базы
        @self.bot.message_handler(commands=['del'])
        def get_del(message):
            print('del', message.chat.id)
            
            self.mongo.coll.remove({"id": message.chat.id})
            
            self.bot.send_message(message.chat.id, 'Всего доброго.')
            
            for men in self.mongo.coll.find({"id": message.chat.id}):
                print(men)            
        
        @self.bot.message_handler(content_types=['text'])
        def get_text(message):
            print('text', message.chat.id)
            
            if self.mongo.coll.find({"id": message.chat.id}).count() :
                for men in self.mongo.coll.find({"id": message.chat.id}):
                    self.bot.send_message(message.from_user.id, "Привет ", men.get("name", ''))
            else :
                self.bot.send_message(message.from_user.id, "Ты ко мне не подключен, напиши /start")
    
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
            
            for men in self.mongo.coll.find({"id": message.chat.id}):
                print(men)            
            
                
    def __del__(self):
        self.threadTimer.do_run = False
        
        self.threadTimer.join()
        
        pass
    
    def run(self):
        self.threadTimer.start()
        
        self.bot.polling(none_stop=True, interval=0)
    
    def save(self, message):
        self.mongo.coll.save({'id': message.chat.id, 'first_name': message.from_user.first_name, 'last_name': message.from_user.last_name, "status": True})
    
    def send_message(self, message) :
        
        return
        
        while True:
        
            for men in self.mongo.coll.find():
                
                time_user = ''
                
                _time = men.get('time', None)
                timezone_offset = men.get('timezone_offset', None)
                #print(men, _time, timezone_offset)
                
                if _time and timezone_offset:
                    now = datetime.datetime.now()
                    
                    time_user = (now + datetime.timedelta(hours=int(timezone_offset.split(':')[0]), minutes=int(timezone_offset.split(':')[1]))).strftime('%H:%M')
                
                    print(now, _time, time_user, timezone_offset)
                    if _time == time_user :
                        self.bot.send_message(men['id'], men.get('text', message))
                
            time.sleep(59)
            
            
        
    
    
    
            
            