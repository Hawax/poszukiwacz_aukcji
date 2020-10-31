from sqlalchemy import create_engine

from aukcje import session
from aukcje.get_new_offers import NewOffers
from aukcje.models import User
from aukcje.scrapers import OtoMotoScraper, OlxScraper, AllegroLokalnieScraper
from aukcje.parsers import OtoMotoParser, OlxParser, AllegroLokalnieParser
import time
from aukcje import bot
from telebot import types
from contextlib import contextmanager



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
    def start(user_id_telegram):
        session_thread_safe = session()
        user = session_thread_safe.query(User).filter_by(id_telegram=user_id_telegram).first()

        while True:
            time.sleep(15)
            if user.start == False or user.urls is None:
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
                        text, photo = get_good_parser(domain)().parse(diff, user)
                        bot.send_photo(user.id_telegram, photo=photo, caption=text, parse_mode='HTML')
                    user.urls_data[dicts[0]] = new_offers
                user.checks -= 1
                session_thread_safe.commit()

            if user.checks < 0:
                bot.send_message(user.id_telegram, '<b>Sprawdzanie zostaje zatrzymane wpisz</b> /start <b>aby wznowic prace</b>',parse_mode='HTML', reply_markup=start_markup())
                user.start = False
                session_thread_safe.commit()



            time.sleep(user.timeout)


