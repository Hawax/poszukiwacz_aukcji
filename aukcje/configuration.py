import datetime
from aukcje import bot
import tldextract
from telebot import types
from aukcje import session
from aukcje.job_creator import start_markup
from aukcje.models import User
from aukcje.domains import Domains
import re


HOW_IT_HAPPEND = 'Nie mam pojęcia jak to sie stało ale najpierw wpisz komendę /start 🙄'

def make_default_keyboard():
    """Makes default KeyBoard"""
    markup = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.InlineKeyboardButton(text='/ustawienia', )
    itembtn2 = types.InlineKeyboardButton(text='/usunlink', )
    itembtn3 = types.InlineKeyboardButton(text='/coileczasu', )
    itembtn4 = types.InlineKeyboardButton(text='/dealer', )
    itembtn5 = types.InlineKeyboardButton(text='/dodajsprawdzenia', )
    itembtn6 = types.InlineKeyboardButton(text='/stop', )
    itembtn7 = types.InlineKeyboardButton(text='/pomoc', )
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6, itembtn7)
    return markup


def make_keyboard_url():
    """Makes KeyBoard"""
    markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
    itembtn1 = types.InlineKeyboardButton(text='/link1', )
    itembtn2 = types.InlineKeyboardButton(text='/link2', )
    itembtn3 = types.InlineKeyboardButton(text='/link3', )
    markup.add(itembtn1, itembtn2, itembtn3)
    return markup


def check_url(url, domain, message):
    """Check url contains correct domain"""
    text_to_send = 'Brakuje sortowania po najnowszych'
    for value in Domains.all():
        if value[0] == domain:
            if value[1] not in url:
                print(url, value[1])
                bot.send_message(message.chat.id, text_to_send)
            return True

    return False


def add_link_to_database(message, domain, url):
    if message.text in ['/link1', '/link2', '/link3']:
        last_dig = message.text[-1]
        user = session.query(User).filter_by(id_telegram=message.chat.id).first()
        if user:
            user.urls[f'url{last_dig}'] = (domain, url)
            bot.send_message(message.chat.id, f'Super, ustawiłem link nr.{last_dig} na \n{url}',
                         disable_web_page_preview=True, reply_markup=make_default_keyboard())
            session.commit()
        else:
            bot.send_message(message.chat.id, HOW_IT_HAPPEND)
    else:

        bot.send_message(message.chat.id, 'Zła komenda', reply_markup=make_default_keyboard())


def find_url_in_message_text(regexp_string, message):
    p = re.compile(regexp_string)
    result = p.search(message.text).group(1)
    return result


def get_url_to_settings(list):
    try:
        return f"{list[0]} : \n{list[1]}"
    except:
        return None


def remove_link_from_database(message, user):
    if message.text in ['/link1', '/link2', '/link3']:
        last_dig = message.text[-1]
        if user:
            try:
                del user.urls[f'url{last_dig}']
            except: pass # not exist
            bot.send_message(message.chat.id, f'Super, usunąłem link nr.{last_dig}', reply_markup=make_default_keyboard())
            session.commit()
        else:
            bot.send_message(message.chat.id, HOW_IT_HAPPEND)
    else:
        bot.send_message(message.chat.id, 'Zła komenda', reply_markup=make_default_keyboard())


def set_timeout(message, user):
    try:
        timeout = int(message.text)
    except:
        bot.send_message(message.chat.id, 'Zła wartość')
        return

    if timeout < 300:
        bot.send_message(message.chat.id, 'Za mała wartość musi być większa niż 300 sekund (5 min)')
    elif timeout > 1800:
        bot.send_message(message.chat.id, 'Za duża wartość musi być mniejasz niż 1800 sekund (30 min)')
    else:
        user.timeout = timeout
        session.commit()
        bot.send_message(message.chat.id, f'Pomyślnie ustawiono czas na {timeout} sekund ({round(timeout/60, 2)} minut)')


def set_dealer(message, user):
    if message.text.lower() == 'tak':
        bot.send_message(message.chat.id, f'😄Bedziesz otrzymywać oferty od dilerów na OtoMoto 😄')
        user.dealer = True
        session.commit()
    elif message.text.lower() == 'nie':
         bot.send_message(message.chat.id, f'😁 <b>NIE</b> bedziesz otrzymywać ofert od dilerów na OtoMoto 😁', parse_mode='HTML')
         user.dealer = False
         session.commit()
    else:
        bot.send_message(message.chat.id, f'Musisz podać Tak lub Nie 😡')



