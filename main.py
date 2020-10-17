from aukcje import bot, session
from aukcje.fireup import FireUP
from aukcje.makeuser import MakeUser
from aukcje.configuration import Configuration


FireUP.start()
MakeUser()
Configuration()

bot.polling(none_stop=True)

