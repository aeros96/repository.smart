import sys
from urllib.parse import quote_plus
import xbmc
import xbmcvfs
import xbmcgui
import xbmcaddon
import xbmcplugin
import requests
from bs4 import BeautifulSoup


class Myaddon:
    
    addon_id = xbmcaddon.Addon().getAddonInfo('id')
    addon_name = xbmcaddon.Addon().getAddonInfo('name')
    addon_data = xbmcvfs.translatePath(xbmcaddon.Addon().getAddonInfo('profile'))
    downloads_path = addon_data + 'downloads/'
    addon_path = xbmcvfs.translatePath(xbmcaddon.Addon().getAddonInfo('path'))
    addon_icon = xbmcaddon.Addon().getAddonInfo('icon')
    addon_fanart = xbmcaddon.Addon().getAddonInfo('fanart')
    addon_version = xbmcaddon.Addon().getAddonInfo('version')
    get_setting = xbmcaddon.Addon().getSetting
    set_setting = xbmcaddon.Addon().setSetting
    lists_path = addon_path + 'lists/'
    cache_file = addon_data + 'cache.db'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
    headers = {"User-Agent":user_agent, "Connection":'keep-alive', 'Accept':'audio/webm,audio/ogg,udio/wav,audio/*;q=0.9,application/ogg;q=0.7,video/*;q=0.6,*/*;q=0.5'}
    kodi_ver = float(xbmc.getInfoLabel("System.BuildVersion")[:4])
    
    def log(self, message: str):
        return xbmc.log(message, xbmc.LOGINFO)
    
    #---Request and Other Various Methods---#
    
    def get_page(self, url: str):
        return requests.get(url, headers=self.headers).text
    
    def get_soup(self, url: str, referer: str = '') -> BeautifulSoup:
        if referer:
            self.headers['Referer'] = referer
        response = requests.get(url, headers=self.headers).text
        return BeautifulSoup(response, 'html.parser')
    
    
    def get_multilink(self, lists, lists2=None, trailers=None):
        labels = []
        links = []
        counter = 1
        if lists2 is not None:
            for _list in lists2:
                lists.append(_list)
        for _list in lists:
            if type(_list) == list and len(_list) == 2:
                if len(lists) == 1:
                    return _list[1]
                labels.append(_list[0])
                links.append(_list[1])
            elif type(_list) == str:
                if len(lists) == 1:
                    return _list
                if _list.strip().endswith(')'):
                    labels.append(_list.split('(')[-1].replace(')', ''))
                    links.append(_list.rsplit('(')[0].strip())
                else:
                    labels.append('Link ' + str(counter))
                    links.append(_list)
            else:
                return
            counter += 1
        if trailers is not None:
            for name, link in trailers:
                labels.append(name)
                links.append(link)             
        dialog = xbmcgui.Dialog()
        ret = dialog.select('Choose a Link', labels)
        if ret == -1:
            return
        if type(lists[ret]) == str and lists[ret].endswith(')'):
            link = lists[ret].rsplit('(')[0].strip()     
        elif type(lists[ret]) == list:
            return lists[ret][1]
        return lists[ret]
  
    def from_keyboard(self, default_text='', header='Search'):
        kb = xbmc.Keyboard(default_text, header, False)
        kb.doModal()
        if (kb.isConfirmed()):
            return kb.getText()
        return None
    
    #---Add Directory Method---#

    def add_dir(self, name, url, mode, icon, fanart, description, name2 = '', page='', foldername='', context_menu=None, infolabels=None, cast=None, hls=False, media_type='video', _id='', season_number='', episode_number='', isFolder=True):
        u=sys.argv[0]+'?name='+quote_plus(name)+'&url='+quote_plus(url)+'&mode='+str(mode)+'&icon='+quote_plus(icon) +'&fanart='+quote_plus(fanart)+'&description='+quote_plus(description)+'&name2='+quote_plus(name2)+'&page='+str(page)+'&foldername='+quote_plus(foldername)+'&mediatype='+quote_plus(media_type)+'&_id='+str(_id)+'&season_number='+str(season_number)+'&episode_number='+str(episode_number)
        if cast is None:
            cast = []
        if infolabels is None:
            infolabels = {'title': name, 'plot': description, 'mediatype': media_type}
        liz=xbmcgui.ListItem(name)
        liz.setArt({'fanart': fanart, 'icon': icon, 'thumb': icon, 'poster': icon})
        self.set_info(liz, infolabels, cast=cast)
            
        if context_menu:
            liz.addContextMenuItems(context_menu)
        if hls is True:
            if '|' in url:
                splitted = url.split('|')
                url = splitted[0]
                url_headers = splitted[1]
                liz.setProperty('inputstream.adaptive.stream_headers', url_headers)
                liz.setPath(url)
            liz.setProperty('inputstream', 'inputstream.adaptive')
            liz.setProperty('inputstream.adaptive.manifest_type', 'hls')
            liz.setMimeType('application/vnd.apple.mpegurl')
            liz.setContentLookup(False)
            
        if isFolder is False:
            liz.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u,listitem=liz, isFolder=isFolder)
    
    def set_info(self, liz: xbmcgui.ListItem, infolabels: dict, cast: list=None):
        if cast is None:
            cast = []
        if self.kodi_ver < 20:
            liz.setInfo("video", infolabels)
            if cast:
                liz.setCast(cast)
        else:
            i = liz.getVideoInfoTag()
            i.setMediaType(infolabels.get("mediatype", "video"))
            i.setTitle(infolabels.get("title", "Unknown"))
            i.setPlot(infolabels.get("plot", infolabels.get("title", "")))
            i.setTagLine(infolabels.get("tagline", ""))
            i.setPremiered(infolabels.get("premiered", ""))
            i.setGenres(infolabels.get("genre", []))
            i.setMpaa(infolabels.get("mpaa", ""))
            i.setDirectors(infolabels.get("director", []))
            i.setWriters(infolabels.get("writer", []))
            i.setRating(infolabels.get("rating", 0))
            i.setVotes(infolabels.get("votes", 0))
            i.setStudios(infolabels.get("studio", []))
            i.setCountries(infolabels.get("country", []))
            i.setSet(infolabels.get("set", ""))
            i.setTvShowStatus(infolabels.get("status", ""))
            i.setDuration(infolabels.get("duration", 0))
            i.setTrailer(infolabels.get("trailer", ""))
            cast_list = []
            for actor in cast:
                name = actor.get("name", "")
                role = actor.get("role", "")
                thumbnail = actor.get("thumbnail", "")
                actor = xbmc.Actor(
                    name=name,
                    role=role,
                    thumbnail=thumbnail
                )
                cast_list.append(actor)
            i.setCast(cast_list)
    
    def end_directory(self):
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
    
    def set_content(self, content: str):
        return xbmcplugin.setContent(int(sys.argv[1]), content)
        

m = Myaddon()