class Configuration:
    global regexp_string
    regexp_string = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"

    @staticmethod
    @bot.message_handler(regexp=regexp_string) #checks URL EXIST in message
    def check_for_url(message):
        message.text = find_url_in_message_text(regexp_string, message) #it accually return URL not message!

        parsed_url = tldextract.extract(message.text)
        domain = (parsed_url.domain + '.' + parsed_url.suffix)
        url = message.text

        is_link_good = check_url(url, domain, message)
        if is_link_good is False:
            bot.send_message(message.chat.id, "Niepoprawny serwis! 😡")
            return

        markup = make_keyboard_url()
        bot.send_message(message.chat.id, "🥳 Wybierz link:", reply_markup=markup)
        bot.register_next_step_handler(message, add_link_to_database, url=url, domain=domain)

    @staticmethod
    @bot.message_handler(commands=['ustawienia', 'settings'])
    def return_settings(message):
        user = session.query(User).filter_by(id_telegram=message.chat.id).first()
        if user is None:
            bot.send_message(message.chat.id, HOW_IT_HAPPEND)
            return

        text = f"Twoje ustawienia:\n\n" \
               f"link nr.1: {get_url_to_settings(user.urls.get('url1')) or 'Brak'}\n\n" \
               f"link nr.2: {get_url_to_settings(user.urls.get('url2')) or 'Brak'}\n\n"\
               f"link nr.3: {get_url_to_settings(user.urls.get('url3')) or 'Brak'}\n\n" \
               f"Ile sprawdzeń: {user.checks}\n\n"\
               f"Czy wysyłać samochody od dilerów: {'Tak' if user.dealer else 'Nie'}\n\n"\
               f"Co ile sprawdzać: {user.timeout} sekund ({round(user.timeout/60, 2)} minut)\n\n"\
               f"Bot wyłączy się dnia: {(datetime.datetime.now()+datetime.timedelta(seconds=(user.timeout*user.checks)/(len(user.urls.items()) or 1))).strftime('%d-%m-%Y o około %H:%M')} \n\n"
        bot.send_message(message.chat.id, text, disable_web_page_preview=True)

    @staticmethod
    @bot.message_handler(commands=['usunlink'])
    def delete_url(message):
        user = session.query(User).filter_by(id_telegram=message.chat.id).first()
        if user is None:
            bot.send_message(message.chat.id, HOW_IT_HAPPEND)
            return

        text = f"Wybierz link do usunięcia"
        bot.send_message(message.chat.id, text, disable_web_page_preview=True,  reply_markup=make_keyboard_url())
        bot.register_next_step_handler(message, remove_link_from_database, user)

    @staticmethod
    @bot.message_handler(commands=['dodajsprawdzenia'])
    def add_checks(message):
        user = session.query(User).filter_by(id_telegram=message.chat.id).first()
        if user is None:
            bot.send_message(message.chat.id, HOW_IT_HAPPEND)
            return
        if user.checks > 300:
            text = f"Żeby dodać sprawdzenia musisz mieć mniej niż 300 sprawdzeń, " \
                   f"aktualnie masz {user.checks} sprawdzeń. 😉"
        else:
            user.checks = 600
            session.commit()
            text = f"Pomyślnie dodano sprawdzenia i aktualnie masz ich 600! 🤩"
        bot.send_message(message.chat.id, text, disable_web_page_preview=True)

    @staticmethod
    @bot.message_handler(commands=['coileczasu'])
    def add_checks(message):
        user = session.query(User).filter_by(id_telegram=message.chat.id).first()
        if user is None:
            bot.send_message(message.chat.id, HOW_IT_HAPPEND)
            return
        text = f"Podaj czas w sekundach, pamięaj nie może być mniejszy niż 300 sekund (5 min) 🥳"
        bot.send_message(message.chat.id, text, disable_web_page_preview=True)
        bot.register_next_step_handler(message, set_timeout, user)


    @staticmethod
    @bot.message_handler(commands=['dealer'])
    def dealer(message):
        user = session.query(User).filter_by(id_telegram=message.chat.id).first()
        if user is None:
            bot.send_message(message.chat.id, HOW_IT_HAPPEND)
            return
        text = f"Wpisz <b>Tak</b> lub <b>Nie</b>"
        bot.send_message(message.chat.id, text, disable_web_page_preview=True, parse_mode='HTML')
        bot.register_next_step_handler(message, set_dealer, user)

    @staticmethod
    @bot.message_handler(commands=['stop'])
    def dealer(message):
        user = session.query(User).filter_by(id_telegram=message.chat.id).first()
        if user is None:
            bot.send_message(message.chat.id, HOW_IT_HAPPEND)
            return
        text = f"<b>Bot zostaje zatrzymany</b>"
        user.start = False
        session.commit()
        bot.send_message(message.chat.id, text, disable_web_page_preview=True, parse_mode='HTML', reply_markup=start_markup())

    @staticmethod
    @bot.message_handler(commands=['pomoc'])
    def help(message):
        with open('help_message.txt', 'r', encoding='UTF-8') as f:
            help_text = f.read()
        bot.send_message(message.chat.id, help_text, parse_mode='HTML')

