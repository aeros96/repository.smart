import re
import math
from base64 import b64decode
import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://thetvapp.to'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
HEADERS = {"User-Agent": USER_AGENT, "Referer": BASE_URL}
SESSION = requests.Session()
SESSION.headers = HEADERS

def get_page(url: str, referer: str = '') -> str:
    if referer:
        HEADERS['Referer'] = referer
    return SESSION.get(url, headers=HEADERS).text

def get_soup(url: str, referer: str = '') -> BeautifulSoup:
    response = get_page(url, referer)
    return BeautifulSoup(response, 'html.parser')

def tvapp_main():
    items = []
    cats = get_soup(BASE_URL).find_all(class_='nav-link')
    for cat in cats[1:]:
        title = cat.text
        link = cat['href']
        items.append([title, link])
    return items

def sub_menu(url: str):
    items = []
    channels = get_soup(url).find_all(class_='list-group-item')
    for channel in channels:
        title = channel.text
        link = f"{BASE_URL}{channel['href']}"
        items.append([title, link])
    return items

def get_link(url: str) -> str:
    soup = get_soup(url)
    js = soup.find('script', attrs={'type': 'module'}).get('src')
    if js:
        js_page = get_page(js)
        js_function = re.findall('{file:(.+?)\(encrypted\)', js_page)[0]
    link = re.findall("encrypted = '(.+?)'", str(soup))
    if link:
        link = a4(link[0], get_key(js_page))
    return f'{link}|Referer={BASE_URL}'

#Tails
def get_key(file: str):
    deobfus_func_name = re.findall(r"{file:(.+?)\(encrypted\)", file)[0]
    deob_func = re.search(f"function {deobfus_func_name}\(.+?,.+?=(.+?)\)", file)
    key = deob_func.group(1)
    if key.startswith("'") or key.startswith('"'):
        key = eval(key)
        return key
    array_get_func_name = key[:key.index("(")]
    array_get_func_setter = re.search(f"const {array_get_func_name}=(.+?);", file)
    array_get_func_name = array_get_func_setter.group(1)
    backslash = "\\"
    array_get_func = re.search(f"return {backslash if array_get_func_name.startswith('$') else ''}{array_get_func_name}=function.+?" + "{", file)
    array_get_offset = int(file[file.index("-", array_get_func.end()) + 1:file.index(",", array_get_func.end())])
    for m in re.finditer(r"\.shift\(\)\)}}\)\((.+?),([0-9]+)\)", file):
        if m.start() > array_get_func_setter.start():
            array_func_match = m
            break
    array_func_name = array_func_match.group(1)
    array_shift_num = int(array_func_match.group(2))
    array_shift_func_body = file[file.rfind("(function", 0, array_func_match.start()):array_func_match.end()]
    array_func = re.search(f"function {array_func_name}\(\)", file)
    array = eval(file[file.index("[", array_func.start()):file.index("];", array_func.start()) + 1])
    expression = compile(re.findall(r"if\((.+?)===", array_shift_func_body)[0], "expression", "eval")

    def x(index) -> str:
        return array[index - array_get_offset]
    
    t = x
    
    def parseInt(s: str) -> int:
        m = re.match(r"([0-9]+)", s)
        if m == None:
            return math.nan
        else:
            return int(m.group(1))
    
    while eval(expression) != array_shift_num:
        array.append(array.pop(0))
    key = x(int(key[key.index("(") + 1:]))
    return key

def a4(n, t):
    e = b64decode(n).decode('utf-8')
    i = ''
    for o, p in enumerate(e):
        i += chr(ord(p) ^ ord(t[o % len(t)]))
    return i
