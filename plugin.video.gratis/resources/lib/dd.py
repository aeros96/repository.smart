import sys
import re
import json
from urllib.parse import quote_plus, urljoin
import xbmcplugin
import xbmcgui
import requests
from bs4 import BeautifulSoup
from .plugin2 import m


BASE_URL = 'https://1.dlhd.sx'
SCHEDULE = urljoin(BASE_URL, '/schedule/schedule-generated.json')
EXTRA = urljoin(BASE_URL, '/schedule/schedule-extra-generated.json')
CHANNELS = f'{BASE_URL}/24-7-channels.php'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
HEADERS = {
    'User-Agent': USER_AGENT,
    'Referer': f'{BASE_URL}/'
}
SOURCE = re.compile("source:'(.+?)'")


def main():
    xbmcplugin.setPluginCategory(int(sys.argv[1]), 'Live Sports')
    schedule = requests.get(SCHEDULE, headers=HEADERS, timeout=10).json()
    extra = requests.get(EXTRA, headers=HEADERS, timeout=10).json()
    schedule.update(extra)
    for key in schedule.keys():
        m.add_dir(key.split(' -')[0], json.dumps(schedule[key]), 'live_categories', m.addon_icon, m.addon_fanart, key.split(' -')[0])

def live_categories(url: str):
    categories = json.loads(url)
    for cat in categories.keys():
        m.add_dir(cat, json.dumps(categories[cat]), 'live_submenu', m.addon_icon, m.addon_fanart, cat)

def submenu(name: str, url: str):
    xbmcplugin.setPluginCategory(int(sys.argv[1]), name)
    events = json.loads(url)
    for event in events:
        m.add_dir(event.get('event', ''), json.dumps([[channel.get('channel_name'), f"{BASE_URL}/stream/stream-{channel.get('channel_id')}.php"] for channel in event.get('channels')]), 'live_links', m.addon_icon, m.addon_fanart, event.get('event', ''), isFolder=False)

def get_channels():
    xbmcplugin.setPluginCategory(int(sys.argv[1]), 'Live Channels')
    response = requests.get(CHANNELS, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    password = m.get_setting('adult_pw')
    channels = []
    for a in soup.find_all('a')[7:]:
        title = a.text
        link = f"{BASE_URL}{a['href']}"
        if '18+' in title and password != 'xxXXxx':
            continue
        if not link in channels:
            channels.append(link)
            m.add_dir(title, link, 'live_links', m.addon_icon, m.addon_fanart, title, isFolder=False)


def get_links(name, url: str):
    if url.startswith('['):
        url = json.loads(url)
        if type(url) == list:
            if len(url) > 1:
                url = m.get_multilink(url)
                if not url:
                    sys.exit()
            else:
                url = url[0][1]
    response = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    iframe = soup.find('iframe', attrs={'id': 'thatframe'})
    if iframe:
        url2 = iframe.get('src')
        if url2:
            headers = {
                'User-Agent': USER_AGENT,
                'Referer': url
            }
            response2 = requests.get(url2, headers=headers, timeout=10)
            links = re.findall(SOURCE, response2.text)
            if links:
                link = f'{links[0]}'
                referer = quote_plus(url2)
                user_agent = quote_plus(USER_AGENT)
                link = f'{link}|Referer={referer}&Origin={referer}&Keep-Alive=true&User-Agent={user_agent}'
                
                liz = xbmcgui.ListItem(name, path=link)
                liz.setProperty('inputstream', 'inputstream.ffmpegdirect')
                liz.setProperty('inputstream.ffmpegdirect.is_realtime_stream', 'true')
                liz.setProperty('inputstream.ffmpegdirect.stream_mode', 'timeshift')
                liz.setProperty('inputstream.ffmpegdirect.manifest_type', 'hls')
                liz.setMimeType('application/x-mpegURL')
                xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)


def runner(p: dict):
    name = p.get('name', '')
    url = p.get('url', '')
    mode = p.get('mode')
    
    if mode == 'live_main':
        main()
    
    elif mode == 'live_categories':
        live_categories(url)
    
    elif mode == 'live_submenu':
        submenu(name, url)
    
    elif mode == 'live_channels_main':
        get_channels()
    
    elif mode == 'live_channels':
        get_channels()
    
    elif mode == 'live_links':
        get_links(name, url)
    
   