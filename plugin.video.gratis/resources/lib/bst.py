import xbmcplugin
import sys
import re
from urllib.parse import quote_plus
from .plugin2 import Myaddon, m

base_url = 'https://srstop.link'
new_shows = base_url + '/new-shows'
all_shows = base_url + '/browse-shows'
most_popular = base_url + '/tv-shows/imdb_rating'


class BST(Myaddon):
    
    def __init__(self):
        self.index = {
            '19e0c88cc': '.',
        	'19e0c88cd': '/',
        	'???' : '_',
        	'????' : '-',
        	'19e0c88d8': ':',
        	'19e0c88df': 'A',
        	'19e0c88e0': 'B',
        	'19e0c88e1': 'C',
        	'19e0c88e2': 'D',
        	'19e0c88e3': 'E',
        	'19e0c88e4': 'F',
        	'19e0c88e5': 'G',
	        '19e0c88e6': 'H',
        	'19e0c88e7': 'I',
        	'19e0c88e8': 'J',
        	'19e0c88e9': 'K',
        	'19e0c88ea': 'L',
        	'19e0c88eb': 'M',
        	'19e0c88ec': 'N',
        	'19e0c88ed': 'O',
        	'19e0c88ee': 'P',
        	'19e0c88ef': 'Q',
        	'19e0c88f0': 'R',
	        '19e0c88f1': 'S',
	        '19e0c88f2': 'T',
        	'19e0c88f3': 'U',
        	'19e0c88f4': 'V',
        	'19e0c88f5': 'W',
        	'19e0c88f6': 'X',
        	'19e0c88f7': 'Y',
	        '19e0c88f8': 'Z',
	        '19e0c88ff': 'a',
	        '19e0c8900': 'b',
        	'19e0c8901': 'c',
        	'19e0c8902': 'd',
        	'19e0c8903': 'e',
	        '19e0c8904': 'f',
        	'19e0c8905': 'g',
        	'19e0c8906': 'h',
        	'19e0c8907': 'i',
        	'19e0c8908': 'j',
        	'19e0c8909': 'k',
	        '19e0c890a': 'l',
        	'19e0c890b': 'm',
        	'19e0c890c': 'n',
        	'19e0c890d': 'o',
        	'19e0c890e': 'p',
        	'19e0c890f': 'q',
	        '19e0c8910': 'r',
        	'19e0c8911': 's',
        	'19e0c8912': 't',
        	'19e0c8913': 'u',
        	'19e0c8914': 'v',
        	'19e0c8915': 'w',
	        '19e0c8916': 'x',
	        '19e0c8917': 'y',
        	'19e0c8918': 'z',
	        '19e0c88ce': '0',
        	'19e0c88cf': '1',
        	'19e0c88d0': '2',
        	'19e0c88d1': '3',
        	'19e0c88d2': '4',
        	'19e0c88d3': '5',
        	'19e0c88d4': '6',
        	'19e0c88d5': '7',
	        '19e0c88d6': '8',
        	'19e0c88d7': '9'
        }

    def get_url(self, string):
        for item in self.index.keys():
            string = string.replace(item, self.index[item])
        return string.replace('-', '')

    def get_latest(self, url):
        soup = self.get_soup(url)
        titles = soup.find_all(class_ = 'hgrid')
        item_list = []
        for title in titles:
            name = title.find(class_ = 'title tags').text
            ep_number = title.find('i').text
            ep_name = title.find('strong').text
            full_name = name + ' ' + ep_number.replace(' ','') + ' - "' + ep_name + '"'
            browse_now = title.find(class_ = 'browse_now morph')
            thumb = re.compile("url\('(.+?)&amp").findall(str(browse_now))[0]
            watch_now = title.find(class_ = 'watch_now morph')
            link = watch_now.get('href')
            fanart = re.compile("url\('(.+?)&amp").findall(str(watch_now))[0]
            item_list.append({'name': full_name, 'url': link, 'icon': thumb, 'fanart': fanart})
        if len(url.split('/'))==5:
            current_page = int(url.split('/')[-1])
            next_page = new_shows + '/' +str(current_page + 1)
        else:
            next_page = new_shows + '/2'
        item_list.append(next_page)
        return item_list

    def get_links(self, title, url, icon):
        soup = self.get_soup(url)
        links_soup = soup.find_all(class_='embed-selector')
        links = []
        for link in links_soup:
            link_coded = re.compile("dbneg\('(.+?)'\)").findall(str(link))[0]
            host = re.compile("domain=(.+?)'").findall(str(link))[0]
            url = self.get_url(link_coded)
            links.append([host, url])
        from .player2 import Player
        Player().play_video(title, links, icon, title)

    def browse_shows(self, url):
        soup = self.get_soup(url).find_all('a', class_ = 'img_poster browse_now morph')
        item_list = []
        for item in soup:
            name = item['title']
            link = item['href']
            thumb = re.compile("url\('(.+?)&amp").findall(str(item))[0]
            item_list.append({'name': name, 'url': link, 'icon': thumb})
        if len(url.split('/'))==6:
            current_page = int(url.split('/')[-1])
            next_page = most_popular + '/' +str(current_page + 1)
        else:
            next_page = most_popular + '/2'
        item_list.append(next_page)
        return item_list

    def all_episodes(self, url):
        soup = self.get_soup(url)
        episodes = soup.find_all(class_='hgrid')
        item_list = []
        for episode in episodes:
            name1 = episode.find('a', class_='episode').text
            name2 = episode.find(class_='episode').text
            link = episode.find(class_='hb-image watch_now')['href']
            thumb = episode.find(class_='hb-image watch_now')['data-original'].split('&w')[0]
            item_list.append({'name': name1+' - '+name2, 'url': link, 'icon': thumb})
        return item_list

