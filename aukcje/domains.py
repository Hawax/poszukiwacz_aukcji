from enum import Enum


class Domains(Enum):
    olx = ('olx.pl', 'created_at%3Adesc')
    #allegro = ('allegro.pl', '?order=n')
    allegrolokal = ('allegrolokalnie.pl', '&sort=startingTime')
    otomoto = ('otomoto.pl', 'search%5Border%5D=created_at_first')

    @classmethod
    def all(cls):
        return (value.value for value in cls)

