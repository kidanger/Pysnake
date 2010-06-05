#!/usr/bin/env python
# -*- coding:Utf-8 -*-

import socket, threading, sys
from Tkinter import *

Sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # on cree notre socket

# definition des informations :
Host = '127.0.0.1'
Port = 4000
PHRASES = ["Hi !", "Good Game !", "Thanks !","Are you ok ?", "Yes !", "No !", "Pwned", "I'm the best :D", "Good Luck !"] #9 phrases

class Envoi(threading.Thread):
     def __init__(self,Sock):
          threading.Thread.__init__(self)
          self.Sock=Sock

     def run(self):
          print "Emission on"
          self.root=Tk()
          self.message=StringVar()
          self.message_saisi=Entry(self.root,textvariable=self.message)
          self.message_saisi.pack()
          self.bouton_envoyer=Button(self.root,text="envoyer",command=self.envoyer)
          self.bouton_envoyer.pack()
          self.root.mainloop()
          sys.exit()

     def envoyer(self):
          self.Sock.send(self.message.get())



class Recv(threading.Thread):
     def __init__(self, Sock):
          self.Sock=Sock
          threading.Thread.__init__(self)
          
     def run(self):
          print "Reception on"
          while True:
               msgServer=self.Sock.recv(1024)
               if msgServer[:3] == "say": # say i n
                    print msgServer[4], "dit:", PHRASES[int(msgServer[6])+1]
               else: print msgServer

Sock.connect((Host,Port))

Envoi_Th=Envoi(Sock)
Envoi_Th.start()
Recp_Th = Recv(Sock)
Recp_Th.start()