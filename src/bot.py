#!/usr/bin/python3
#-*- coding: utf-8 -*-

import sys
sys.path.append('../token')

from threading import Thread
import sched, time
import telebot
import mongo
import SvetaEyesToken

class SvetaEyes():
    
    def __init__(self, _mongo):
        self.bot = telebot.TeleBot(SvetaEyesToken.token)
        
        self.mongo = _mongo
        
        self.keyboardStart = telebot.types.ReplyKeyboardMarkup()
        self.keyboardStart.row('Подключиться', 'Не подключаться')
        
        self.threadTimer = Thread(target=self.send_message, args=("Тренеруй глаза!",))
        
        @self.bot.message_handler(commands=['start'])
        def get_start(message):
            if not self.mongo.coll.find({"id": message.chat.id}).count() :
                
                self.bot.send_message(message.chat.id, 'Привет, ты подключился ко мне.')
            
                #print(message.chat.id, message.from_user.first_name, message.from_user.last_name)
                
                args = message.text.split(' ')
                if len(args) == 2 :
                    self.mongo.coll.save({'id': message.chat.id, 'first_name': message.from_user.first_name, 'last_name': message.from_user.last_name, 'time': args[1]})
                elif len(args) == 3 :
                    self.mongo.coll.save({'id': message.chat.id, 'first_name': message.from_user.first_name, 'last_name': message.from_user.last_name, 'time': args[1], 'text': args[2]})
                else :
                    self.mongo.coll.save({'id': message.chat.id, 'first_name': message.from_user.first_name, 'last_name': message.from_user.last_name})
                
                #print(message.text)
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
                    self.bot.send_message(message.from_user.id, "Привет ", men["name"])
            else :
                self.bot.send_message(message.from_user.id, "Ты ко мне не подключен, напиши /start")
    
    def __del__(self):
        self.threadTimer.do_run = False
        
        self.threadTimer.join()
        
        pass
    
    def run(self):
        self.threadTimer.start()
        
        self.bot.polling(none_stop=True, interval=0)
        
    def send_message(self, message) :
        time.sleep(10)
        
        while True:
        
            for men in self.mongo.coll.find():
                self.bot.send_message(men['id'], men.get('time', 'QQQ'), men.get('text', 'WWW'))
                
            time.sleep(30)
            
            
        
    
    
    
            
            