#---BS Menus---#

bst = BST()

def bshows1(url):
    for x in bst.get_latest(url)[:-1]:
        bst.add_dir(x.get('name'), x.get('url'), 'bst_get_links', x.get('icon'), x.get('fanart'),'', name2=x.get('name'), isFolder=False)
    bst.add_dir('Next Page', bst.get_latest(url)[-1], 'bst_new_shows', '', '', 'Next Page')

def bshows_series(url):
    for x in bst.browse_shows(url)[:-1]:
        bst.add_dir(x.get('name'), x.get('url'), 'bst_episodes', x.get('icon'), bst.addon_fanart,'')
    bst.add_dir('Next Page', bst.browse_shows(url)[-1], 'bst_browse_shows', '', '', 'Next Page')

def bshows_episodes(title, url):
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE)
    for x in bst.all_episodes(url):
        bst.add_dir(x.get('name'), x.get('url'), 'bst_get_links', x.get('icon'), bst.addon_fanart, '', name2=f'{title} - {x.get("name")}', isFolder=False)

def search_shows():
    query = m.from_keyboard()
    if not query:
        quit()
    import requests
    response = requests.post(f'https://srstop.link/ajax/search.php?q={quote_plus(query)}', headers=m.headers).json()
    for item in response:
        title = item.get('title', '')
        link = item.get('permalink', '')
        thumbnail = item.get('image', '')
        m.add_dir(title, link, 'bst_episodes', thumbnail, m.addon_fanart, title)

def runner(p: dict):
    name = p.get('name', '')
    name2 = p.get('name2', '')
    url = p.get('url', '')
    mode = p.get('mode')
    icon = p.get('icon', bst.addon_icon)
    page = p.get('page', '')
    if page: page = int(page)
    
    if mode == 'bst_new_shows':
        if url == '':
            url = new_shows
        bshows1(url)
    
    elif mode == 'bst_series':
        bshows_series(most_popular)
    
    elif mode == 'bst_episodes':
        bshows_episodes(name, url)
        
    elif mode == 'bst_get_links':
        bst.get_links(name2, url, icon)
        
    elif mode == 'bst_browse_shows':
        bshows_series(url)
    
    elif mode == 'bst_search':
        search_shows()