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

class SvetaEyes():
    
    def __init__(self, _mongo):
        self.bot = telebot.TeleBot(SvetaEyesToken.token)
        
        self.mongo = _mongo
        
        self.threadTimer = Thread(target=self.send_message, args=("Напоминание!",))
        
        @self.bot.message_handler(commands=['start'])
        def get_start(message):
            if not self.mongo.coll.find({"id": message.chat.id}).count() :
                
                self.bot.send_message(message.chat.id, 'Привет, ты подключился ко мне.')
                self.bot.send_message(message.chat.id, 'Пришли мне свое местоположение, что бы я определил твое время.')
                '''
                args = message.text.split(' ')
                if len(args) == 2 :
                    self.mongo.coll.save({'id': message.chat.id, 'first_name': message.from_user.first_name, 'last_name': message.from_user.last_name, 'time': args[1]})
                elif len(args) > 2 :
                    text = ''
                    for i in range(len(args) - 2) :
                        text += args[i] + ' '
                        
                    self.mongo.coll.save({'id': message.chat.id, 'first_name': message.from_user.first_name, 'last_name': message.from_user.last_name, 'time': args[1], 'text': text})
                    
                    self.bot.send_message(message.chat.id, 'Я буду напоминать тебе каждый день в {}.'.format(args[1]))
                else :
                    self.mongo.coll.save({'id': message.chat.id, 'first_name': message.from_user.first_name, 'last_name': message.from_user.last_name})
                '''
            else :
                self.bot.send_message(message.chat.id, 'Привет, ты уже подключен ко мне.')
            
        @self.bot.message_handler(commands=['stop'])
        def get_start(message):
            self.bot.send_message(message.chat.id, 'Привет, ты отключился от меня.')
            self.mongo.coll.remove({"id": message.chat.id})
        
        @self.bot.message_handler(content_types=['text'])
        def get_text(message):
            if self.mongo.coll.find({"id": message.chat.id}).count() :
                for men in self.mongo.coll.find({"id": message.chat.id}):
                    self.bot.send_message(message.from_user.id, "Привет ", men.get("name", ''))
            else :
                self.bot.send_message(message.from_user.id, "Ты ко мне не подключен, напиши /start")
    
        @self.bot.message_handler(content_types=['location'])
        def get_text(message):
            tz = tzwhere.tzwhere()
            timezone_str = tz.tzNameAt(message.location.latitude, message.location.longitude)            
            
            print(timezone_str)
            
            print(message.location.latitude, message.location.longitude)
                
                
    def __del__(self):
        self.threadTimer.do_run = False
        
        self.threadTimer.join()
        
        pass
    
    def run(self):
        self.threadTimer.start()
        
        self.bot.polling(none_stop=True, interval=0)
        
    def send_message(self, message) :
        
        while True:
        
            for men in self.mongo.coll.find():
                now = datetime.datetime.now()
                
                if men.get('time', '') == (str(now.hour) + ':' + str(now.minute)) :
                    self.bot.send_message(men['id'], men.get('text', message))
                
            time.sleep(59)
            
            
        
    
    
    
            
            