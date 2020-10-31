from contextlib import contextmanager

import telebot
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# import logging
# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    Session = sessionmaker()
    db = create_engine('sqlite:///database.db', connect_args={'check_same_thread': False})
    Session.configure(bind=db)
    session = Session()

    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()



Session = sessionmaker()
db = create_engine('sqlite:///database.db', connect_args={'check_same_thread': False})
Session.configure(bind=db)
session = Session
bot = telebot.AsyncTeleBot("TOKEN_TELEGRAM")

