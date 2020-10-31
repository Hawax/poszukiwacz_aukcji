import sys
from threading import Thread
from aukcje import session, session_scope
from aukcje.job_creator import JobStarter
from aukcje.models import User
import time
from threading import Thread


class FireUP:
    @staticmethod
    def start():
        with session_scope() as session:
            users = session.query(User).filter(User.checks > 0).filter(User.start==True).all()
            for user in users:
                job_starter = JobStarter().start
                Thread(target=job_starter, args=(str(user.id_telegram),)).start()
                time.sleep(0.1)
            print(f'Ukończono włączanie dla {len(users)} użytkowników')


def list_active_users():
    while True:
        time.sleep(15)
        sesja = session()
        users = sesja.query(User).filter(User.checks > 0).filter(User.start==True).all()
        sys.stdout.write(str(len(users)) + ' - Ilość Aktywnych Użytkowników   ')
        sys.stdout.flush()
        sesja.close()


#Thread(target=list_active_users, args=()).start()