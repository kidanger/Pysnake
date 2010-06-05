#!/usr/bin/env python
# -*- coding:Utf-8 -*-

import ftplib
import os

def upload(ftp, file):
   ext = os.path.splitext(file)[1]
   if ext in (".txt", ".htm", ".html"):
      ftp.storlines("STOR " + file, open(file))
   else:
      print ftp.storbinary("STOR " + file, open(file, "rb"), 1024)

def for_admin(ftp):
   list = ["serveur.py", "pysnake.py", "pysnake_needed.py", "upload.py", "update.py", "note.txt", "bugs.txt", "config", "the_map_editor_of_the_death_that_kill.py"]
   for i in list:
      while 1:
         rep = raw_input("Do you want to upload \"" + i + "\" ? (y/n) : ")
         if rep.upper() == "Y":
            upload(ftp, i)
            break
         elif rep.upper() == "N":
            print "Dommage :("
            break
   print "For maps, please wait, still in developpement !"

def up_map(ftp):
   listing = os.listdir(os.getcwd())
   list = []
   for i in range(len(listing)):
      if listing[i] != "config.ini" and listing[i][(len(listing[i])-4):] == ".ini":
         list.append(listing[i])
   rep = raw_input('In this list: '+list+'\nWhich map do you want to upload ?')
   if rep in list:
      upload(ftp, rep)
      print "Uploaded"
   else:
      print "Can't found", rep

print "If you want to upload a map, it's on this page: http://pysnake.franceserv.com/upload.html"
ftp = ftplib.FTP("ftp.franceserv.com")
mdp = raw_input("\nEnter the password of the FTP admin account: ")
print ftp.login("pysnake", mdp)
dir = "/pysnake.franceserv.com/pysnake"
ftp.cwd(dir)
for_admin(ftp)

ftp.quit()
ftp.close()

