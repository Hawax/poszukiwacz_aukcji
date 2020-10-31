from threading import Thread

from aukcje import session_scope
from aukcje.job_creator import JobStarter
from aukcje.models import User
from aukcje import bot
from aukcje.configuration import make_default_keyboard


class MakeUser():
    @staticmethod
    @bot.message_handler(commands=['start'])
    def creation(message):
        with session_scope() as session:
            user = session.query(User).filter_by(id_telegram=message.chat.id).first()
            if user and user.start:
                bot.send_message(message.chat.id, f'Spokojnie bot działa ☺️', reply_markup=make_default_keyboard())
                return
            if user and user.start is False:
                user.start = True
                job_starter = JobStarter().start
                Thread(target=job_starter, args=(str(user.id_telegram), )).start()
                bot.send_message(message.chat.id, f'Wznawiam pracę bota 🥳 ', reply_markup=make_default_keyboard())
                if user.checks < 300:
                    user.checks = 600
                session.commit()
                return
            user = User(id_telegram=message.chat.id,
                        username=(message.chat.first_name + ' ' + message.chat.last_name))


            session.add(user)
            session.commit()
            print('dodano', user.username)

            with open('help_message.txt', 'r', encoding='UTF-8') as f:
                help_text = f.read()
            bot.send_message(message.chat.id, help_text, parse_mode='HTML', reply_markup=make_default_keyboard())
            job_starter = JobStarter().start
            Thread(target=job_starter, args=(str(user.id_telegram), )).start()
