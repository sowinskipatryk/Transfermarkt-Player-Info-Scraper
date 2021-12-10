from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd

url = "https://www.transfermarkt.pl/spieler-statistik/wertvollstespieler/marktwertetop?ajax=yw1&page=19"

profile_links_short = []


def scrape_page(url):
    print(f'Now scraping: {url}')

    PATH = r'C:\Program Files (x86)\chromedriver.exe'

    driver = webdriver.Chrome(PATH)

    driver.get(url)

    driver.implicitly_wait(5)

    page_html = driver.page_source

    driver.close()

    soup = BeautifulSoup(page_html, 'html.parser')

    return soup


def get_profile_links(soup):

    items = soup.find('table', {'class': 'items'})
    rows = items.find_all('td', {'class': 'hauptlink'})

    i = 0
    for row in rows:
        try:
            row_tag = row.find('a')
            profile_link_short = row_tag['href']
            profile_links_short.append(profile_link_short)
            i += 1
        except:
            i += 0

    print(f'Scraped {i} player profile links, {len(profile_links_short)} in total.')
    return


def is_next_page(soup):
    try:
        next_page = soup.find('li', {'class': 'tm-pagination__list-item tm-pagination__list-item--icon-next-page'})
        next_page_a = next_page.find('a')
        next_page_link = f"https://www.transfermarkt.pl{next_page_a['href']}"
        print('There is a next page with links.\n')
    except:
        next_page = []
        next_page_link = []
        print('This is the last page with links.\n')
    return next_page, next_page_link


def scrape_player_info():
    for link in profile_links_short:
        profile_link_long = f'https://www.transfermarkt.pl{link}'
        soup = scrape_page(profile_link_long)

        try:
            name = soup.find('h1', {'itemprop': 'name'}).text
        except:
            name = []

        try:
            nationality = soup.find('span', {'itemprop': 'nationality'}).text
        except:
            nationality = []

        try:
            birth_date_full = (soup.find('span', {'itemprop': 'birthDate'}).text.replace('\n', '').strip()).split()
            birth_date = ' '.join(birth_date_full[0:3])
            age = int(birth_date_full[3].replace('(', "").replace(')', ""))
        except:
            birth_date = []
            age = []

        try:
            height = round(float((soup.find('span', {'itemprop': 'height'}).text.split()[0]).replace(',', '.')), 2)
        except:
            height = []

        try:
            position_divs = soup.find_all('div', {'class': 'dataDaten'})
            position_spans = position_divs[1].find_all('span', {'class': 'dataValue'})
            position = position_spans[1].text.replace('\n', '').strip()
        except:
            position = []

        try:
            market_value = (' '.join(soup.find('div', {'class': 'dataMarktwert'}).text.replace('\n', '').split()[0:1]))\
                .replace(',', '.')
            market_value = round(float(market_value), 2)
        except:
            market_value = []

        try:
            club = soup.find('span', {'class': 'hauptpunkt'}).text
        except:
            club = []

        player_index = profile_links_short.index(link)+1
        print(f'Scraped {player_index}/{len(profile_links_short)} player profile info page(s).')
        save_data(player_index, name, nationality, birth_date, age, height, position, market_value, club,
                  profile_link_long)

    return


def save_data(player_index, name, nationality, birth_date, age, height, position, market_value, club,
              profile_link_long):
    df = pd.DataFrame([player_index, name, nationality, birth_date, age, height, position, market_value, club,
                       profile_link_long]).T
    df.columns = ['Index', 'Player', 'Country', 'Birth Date', 'Age', 'Height (m)', 'Position',
                  'Market Value (mln EUR)', 'Team', 'Profile link']
    df.to_csv('results.csv', mode='a', index=False, header=False)
    print('Data saved in CSV file.\n')
    return


def export_to_excel():
    read_file = pd.read_csv('results.csv', header=None)
    read_file.columns = ['Index', 'Player', 'Country', 'Birth Date', 'Age', 'Height (m)', 'Position',
                         'Market Value (mln EUR)', 'Team', 'Profile link']
    read_file.to_excel('results.xlsx', index=None, header=True)
    return


soup = scrape_page(url)
get_profile_links(soup)
next_page, next_page_link = is_next_page(soup)

while next_page:
    soup = scrape_page(next_page_link)
    get_profile_links(soup)
    next_page, next_page_link = is_next_page(soup)

scrape_player_info()
export_to_excel()
