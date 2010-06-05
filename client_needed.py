#!/usr/bin/env python
# -*- coding:Utf-8 -*-

PHRASES = ["Hi !", "Bye Bye !", "Good Luck !", "Thanks !", "Are you ok ?", "Yes !", "No !", "I'm the best :D", "Good Game !!", "Argh I'm laggy ! -.-", "XD", "I love this game !"]
CHAT_MAX_MSG = 12


class Joueurs():

   def __init__(self):
      self.list = [] # [[0, kidanger, 0], [1, choupom, 99]]
      #self.texts = [["", ""]]*CHAT_MAX_MSG #[[pseudo, msg], ...]
      #self.texts = [["", ""], ["", ""], ["", ""], ["", ""], ["", ""], ["", ""], ["", ""], ["", ""], ["", ""], ["", ""], ["", ""], ["", ""]] #[[pseudo, msg], ...] #pas de hard-coding
      exec('self.texts = [' + '[-1, ""],' * (CHAT_MAX_MSG - 1) + '[-1, ""]]') #[[id, msg], ..]
   
   def ajout(self, id, pseudo, score=0):
      a = [int(id), pseudo, int(score)]
      self.list.append(a)
   
   def suppr(self, id):
      for i in range(4):
         try: self.list[i]
         except IndexError: 0
         else:
            if self.list[i][0] == id:
               del self.list[i]
   
   def change_pseudo(self, id, pseudo):
      for j in range(len(self.list)):
         if self.list[j][0] == int(id):
            self.list[j][1] = pseudo
   
   def change_score(self, id, score):
      for j in range(len(self.list)):
         if self.list[j][0] == int(id):
            self.list[j][2] = int(score)
   
   def dit(self, id, phrase): #Ajoute un text à la liste utilisée par le chat
      #On décale les phrases
      for i in range(len(self.texts)):
         if i != len(self.texts)-1:
            self.texts[i][0] = self.texts[i+1][0]
            self.texts[i][1] = self.texts[i+1][1]
      
      try: int(phrase) #Si la phrase est un nombre => else
      except ValueError: #sinon, ça vient du serv, on ajoute alors sa phrase
         self.texts[len(self.texts)-1][0] = -1
         self.texts[len(self.texts)-1][1] = phrase
      else: #on ajoute la phrase => except
         self.texts[len(self.texts)-1][0] = int(id)
         self.texts[len(self.texts)-1][1] = PHRASES[int(phrase)-1]




class Objets():

   def __init__(self):
      self.list = {}
   
   def update(self, objets):
      if objets == ["EMPTY"]:
         self.list.clear()
         return
      self.list.clear()
      for o in objets:
         o = o.split(",")
         x = int(o[0])
         y = int(o[1])
         type = int(o[2])
         id = int(o[3])
         self.list[id] = [x, y, type, id]



class Snake():
   
   def __init__(self, dir, couleur, tete, queues): # tete = [x, y] || queues = [[x, y], [x2, y2], ..., [xn, yn]]
      self.direction = dir
      x_tete = int(tete[0])
      y_tete = int(tete[1])
      self.couleur = couleur
      self.tete = [x_tete, y_tete]
      self.queues = []
      for q in queues:
         x = int(q[0])
         y = int(q[1])
         self.queues.append([x, y])
   
   def update(self, dir, couleur, tete, queues): #actualisation
      #exemple : tete = [1, 2], queues = [[1,3]]
      self.direction = dir
      x_tete = int(tete[0])
      y_tete = int(tete[1])
      self.tete = [x_tete, y_tete]
      self.queues = []
      for q in queues:
         x = int(q[0])
         y = int(q[1])
         self.queues.append([x, y])
   
   def move(self, x, y): #avance dans la direction donnÃ©e sans rÃ©flÃ©chir
      x_tete = self.tete[0]
      y_tete = self.tete[1]
      self.tete = [self.tete[0], x, y]
      
      #chaque queue prend la place de la prÃ©cÃ©dente :
      for i in range(len(self.queues)):
         i = len(self.queues)-i-1 #on part de la derniÃ¨re queue pour arriver Ã  la premiÃ¨re
         if i == 0: #si c'est la 1Ã¨re queue
            self.queues[i][0] = x_tete
            self.queues[i][1] = y_tete
         else:
            self.queues[i][0] = self.queues[i-1][0] #prend la place de la queue d'avant
            self.queues[i][1] = self.queues[i-1][1]
   
   def suppr(self):
      self.tete = []
      self.queues = []


class Murs():
   
   def __init__(self):
      self.list = []
   
   def update(self, murs):
      self.list = []
      for m in murs:
         m = m.split(",")
         x1 = int(m[0])
         y1 = int(m[1])
         x2 = int(m[2])
         y2 = int(m[3])
         self.list.append([x1, y1, x2, y2])
