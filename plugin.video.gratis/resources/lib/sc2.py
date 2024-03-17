import requests
import datetime
from bs4 import BeautifulSoup as bs
from base64 import b64decode
from .plugin2 import m

base_url = 'https://soccercatch.com'
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'
headers = {"User-Agent":user_agent, 'Referer': base_url}

def date_url(date):
    return f'{base_url}/api/matches/date?date={date}'

def date_post(url):
    return requests.post(url, headers=headers).text

def get_dates():
    dates = []
    d = datetime.date(2021,1,18)
    while d <= datetime.date.today():
        dates.append([datetime.datetime.strftime(d,'%A, %B %d, %Y'), datetime.datetime.strftime(d,'%d-%m-%Y')])
        d += datetime.timedelta(days=1)
    return list(reversed(dates))

def main(icon):
    dates = get_dates()
    for name, number in dates:
        url = date_url(number)
        m.add_dir(name, url, 'soccer_matches', icon, m.addon_fanart, '')

def matches(url):
    r = date_post(url)
    soup = (bs(r, 'html.parser'))
    _matches = soup.find_all('a', class_='match-list-content')
    for match in _matches:
        url = f"{base_url}{match['href']}"
        home = match.find(class_='match-list-home')
        away = match.find(class_='match-list-away')
        home_name = home.img['alt']
        home_icon = home.img['src']
        away_name = away.img['alt']
        away_icon = away.img['src']
        name = f'{home_name} vs {away_name}'
        m.add_dir(name, url, 'soccer_get_links', home_icon, away_icon, name, isFolder=False)

def get_links(name, url, icon):
    links = []
    r = requests.get(url, headers=headers).text
    soup = bs(r, 'html.parser')
    
    highlights = soup.find(class_ = "iframe-responsive")
    if highlights:
        embed = highlights.get("data-src")
        if embed:
            link = bs(embed, "html.parser").iframe.get("src")
            links.append(["Highlights", link])
    
    replays = soup.find(class_ = "code-block")
    if replays:
        embed = replays.get("data-src")
        if embed:
            data_url = bs(embed, "html.parser").find(class_="archive-link").get("data-url")
            if data_url:
                link = b64decode(data_url).decode("utf-8")
                splitted = link.split('/')
                _url = "https://footyarchive.com/api/matches/" + splitted[-1]
                headers['Referer'] = 'https://footyarchive.com/'
                try:
                    r = requests.get(_url, headers=headers).json()
                    vids = r.get('content')
                    for vid in vids:
                        for content in vid['content']:
                            title = content.get('title', '').split(' - ')
                            if len(title) > 1:
                                title = title[1]
                            else:
                                title = title[0]
                            link = b64decode(content['base64']).decode("utf-8")
                            splitted = link.split('/')
                            link_host = splitted[2]
                            title = f'{title} - {link_host}'
                            if 'payskip.org' in link:
                                continue
                            links.append([title, link])
                except:
                    pass
    if links:
        from .player2 import player
        player.play_video(name, links, icon, name)

def runner(p: dict):
    #---Params---#
    name = p.get('name', '')
    url = p.get('url', '')
    mode = p.get('mode', 'main_menu')
    if mode and str.isdecimal(mode):
        mode = int(mode)
    icon = p.get('icon', m.addon_icon)
    page = p.get('page', '1')
    if str.isdecimal(page):
        page = int(page)
    
    #---Modes---#
    if mode == 'soccer_main':
        main(icon)

    elif mode == 'soccer_matches':
        matches(url)

    elif mode == 'soccer_get_links':
        get_links(name, url, icon)