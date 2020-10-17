import telebot
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging


Session = sessionmaker()
db = create_engine('sqlite:///database.db', connect_args={'check_same_thread': False})
Session.configure(bind=db)
session = Session()
bot = telebot.AsyncTeleBot("TOKEN")

