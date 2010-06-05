#!/usr/bin/env python
# -*- coding:Utf-8 -*-

import urllib, urllib2, os
import zipfile
import os.path
import glob

dir = os.getcwd() + "/"
prg = ["serveur.py", "pysnake.py", "pysnake_needed.py"]
tools = ["update.py", "upload.py", "the_editor_of_the_death_that_kill.py"]
config = ["config"]
maps = ["map1", "map2", "map3", "map4"]
note = ["note.txt", "bugs.txt"]

#snakes :
couleur = ["bleu", "vert", "rouge", "jaune", "orange", "violet", "rose"]
parties = ["corps", "tete_g", "tete_h", "tete_d", "tete_b"]
img = []
try: os.listdir(dir+"img/snakes/")
except:
   os.mkdir(dir+"img/")
   os.mkdir(dir+"img/snakes/")
   os.mkdir(dir+"img/objets/")
   os.mkdir(dir+"img/murs/")
for c in couleur:
   try: os.listdir(dir+"img/snakes/"+c+"/")
   except:
      os.mkdir(dir+"img/snakes/" + c + "/")
   #for p in parties:
   #   img.append("snakes/"+c + "/" + p + ".gif")

#objets :
obj = ["pomme", "accel", "apocalypse", "decel", "arma-powa", "nocontrol", "demi-tour"]
objets = []
for o in obj:
   objets.append(o + ".gif")

#murs :
murs = ["murs/murs.gif", "murs/murs_big.gif"]

URL = "http://pysnake.franceserv.com/pysnake/"

def down(list, url = URL, dir_voulu = ""):
   while True:
      if dir_voulu == "img/": rep = "Y"
      else: rep = raw_input("Do you want to download "+str(list)+" files ? (y/n) : ")
      if rep.upper() == "Y":
         print "Downloading "+str(list)+" :\n",
         try: list.reverse(); list.reverse() #teste si list est un liste...
         except:
            print "pas liste"
            if dir_voulu == "":
               urllib.urlretrieve(url + list, dir + list)
            else:
               urllib.urlretrieve(url+list, dir + dir_voulu + list)
            return
         for i in list:
            print "liste"
            print "   -", i,
            try:
               if dir_voulu == "":
               	urllib.urlretrieve(url + i, dir + i)
               else:
                  urllib.urlretrieve(url+i, dir + dir_voulu + i)
            except:
               print "Failed, check your connection, and retry later."
               break
            else:
               print "-OK-\n"
         break
      elif rep.upper() == "N":
         break

def dezip(filezip, pathdst = ''):
    if pathdst == '': pathdst = os.getcwd()  ## on dezippe dans le repertoire locale
    zfile = zipfile.ZipFile(filezip, 'r')
    for i in zfile.namelist():  ## On parcourt l'ensemble des fichiers de l'archive
        print i
        if os.path.isdir(i):   ## S'il s'agit d'un repertoire, on se contente de creer le dossier
            try: os.makedirs(pathdst + os.sep + i)
            except: pass
        else:
            try: os.makedirs(pathdst + os.sep + os.path.dirname(i))
            except: pass
            data = zfile.read(i)                   ## lecture du fichier compresse
            fp = open(pathdst + os.sep + i, "wb")  ## creation en local du nouveau fichier
            fp.write(data)                         ## ajout des donnees du fichier compresse dans le fichier local
            fp.close()
    zfile.close()


def getmaps():
   the_url = "http://pysnake.franceserv.com/map.php"
   req = urllib2.Request(the_url)
   handle = urllib2.urlopen(req)
   the_page = handle.read() # "map1-map2-map3-map4-"
   the_page = the_page.split("-")
   print the_page
   list = []
   for i in the_page:
   		if i != "":
   			list.append(i)
   try: os.listdir(dir+"maps/")
   except: os.mkdir("maps/")
   down(list, "http://pysnake.franceserv.com/maps/", "maps/")

down(prg)
down(note)
down(config)
while 1:
   rep = raw_input("Do you want to download images ? (y/n) : ")
   if rep.upper() == "Y":
      urllib.urlretrieve("http://pysnake.franceserv.com/img.zip", dir + "img.zip")
      dezip('img.zip', os.getcwd())
      break
   elif rep.upper() == "N":
      break

#down(murs, "http://pysnake.franceserv.com/img/", "img/")

while 1:
   rep = raw_input("Do you want to try to get the maps ? (y/n) : ")
   if rep.upper() == "Y":
      getmaps()
      break
   elif rep.upper() == "N":
      break
