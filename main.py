from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd

domain = '.pl'  # change it if you want your data to be in another language or currency (.us/.co.uk/.de and so on)
driver_path = r'C:\Program Files (x86)\chromedriver.exe'
first_page_url = f"https://www.transfermarkt{domain}/spieler-statistik/wertvollstespieler/marktwertetop"

profile_links_short = []  # for iteration purposes


def scrape_page(path, url):

    print(f'Now scraping: {url}')
    driver = webdriver.Chrome(path)
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
        next_p = soup.find('li', {'class': 'tm-pagination__list-item tm-pagination__list-item--icon-next-page'})
        next_a = next_p.find('a')
        next_url = f"https://www.transfermarkt{domain}{next_a['href']}"
        print('There is a next page with links.\n')
    except:
        next_p = []
        next_url = []
        print('This is the last page with links.\n')
    return next_p, next_url


def scrape_player_info(path):

    for link in profile_links_short:
        profile_link_long = f'https://www.transfermarkt{domain}{link}'
        soup = scrape_page(path, profile_link_long)

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
    df.to_csv('results.csv', mode='a', index=False, header=False)
    print('Data saved in CSV file.\n')
    return


def export_to_excel():

    read_file = pd.read_csv('results.csv', header=None)
    # # header in english

    # read_file.columns = ['Index', 'Player', 'Country', 'Birth Date', 'Age', 'Height (m)', 'Position',
    #                      'Market Value (mln EUR)', 'Team', 'Profile link']

    # # header in polish
    read_file.columns = ['Lp.', 'Gracz', 'Kraj pochodzenia', 'Data urodzenia', 'Wiek', 'Wzrost (m)', 'Pozycja',
                         'Wartość rynkowa (mln EUR)', 'Drużyna', 'Link do profilu']
    read_file.to_excel('results.xlsx', index=None, header=True)
    print('Data saved in XLSX file')
    return


player_link_soup = scrape_page(driver_path, first_page_url)
get_profile_links(player_link_soup)
next_page_bool, next_page_url = is_next_page(player_link_soup)

while next_page_bool:
    player_link_soup = scrape_page(driver_path, next_page_url)
    get_profile_links(player_link_soup)
    next_page_bool, next_page_url = is_next_page(player_link_soup)

scrape_player_info(driver_path)
export_to_excel()
