from sqlalchemy import create_engine

from aukcje import session
from aukcje.get_new_offers import NewOffers
from aukcje.scrapers import OtoMotoScraper, OlxScraper, AllegroLokalnieScraper
from aukcje.parsers import OtoMotoParser, OlxParser, AllegroLokalnieParser
import time
from aukcje import bot
from telebot import types
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker

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


def start_markup():
    markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    itembtn1 = types.InlineKeyboardButton(text='/start', )
    markup.add(itembtn1)
    return markup


def get_good_scrapers(domain):
    if domain == 'otomoto.pl':
        return OtoMotoScraper
    if domain == 'olx.pl':
        return OlxScraper
    if domain == 'allegrolokalnie.pl':
        return AllegroLokalnieScraper


def get_good_parser(domain):
    if domain == 'otomoto.pl':
        return OtoMotoParser
    if domain == 'olx.pl':
        return OlxParser
    if domain == 'allegrolokalnie.pl':
        return AllegroLokalnieParser


class JobStarter():
    @staticmethod
    def start(user):
        while True:
            time.sleep(15)
            if user.start == False:
                break
            for dicts in list(user.urls.items()).copy():
                if dicts is None:
                    continue
                domain = dicts[1][0]
                url = dicts[1][1]

                new_offers = (get_good_scrapers(domain)().scrape(url, dicts[0])).get(dicts[0])
                old_offers = user.urls_data.get(dicts[0])
                diffs = NewOffers.diff(new_offers, old_offers, domain, user)
                if diffs:
                    for diff in diffs:
                        text, photo = get_good_parser(domain)().parse(diff)
                        bot.send_photo(user.id_telegram, photo=photo, caption=text, parse_mode='HTML')
                    user.urls_data[dicts[0]] = new_offers
                user.checks -= 1
                with session_scope() as session:
                    session.commit()
            if user.checks < 0:
                bot.send_message(user.id_telegram, '<b>Sprawdzanie zostaje zatrzymane wpisz</b> /start <b>aby wznowic prace</b>',parse_mode='HTML', reply_markup=start_markup())
                user.start = False
                session.commit()
                break
            time.sleep(user.timeout)


