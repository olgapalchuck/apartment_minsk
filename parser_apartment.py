# coding=utf-8
import requests
from bs4 import BeautifulSoup
import csv
import datetime
from random import randint
from time import sleep

from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth

URL = 'https://m.realt.by/sale/flats/?search=eJwrLkksSY0vSk3PzM%2BLz0xRNXVKVTV1sTVVK8kvRxEwNDBSiy9OLSktAAoVpSbHF6QWxRckpoNljQ0AdXcXbA%3D%3D&view=0='

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Mobile Safari/537.36',
    'accept': '*/*'}
DATE = datetime.date.today()
FILE = f"apartment_{DATE}.csv"  # type:


def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='list-objects-item')

    apartment = []
    for item in items:
        apartment.append({
            'adress': item.find('div', class_='address-line').get_text(strip=True).replace('Минск,', ''),
            'district': item.find('div', class_='district').get_text(strip=True).replace('район,', ''),
            'metro_near': item.find('div', class_='mobile-metro').get_text(strip=True).replace('-комнатная квартира',
                                                                                               ''),
            'rooms': item.find('span', class_='desc').get_text(strip=True).replace('-комнатная квартира', ''),
            'price_byn': item.find('span', class_='byn').get_text(strip=True).replace('\xa0', ''),
            'date': item.find('span', class_='data').get_text(strip=True).replace('Обновлено', ''),
        })
    return apartment


def get_pages_count(html):
    soup = BeautifulSoup(html, 'html.parser')
    pagination = soup.find('div', class_='pagination')
    page = pagination.find_all('a')
    return int(page[-1].get_text())


def save_file(items, path):
    with open(path, 'w') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['adress', 'district', 'metro_near', 'rooms', 'price_byn', 'date'])
        for item in items:
            writer.writerow([item['adress'], item['district'],
                             item['metro_near'], item['rooms'],
                             item['price_byn'], item['date']])


def save_drive(file):
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    gfile = drive.CreateFile({'parents': [{'id': '1z5eSqxbcz1uqdS7CsAdFm17lRNmuRcYE'}]})
    gfile.SetContentFile(file)
    gfile.Upload()
    print('Загрузка на Google drive прошла успешно')


def parse():
    html = get_html(URL)

    if html.status_code == 200:
        apartments = []
        pages_count = get_pages_count(html.text)
        for page in range(0, pages_count - 2):
            print(f"Парсинг страницы {page} из {pages_count - 2} страниц ...")
            html = get_html(URL, params={'page': page})
            apartments.extend(get_content(html.text))
            save_file(apartments, FILE)
            x = randint(1, 5)
            sleep(x)
            print(f"Получено {len(apartments)} квартир")
            print(f"Я подождал {x} сек")

        print(f"Получено {len(apartments)} квартир")
        save_drive(FILE)

    else:
        print('Error')


parse()
