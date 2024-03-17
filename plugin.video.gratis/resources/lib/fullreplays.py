from bs4 import BeautifulSoup as bs
from requests.sessions import Session
from .player2 import player
from .plugin2 import m


class FullReplays():
    def __init__(self):
        self.base_url = "https://www.fullreplays.com"
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
        self.headers = {
            'User-Agent': self.user_agent,
            'Referer': self.base_url
        }
        self.session = Session()
        self.session.headers = self.headers

    def main(self):
        return self.submenu(self.base_url)
    
    def submenu(self, page: str):
        m.add_dir('[COLOR red][B]***Links may take several seconds to populate!***[/B][/COLOR]', '', '', m.addon_icon, m.addon_fanart, '', isFolder=False)
        response = self.session.get(page).text
        soup = (bs(response, 'html.parser'))
        row = soup.find(class_='row vlog-posts row-eq-height')
        for article in row.find_all('article'):
            title = article.h2.text
            link = article.a['href']
            thumbnail = article.a.img['src']
            m.add_dir(title, link, 'soccer_links', thumbnail, m.addon_fanart, title, isFolder=False)
        pagination = soup.find(class_='next page-numbers')
        if pagination:
            next_page = pagination['href']
            m.add_dir('Next Page', next_page, 'soccer_submenu', m.addon_icon, m.addon_fanart, 'Next Page')
    
    def get_links(self, name: str, url: str, icon: str):
        links = []
        response = self.session.get(url).text
        soup = bs(response, 'html.parser')
        sources = soup.find_all(class_='frc-sources-wrap')
        for source in sources:
            host = source.find(class_='frc-vid-label').text.lower()
            for button in source.find_all(class_='vlog-button'):
                title = f'{button.text.strip()} - {host.capitalize()}'
                link = button['data-sc']
                #if 'fviplions' in link:
                    #continue
                links.append([title, link])
        if links:
           player.play_video(name, links, icon, name)

def runner(p: dict):
    #---Params---#
    name = p.get('name', '')
    url = p.get('url', '')
    mode = p.get('mode')
    if mode and str.isdecimal(mode):
        mode = int(mode)
    icon = p.get('icon', m.addon_icon)
    page = p.get('page', '1')
    if str.isdecimal(page):
        page = int(page)
    soccer = FullReplays()
    
    #---Modes---#
    if mode == 'soccer_main':
        soccer.main()

    elif mode == 'soccer_submenu':
        soccer.submenu(url)

    elif mode == 'soccer_links':
        soccer.get_links(name, url, icon)
    