#!/usr/bin/python3
#-*- coding: utf-8 -*-

import pymongo

class mongo():
    
    conn = None
    db = None
    coll = None
    
    def __init__(self, host = None, port = None):
        # соединяемся с сервером базы данных
        if host and port :
            self.conn = pymongo.MongoClient(host, port)
        else :
            self.conn = pymongo.MongoClient()
            
        # выбираем базу данных
        self.db = self.conn.SvetaEyesDB
            
        # выбираем коллекцию документов
        self.coll = self.db.SvetaEyesColl      
        