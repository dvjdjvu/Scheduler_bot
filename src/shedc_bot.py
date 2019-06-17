#!/usr/bin/python3
#-*- coding: utf-8 -*-

import bot
import mongo

if __name__ == "__main__":
    _mongo = mongo.mongo()
    
    bot = bot.Sheduler(_mongo)
    
    bot.run()


