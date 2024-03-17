import sys
import xbmcplugin
import xbmcgui
from .plugin2 import Myaddon


class Player(Myaddon):
    
    def play_video(self, name, url, icon, description, resolve=True):
           if url is None:
               return
           link = url
           if type(link) == list:
               if len(link) > 1:
                   link = self.get_multilink(link)
               elif len(link) == 1:
                   if len(link[0]) == 2:
                       link = link[0][1]
                   elif len(link[0]) == 1:
                       link = link[0]
               else:
                   return
           if not link:
               return
           if link.endswith(')'):
               link = link.split('(')[0]
           
           if 'fviplions' in link:
               from resolveurl.plugins.filelions import FileLionsResolver
               #url = 'https://fviplions.com/s/dcs11dmqc49g'
               splitted = link.split('/')
               link = FileLionsResolver().get_media_url(splitted[2], splitted[-1])
           
           if 'tapenoads' in link:
               from resolveurl.plugins.streamtape import StreamTapeResolver
               resolver = StreamTapeResolver()
               #link = 'https://tapenoads.com/e/VzVD60JqXQh3Bl/Crvena_Zvezda_v_Leipzig_-_1080p_-_stan.mp4'
               splitted = link.split('/')
               link = resolver.get_media_url(splitted[2], splitted[4])
           
           if resolve is True:
               import resolveurl
               if resolveurl.HostedMediaFile(link).valid_url():
                   link = resolveurl.HostedMediaFile(link).resolve()
           liz = xbmcgui.ListItem(name, path=link)
           self.set_info(liz, {'title': name, 'plot':description})
           liz.setArt({'thumb': icon, 'icon': icon, 'poster': icon})
           liz.setProperty('IsPlayable', 'true')
           xbmcplugin.setResolvedUrl(int(sys.argv[1]), False, liz)

player = Player()
