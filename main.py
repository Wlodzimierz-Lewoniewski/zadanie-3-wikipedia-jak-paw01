import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote
import re


def pobierz_html_kategorii(nazwa_kategorii):
    url = f"https://pl.wikipedia.org/wiki/Kategoria:{nazwa_kategorii}"
    response = requests.get(url)
    return response.text


def ekstrakcja_adresow_i_nazw(html):
    soup = BeautifulSoup(html, 'html.parser')
    linki = soup.select('.mw-category-group a')

    adresy_url = []
    nazwy = []
    for link in linki:
        href = link.get('href')
        if href and href.startswith("/wiki/") and ':' not in href:
            adresy_url.append(href)
            nazwy.append(link.get_text())
    return adresy_url, nazwy


def pobierz_i_analizuj_artykuly(adresy_url):
    wyniki = {}
    for adres in adresy_url[:2]:
        url = f"https://pl.wikipedia.org{adres}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        odnosniki = []

        for link in soup.find_all('a', href=True, title=True):
            if (link['href'].startswith("/wiki/") and
                ':' not in link['href'] and
                "Zobacz stronę treści [c]" not in link['title'] and
                link['title'] != "Ziemia"):  # Wykluczenie ziemia
                tytul = link['title']
                odnosniki.append(tytul)
                if len(odnosniki) == 5:
                    break

        wyniki[adres.split('/')[-1]] = odnosniki

    return wyniki


def pobierz_url_obrazow(html):
    soup = BeautifulSoup(html, 'html.parser')

    obrazy_do_pominięcia = [
        '/static/images/icons/wikipedia.png',
        '//upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Geographylogo.svg/20px-Geographylogo.svg.png',
        '/static/images/footer/wikimedia-button.png',
        '/static/images/footer/poweredby_mediawiki_88x31.png'
    ]

    obrazy = soup.find_all('img', src=True)

    obrazy = [img for img in obrazy if re.search(r'\.(jpg|jpeg|png|gif)$', img['src'], re.IGNORECASE)
              and not any(pomijany in img['src'] for pomijany in obrazy_do_pominięcia)]

    # Zbierz URL pierwszych trzech obrazów
    url_obrazow = [img['src'] for img in obrazy[:3]]

    return url_obrazow

def pobierz_url_zrodel(html):
    soup = BeautifulSoup(html, 'html.parser')
    przypisy = soup.find_all('span', class_='reference-text')

    url_zrodel = []
    for przypis in przypisy:
        linki = przypis.find_all('a', class_='external text')
        for link in linki[:3]:
            url = link.get('href')
            # Zastąpienie '&' przez '&amp;'
            url_zamienione = url.replace('&', '&amp;')
            url_zrodel.append(url_zamienione)

    return url_zrodel[:3]

def pobierz_liste_kategorii(html):
    soup = BeautifulSoup(html, 'html.parser')
    kategorie = soup.select('.mw-normal-catlinks ul li a')[:3]
    return [kat.get_text() for kat in kategorie]


# Główna część skryptu
nazwa_kategorii = input()
html_kategorii = pobierz_html_kategorii(nazwa_kategorii)
adresy_url, _ = ekstrakcja_adresow_i_nazw(html_kategorii)
wyniki_odnosnikow = pobierz_i_analizuj_artykuly(adresy_url)

for adres in adresy_url[:2]:
    url_artykulu = f"https://pl.wikipedia.org{adres}"
    html_artykulu = requests.get(url_artykulu).text

    obrazki = [url.replace('%0A', '') for url in pobierz_url_obrazow(html_artykulu)]
    zrodla = pobierz_url_zrodel(html_artykulu)
    kategorie = pobierz_liste_kategorii(html_artykulu)

    print(" | ".join(wyniki_odnosnikow[adres.split('/')[-1]]))
    print(" | ".join(obrazki))
    print(" | ".join(zrodla))
    print(" | ".join(kategorie))
