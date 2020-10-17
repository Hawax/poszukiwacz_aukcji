import requests
import lxml.html
import random
from bs4 import BeautifulSoup


def get_element(list):
    try:
        return list[0].text.replace('\n', '')
    except:
        return None


class Node:
    @staticmethod
    def childTexts(node):
        texts = {}
        for child in list(node):
            texts[child.tag] = child.text
        return texts['span']


class Scraper:
    def get_proxy(self):
        with open('proxy_list.txt', 'r') as f:
            proxy_list = f.read().splitlines()
        return {'http': random.choice(proxy_list)}

    def open_connection(self, url):
        # proxy = self.get_proxy()
        try:
            r = requests.get(url)
            if r.status_code == 200:
                return r
            else:
                return self.open_connection(url)
        except:
            return self.open_connection(url)


class OtoMotoScraper(Scraper):
    def scrape(self, url, which_one):
        response = self.open_connection(url)
        tree = lxml.html.fromstring(response.content)
        articles = tree.xpath('//article')
        data = {which_one: []}
        for article in articles:
            parms = {}
            tree = lxml.html.fromstring(lxml.html.tostring(article))  # makes tree from article
            name = str(tree.xpath("//a[@class='offer-title__link']")[0].text).strip()
            try:
                description = str(
                    tree.xpath("//h3[@class='offer-item__subtitle ds-title-complement hidden-xs']")[0].text).strip()
            except IndexError:
                description = "Brak Opisu"

            for car_parm in tree.xpath("//li[@class='ds-param']"):
                parms.update({car_parm.attrib['data-code']: Node.childTexts(car_parm)})

            location = tree.xpath("//span[@class='ds-location-city']")[0].text + ' ' + \
                       tree.xpath("//span[@class='ds-location-region']")[0].text
            price = tree.xpath("//span[@class='offer-price__number ds-price-number' and 1]/span[1]")[0].text + ' ' + \
                    tree.xpath("//span[@class='offer-price__number ds-price-number' and 1]/span[2]")[0].text
            dealer = tree.xpath("//a[@class='offer-item__link-logo ds-image-button' and 1]/span[1]") + tree.xpath(
                "//a[@class='offer-item__link-seller ds-seller-link' and 1]")
            car_id = article.attrib['data-ad-id']
            try:
                photo = (
                    (tree.xpath("//div[@class='offer-item__photo  ds-photo-container']/a/img")[0].attrib[
                        'data-srcset']).split(
                        ' ')[0]).replace(';s=320x240', '')

            except IndexError:
                photo = 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Brak_obrazka.svg/600px-Brak_obrazka.svg.png'
            link = article.attrib['data-href']

            data[which_one].append({
                'id': car_id,
                'name': name,
                'photo': photo,
                'link': link,
                'price': price,
                'description': description,
                'params': parms,
                'location': location,
                'dealer': str(dealer),

            })
        return data


class OlxScraper(Scraper):
    def scrape(self, url, which_one):
        response = self.open_connection(url)
        tree = lxml.html.fromstring(response.content)
        articles = tree.xpath("//td[@class='offer  ']") or tree.xpath("//td[@class='offer  offer-job']")
        data = {which_one: []}

        for article in articles:
            tree = lxml.html.fromstring(lxml.html.tostring(article))
            soup = BeautifulSoup(lxml.html.tostring(article), "html.parser") #had to use bs4 beacuse lxml does not work properly
            where_and_when = " ".join(soup.find_all('td', {'class': 'bottom-cell'})[0].text.split())
            name = str(tree.xpath("//a[1]/strong[1]")[0].text).strip().replace('\n', '')
            price = get_element(tree.xpath("//p[1]/strong[1]")) or soup.find_all('div', {'class': 'list-item__price'})[
                0].text.replace('\n', '') or 'Brak informacji'
            offer_id = tree.xpath("//div[@class='offer-wrapper']//table")[0].attrib['data-id']
            try:
                link = tree.xpath("//td/a")[0].attrib['href']
            except IndexError:
                link = tree.xpath("//div/h3[@class='lheight22 margintop5' and 1]//a")[0].attrib['href']

            try:
                photo = tree.xpath("//img")[0].attrib['src']
            except IndexError:
                photo = 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Brak_obrazka.svg/600px-Brak_obrazka.svg.png'

            data[which_one].append({
                'id': offer_id,
                'name': name,
                'photo': photo,
                'link': link,
                'price': price,
                'location': where_and_when,

            })
        return data


class AllegroLokalnieScraper(Scraper):
    def scrape(self, url, which_one):
        response = self.open_connection(url)
        tree = lxml.html.fromstring(response.content)
        articles = tree.xpath("//a[@class='card offer-card']")
        data = {which_one: []}
        for article in articles:
            tree = lxml.html.fromstring(lxml.html.tostring(article))
            soup = BeautifulSoup(lxml.html.tostring(article), "html.parser")
            name = tree.xpath("//h3[@class='offer-card__title']")[0].text.strip()
            price = tree.xpath("//span[@class='price offer-card--buy-now' and 1]") or \
                    tree.xpath("//span[@class='price offer-card--bidding' and 1]") or \
                    tree.xpath("//span[@class='price offer-card--classified' and 1]")
            kind_offer = tree.xpath(
                "//div[@class='text-11 text-uppercase fw-semi m-b-1 offer-card__type offer-card--classified' and 2]") or \
                         tree.xpath(
                             "//div[@class='text-11 text-uppercase fw-semi m-b-1 offer-card__type offer-card--buy-now' and 2]") or \
                         tree.xpath(
                             "//div[@class='text-11 text-uppercase fw-semi m-b-1 offer-card__type offer-card--bidding']")
            location = tree.xpath("//div[@class='offer-card__location']/span[1]")[0]
            photo = tree.xpath("//div/img[1]")[0].attrib['src']
            link = tree.xpath("//a[1]")[0].attrib['href']
            try:
                description = " ".join(soup.find_all('li', {'class': 'd-ib m-r-2'})[0].text.split())
            except IndexError:
                description = 'Brak'

            data[which_one].append({
                'id': str(link),
                'name': str(name),
                'photo': str(photo),
                'link': str("https://allegrolokalnie.pl" + link),
                'price': str(price[0].text) + ',00zł',
                'description': str(description),
                'location': str(location.text),
                'kind_offer': str(kind_offer[0].text)

            })

        return data
