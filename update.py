#!/usr/bin/env python
# -*- coding:Utf-8 -*-

import urllib, urllib2, os
import os.path
import glob
import re

dir = os.getcwd() + "/"
prg = ["server.py", "client.py", "client_needed.py", "crc.py", "update.py", "the_map_editor_of_the_death_that_kill.py", "autoexec.cfg"]


#murs :
murs = ["murs/murs.gif", "murs/murs_big.gif"]



def check_for_update():
   url = "http://pysnake.franceserv.com/update"
   f = urllib2.urlopen(url)
   r = f.read(-1)
   try:
      s = open('update', 'r')
   except:
      open('update', 'w').write('000000')
      return True
   else:
      if r != s.read():
         return True
   return False
   
def do_update():
   download_files()
   url = "http://pysnake.franceserv.com/update"
   f = urllib2.urlopen(url)
   r = f.read(-1)
   s = open('update', 'w').write(r)

URL = "http://github.com/kidanger/Pysnake/blob/master/"
def download_files():
   for x in prg:
      try:
         f = urllib2.urlopen(URL + x)
         r = f.read(-1)
         t = re.search('<li><a href="(/kidanger/Pysnake/raw/.*/' + x +')" id="raw-url">raw</a></li>', r)
         f2 = urllib2.urlopen("http://github.com" + t.group(1))
         r2 = f2.read(-1)
         open(x, "w").write(r2)
      except:
         continue
      





