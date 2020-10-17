class OtoMotoParser:

    @staticmethod
    def parse(raw_text):
        text_html = \
            f"""    
    <strong>{raw_text['name']}</strong>
<em>{raw_text['description']}</em>

Cena: <strong>{raw_text['price']}</strong>

<strong>Parametry:</strong>
 Rok produkcji: <em><strong>{raw_text['params'].get('year') or 'Brak'}</strong></em>
 Przebieg: <em>{raw_text['params'].get('mileage') or 'Brak'}</em>
 Pojemność: <em>{raw_text['params'].get('engine_capacity') or 'Brak'}</em>
 Rodzaj paliwa: <em>{raw_text['params'].get('fuel_type') or 'Brak'}</em>
 Lokalizacja: <em>{raw_text['location']}</em>
 LINK do aukcji : <a href="{(raw_text['link'])}">KLIKNIJ MNIE!</a>"""

        return text_html, raw_text['photo']


class OlxParser:

    @staticmethod
    def parse(raw_text):
        text_html = \
            f"""    
    <strong>{raw_text['name']}</strong>

Cena: <strong>{raw_text['price']}</strong>

<strong>Informacje:</strong>
 Lokalizacja: <em>{raw_text['location']}</em>
 LINK do aukcji : <a href="{raw_text['link']}">KLIKNIJ MNIE!</a>
                    """
        return text_html, raw_text['photo']


class AllegroLokalnieParser:

    @staticmethod
    def parse(raw_text):
        text_html = \
            f"""    
    <strong>{raw_text['name']}</strong>

Cena: <strong>{raw_text['price']} {raw_text['kind_offer']}</strong>

<strong>Informacje:</strong>
 Parametry: <em>{raw_text['description']}</em>
 
 Lokalizacja: <em>{raw_text['location']}</em>
 LINK do aukcji : <a href="{raw_text['link']}">KLIKNIJ MNIE!</a>
                    """
        return text_html, raw_text['photo']


