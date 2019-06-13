#!/usr/bin/python3
#-*- coding: utf-8 -*-

import telebot
import mongo
import SvetaEyesToken

class SvetaEyes():
    
    bot = telebot.TeleBot(SvetaEyesToken.token)
    
    def __init__(self, _mongo):
        self.mongo = _mongo
        
        self.keyboardStart = telebot.types.ReplyKeyboardMarkup()
        self.keyboardStart.row('Подключиться', 'Не подключаться')        
    
    def __del__(self):
        pass
    
    def run(self):
        self.bot.polling(none_stop=True, interval=0)
    
    @bot.message_handler(commands=['start'])
    def get_start(message):
        self.bot.send_message(message.chat.id, 'Привет, ты подключился ко мне.')
        
        self.mongo.coll.save({'id': message.chat.id, 'name': message.user.first_name})
        
        print(message.chat.id, message.user.first_name)
        
    @bot.message_handler(commands=['stop'])
    def get_start(message):
        self.bot.send_message(message.chat.id, 'Привет, ты отключился от меня.')
        self.mongo.coll.remove({"id": message.chat.id})
    
    
    @bot.message_handler(content_types=['text'])
    def get_text(message):
        for men in self.mongo.coll.find({"id": message.chat.id}):
            self.bot.send_message(message.from_user.id, "Привет ", men["name"])
            
            return
        
        self.bot.send_message(message.from_user.id, "Ты ко мне не подключен, напиши /start")
        
        return
    
            
            