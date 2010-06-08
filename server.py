#!/usr/bin/env python
# -*- coding:Utf-8 -*-


import sys, socket, threading, urllib, urllib2, time, datetime, os, ConfigParser
from random import randrange
from datetime import datetime

#Map's crc:
from crc import *

global DEBUG
DEBUG = False


config = ConfigParser.RawConfigParser()
config.read("autoexec.cfg")

#[Objets]
OBJETS_WAIT_TIME = eval(config.get("Objets", "objets_wait_time"))
OBJETS_MAX = eval(config.get("Objets", "objets_max"))
ACCEL_DURATION = eval(config.get("Objets", "accel_duration"))
DECEL_DURATION = eval(config.get("Objets", "decel_duration"))
NOCONTROL_DURATION = eval(config.get("Objets", "nocontrol_duration"))
NOCONTROL_POINTS = eval(config.get("Objets", "nocontrol_points"))
LENGTH_OF_ARMA = eval(config.get("Objets", "length_of_arma"))

#[Game]
SCORE_MAX = eval(config.get("Game", "score_max"))
TIME_BETWEEN_GAME = eval(config.get("Game", "time_between_game"))
TIME_BETWEEN_CHAT = eval(config.get("Game", "time_between_chat"))
MAPS = eval(config.get("Game", "maps"))
SPEED_MAX = eval(config.get("Game", "speed_max"))
CLIENTS_MAX = eval(config.get("Game", "clients_max"))


CASES_X = 32
CASES_Y = 24
#SPEED_MAX = 1*(1.5**2) #2 accels max
SPEED_MIN = 1/(1.5**2) #2 deccel max

LENGTH_MAX_SERVER = 256
LENGTH_MAX_CLIENT = 20

LENGTH_QUEUE_MAX = 38

def log(text, what = "Global", keap_suspence = 0):
   if not keap_suspence and what != "":
      print "[%s] %s" % (what, text)
   elif keap_suspence:
      print "["+what+"] "+text,
   elif what == "":
      print text

def log_debug(text, what = "Global", keap_suspence=0):
   if DEBUG:
      log(text, what, keap_suspence)

class Objets(threading.Thread):

   def __init__(self):
      self.list = [] #[[x, y, type], [x, y, type]]
      threading.Thread.__init__(self, target = self.run)
   
   def run(self):
      #Au début, une bouffe => Jeu.game_start()
      #self.bouffe()
      #Au début, aléatoirement un bonus
      #self.bonus()
      
      while True:
         if len(clients) == 0:
            log("Nobody...")
         else:
            self.bonus()
         if clients: time.sleep(OBJETS_WAIT_TIME/len(clients)) #Ajout "dynamique" d'objet
         else: time.sleep(20)
   
   def bonus(self):
      if len(self.list) > OBJETS_MAX: return 0
      nb = randrange(0, 17)
      if nb in range(5): type = 1
      elif nb in range(5, 9): type = 2 #malus
      elif nb in range(9, 11): type = 3
      elif nb in range(11, 14): type = 4
      elif nb in range(14, 16): type = 5
      elif nb == 16: type = 6
      if type != 2:
         while 1:
            x = randrange(0, CASES_X)
            y = randrange(0, CASES_Y)
            if self.check(x, y):
               log("Bonus : type " + str(type), "Object")
               self.ajout(x, y, type)
               break
      
      else:
         objets = self.list
         if objets == []:
            while 1:
               x = randrange(0, CASES_X)
               y = randrange(0, CASES_Y)
               if self.check(x, y):
                  log("Malus : type " + str(type), "Objet")
                  self.ajout(x, y, type)
                  return
         essaie = []
         while 1:
            cible_id = randrange(0, len(objets))
            last_id = objets.index(objets[-1])
            i = 0
            for id in range(last_id+1):
               try: objet = objets[id] #[x, y, type]
               except: 0
               else:
                  if i == cible_id and objet[2] != 2:
                     cible = objet
                     break
                  i += 1
            #on a notre cible, on choisit de mettre le malus soit à droite, soit à gauche, soit... de la cible :
            while 1:
               dir = randrange(0, 4) #gauche = 0, haut = 1, droite = 2, bas = 3
               x, y = cible[0], cible[1]
               if dir == 0:
                  if self.check(x-1, y):
                     x -= 1
                     self.ajout(x, y, type)
                     return
               
               elif dir == 2:
                  if self.check(x+1, y):
                     x += 1
                     self.ajout(x, y, type)
                     return
               
               elif dir == 1:
                  if self.check(x, y-1):
                     y -= 1
                     self.ajout(x, y, type)
                     return
               
               elif dir == 3:
                  if self.check(x, y+1):
                     y += 1
                     self.ajout(x, y, type)
                     return
               
               essaie.append(cible_id)
               if len(essaie) == OBJETS_MAX: #Si on a essayé avec acharnement mais ça marche toujours pas, on le met n'importe où...
                  while 1:
                     x = randrange(0, CASES_X)
                     y = randrange(0, CASES_Y)
                     if self.check(x, y):
                        log("Malus : type " + str(type), "Objet")
                        self.ajout(x, y, type)
                        return
   
   def bouffe(self):
      while 1:
         x = randrange(0, CASES_X)
         y = randrange(0, CASES_Y)
         if self.check(x, y):
            self.ajout(x, y, 0)
            log("Bouffe", "Object")
            break
   
   def clear(self):
      self.list = []
      to_send = self.send_to_client()
      for id in clients:
         c = clients[id]
         c.envoyer(to_send, id)
   
   def check(self, x, y):
      if self.check_objet_vs_snakes(x, y) == 0:
         return 0
      if self.check_objet_vs_murs(x, y) == 0:
         return 0
      if self.check_objet_vs_startpos(x, y) == 0:
         return 0
      if self.check_objet_vs_objets(x, y) == 0:
         return 0
      return 1
   
   def check_objet_vs_snakes(self, x, y):
      for id in range(4):
         try: c = clients[id]
         except KeyError: 0
         else:
            if x == c.instance_jeu.tete[0] and y == c.instance_jeu.tete[1]: #objet meme position que tete
               return 0
            for q in c.instance_jeu.queues:
               if x == q[0] and y == q[1]: #objet meme position que queue
                  return 0
      return 1
   
   def check_objet_vs_murs(self, x, y):
      for m in murs.list:
         for x_m in range(m[0], m[2]+1):
            for y_m in range(m[1], m[3]+1):
               if x == x_m and y == y_m: #objet meme position que mur
                  return 0
      return 1
   
   def check_objet_vs_startpos(self, x, y):
      for id in clients:
         #if id == 1: start_pos = ["d", [5, 1], [4, 1], [3, 1], [2, 1]]
         #if id == 2: start_pos = ["g", [CASES_X-5, CASES_Y-1], [CASES_X-4, CASES_Y-1], [CASES_X-3, CASES_Y-1], [CASES_X-2, CASES_Y-1]]
         #if id == 3: start_pos = ["h", [1, CASES_Y-5], [1, CASES_Y-4], [1, CASES_Y-3], [1, CASES_Y-2]]
         #if id == 4: start_pos = ["b", [CASES_X-2, 5], [CASES_X-2, 4], [CASES_X-2, 3], [CASES_X-2, 2]]
         start_pos = murs.start_pos[id-1]
         for sp in start_pos[1:]:
            if x == sp[0] and y == sp[1]:
               return 0
   
   def check_objet_vs_objets(self, x, y):
      for o in self.list:
         if x == o[0] and y == o[1]: #objet meme position que objet
            return 0
      return 1
   
   def send_to_client(self):
      if len(self.list) == 0:
         return "objets EMPTY"
      to_send = "objets "
      for id in range(OBJETS_MAX):
         try: o = objets.list[id] #[x, y, type]
         except IndexError: 0
         else:
            x = o[0]
            y = o[1]
            type = o[2]
            if to_send=="objets ": to_send += str(x)+","+str(y)+","+str(type)+","+str(id)
            else: to_send += ";"+str(x)+","+str(y)+","+str(type)+","+str(id)
      return to_send
   
   def include_bouffe(self):
      for o in self.list:
         if self.list[o][2] == 0:
            return 1
      return 0

   def ajout(self, x, y, type):
      self.list.append([x, y, type])
      to_send = self.send_to_client()
      for id in clients:
         c = clients[id]
         c.envoyer(to_send, id)
      return 1
   
   def suppr(self, id):
      log_debug("Object to delete " + str(id), "Object")
      try: del self.list[id]
      except: log_debug("Not deleted", "Object")
      to_send = self.send_to_client()
      for id in clients:
         c = clients[id]
         c.envoyer(to_send, id)
   



class Jeu(threading.Thread):
   
   def __init__(self, client):
#      global conn_client
      threading.Thread.__init__(self, target = self.run)
      self.client = client
      couleurs = ["bleu", "jaune", "orange", "rose", "rouge", "vert", "violet"]
      for x in range(1, len(clients)+1):
         log_debug("Remove color: " + clients[x].instance_jeu.couleur, "Client's game")
         couleurs.remove(clients[x].instance_jeu.couleur)
      self.couleur = couleurs[randrange(0, len(couleurs))]
      #self.couleur = str(murs.start_pos[self.client.id-1][0])
      self.score = 0
      self.resu(0)
      self.deco = 0
   
   def run(self):
      self.client.envoyer(self.send_to_client())
      while True:
         if self.deco: break
         
         if self.accel != -1:
            dt = datetime.now()
            sec = dt.second
            if sec < self.accel: sec += 60
            if sec >= self.accel+ACCEL_DURATION:
               self.accel = -1
               self.speed /= 1.5
         
         if self.decel != -1:
            dt = datetime.now()
            sec = dt.second
            if sec < self.decel: sec += 60
            if sec >= self.decel+DECEL_DURATION:
               self.decel = -1
               self.speed *= 1.5
         
         if self.nocontrol != -1:
            dt = datetime.now()
            sec = dt.second
            if sec < self.nocontrol: sec += 60
            if sec >= self.nocontrol+NOCONTROL_DURATION:
               self.nocontrol = -1
         
         dt = datetime.now()
         ms = dt.microsecond/1000
         if ms < self.last_ms: ms += 1000
         if self.start_move and ms >= self.last_ms+(1000.0/(3*self.speed)): #3 = 3 cases par secondes
            self.move()
            dt = datetime.now()
            self.last_ms = dt.microsecond/1000
            to_send = self.send_to_client()
            self.client.envoyer(to_send)
   
   def eat(self):
      if len(self.queues) >= LENGTH_QUEUE_MAX:
         if clients:
            objets.bouffe()
         return 0
      x, y = self.queues[-1]
      self.queues.append([x, y])
      self.change_score(self.score+1)
      to_send = self.send_to_client()
      self.client.envoyer(to_send)
      if self.score == SCORE_MAX:
         self.game_end()
      elif clients:
         objets.bouffe()
   
   def game_end(self):
      self.client.envoyer("serv This_is_the_end_of_the_match_!")
      time.sleep(2)
      self.client.envoyer("serv The_Winner_is:_" + self.client.pseudo)
      time.sleep(TIME_BETWEEN_GAME)
      self.game_start()
   
   def game_start(self):
      objets.clear()
      murs.clean()
      murs.new_map()
      objets.bouffe()
      objets.bonus()
      for i in clients:
         client = clients[i]
   #      client.response_murs()
         client.instance_jeu.change_score(0)
         client.instance_jeu.resu(0)
      self.client.envoyer("serv Good_luck_everysnake_!")
   
   def change_score(self, new):
      if new < 0: return 0
      self.score = new
      to_send = "score %s %s" % (str(self.client.id), str(self.score))
      self.client.envoyer(to_send)
   
   def resu(self, score_moins_un=1):
      self.last_direction = str(murs.start_pos[self.client.id-1][1])
      self.direction = str(murs.start_pos[self.client.id-1][1])
      self.tete = list(murs.start_pos[self.client.id-1][2])
      self.queues = []
      for q in list(murs.start_pos[self.client.id-1][3:]):
         self.queues.append(list(q))

      self.derniere_phrase_date_de = 0
      self.speed = 1.0
      self.last_ms = 0
      self.start_move = 0 #changer de direction pour commencer à jouer
      to_send = self.send_to_client()
      self.client.envoyer(to_send, -1)
      self.accel = -1
      self.decel = -1
      self.nocontrol = -1
      if score_moins_un: self.change_score(self.score-1)
   
   
   def check(self):
      self.check_snake_vs_objets()
      self.check_snake_vs_snakes()
      self.check_snake_vs_murs()
   
   def demi_tour(self): #probleme : regarder les 2 dernières queues
      tete = self.tete
      queues = []
      for q in self.queues:
         queues.append(q)
      self.tete = queues[-1]
      self.queues[len(self.queues)-1] = tete
      for i in range(len(self.queues)):
         if i == len(self.queues)-1: self.queues[i] = tete
         else: self.queues[i] = queues[-2-i]
      
      premiere_queue = self.queues[0]
      if self.tete[0] - premiere_queue[0] == 1: #si tete à droite de 1ère queue
         self.direction = "d"
         self.last_direction = "d"
      elif self.tete[0] - premiere_queue[0] == -1: #si tete à gauche de 1ère queue
         self.direction = "g"
         self.last_direction = "g"
      elif self.tete[1] - premiere_queue[1] == 1: #si tete en bas de 1ère queue
         self.direction = "b"
         self.last_direction = "b"
      elif self.tete[1] - premiere_queue[1] == -1: #si tete en haut de 1ère queue
         self.direction = "h"
         self.last_direction = "h"
      
      to_send = self.send_to_client()
      self.client.envoyer(to_send)
   
   def armagetronad_powa(self):
      for i in range(LENGTH_OF_ARMA):
         x, y = self.queues[-1]
         self.queues.append([x, y])
      to_send = self.send_to_client()
      self.client.envoyer(to_send)

   
   def check_snake_vs_objets(self):
      for id in range(OBJETS_MAX):
         try: o = objets.list[id] #[x, y, type]
         except IndexError: 0
         else:
            if self.tete[0] == o[0] and self.tete[1] == o[1]: #tete meme position que objet
               if o[2] == 0: #bouffe
                  self.eat()
               elif o[2] == 1: #accélérateur
                  dt = datetime.now()
                  self.accel = dt.second
                  if self.speed < SPEED_MAX:
                     self.speed *= 1.5
                     self.client.envoyer("serv You_ate_an_accelerator_!", self.client.id)
               elif o[2] == 2: #déccélérateur
                  dt = datetime.now()
                  self.decel = dt.second
                  if self.speed > SPEED_MIN:
                     self.speed /= 1.5
                     self.client.envoyer("serv You_ate_a_deccelerator.", self.client.id)
               elif o[2] == 3: #nocontrol
                  dt = datetime.now()
                  self.nocontrol = dt.second
                  self.change_score(self.score+NOCONTROL_POINTS)
                  self.client.envoyer("serv You're_out_of_control...", self.client.id)
               elif o[2] == 4: #demi-tour
                  self.demi_tour()
               elif o[2] == 5: #armagetronad powa
                  self.armagetronad_powa()
                  self.client.envoyer("serv Your_snake_grow(grandir?).", self.client.id)
               elif o[2] == 6: #apocalypse
                  for c_id in clients:
                     if c_id != self.client.id:
                        snake = clients[c_id].instance_jeu
                        snake.resu()
                  self.change_score(self.score-len(clients))
                  self.client.envoyer("serv Apocalypse,_everysnake_are_dead,_expect_%s." % self.client.pseudo)
               objets.suppr(id)
               break
   
   def check_snake_vs_snakes(self):
      x, y = self.tete
      for i in clients:
         snake = clients[i].instance_jeu
         if self.start_move and snake.start_move:
            x_tete, y_tete = snake.tete
            if snake != self and x == x_tete and y == y_tete: #Si tête à tête, chaqu'un dans son camp
               self.resu()
               snake.resu()
               return 0
            for q in snake.queues:
               if x == q[0] and y == q[1]:
                  if snake == self: #on se coupe sa queue
                     del self.queues[self.queues.index(q):]
                  else:
                     self.resu()
                  return 0
      return 0
   
   def check_snake_vs_murs(self):
      tete = self.tete
      for m in murs.list:
         if tete[0] in range(m[0], m[2]+1):
            if tete[1] in range(m[1], m[3]+1):
               self.resu()
   
   
   def move(self): #avance dans la direction donnée sans réfléchir
      
      x_tete = self.tete[0]
      y_tete = self.tete[1]
      if self.direction == "g": #gauche
         self.tete[0] -= 1
      
      if self.direction == "h": #haut
         self.tete[1] -= 1
      
      if self.direction == "d": #droite
         self.tete[0] += 1
      
      if self.direction == "b": #bas
         self.tete[1] += 1
      
      #quand on vas à un coté de la map, on apparait à l'autre bout :
      if self.tete[0] == CASES_X:
         self.tete[0] = 0
      elif self.tete[0] == -1:
         self.tete[0] = CASES_X-1
      elif self.tete[1] == CASES_Y:
         self.tete[1] = 0
      elif self.tete[1] == -1:
         self.tete[1] = CASES_Y-1
         
      #chaque queue prend la place de la précédente :
      for i in range(len(self.queues)):
         i = len(self.queues)-i-1 #on part de la dernière queue pour arriver à la première
         if i == 0: #si c'est la 1ère queue
            self.queues[i][0] = x_tete
            self.queues[i][1] = y_tete
         else:
            self.queues[i][0] = self.queues[i-1][0] #prend la place de la queue d'avant
            self.queues[i][1] = self.queues[i-1][1]
      
      self.last_direction = self.direction
      self.check() #si prend un mur, de la bouffe, ou un snake
   
   def change_dir(self, dir):
      if self.nocontrol != -1: return 0
      if dir == "h": #haut
         if self.last_direction == "b": return 0 #on ne peut pas aller dans la direction opposée
         self.direction = "h"
      if dir == "g": #gauche
         if self.last_direction == "d": return 0 #on ne peut pas aller dans la direction opposée
         self.direction = "g"
      if dir == "d": #droite
         if self.last_direction == "g": return 0 #on ne peut pas aller dans la direction opposée
         self.direction = "d"
      if dir == "b": #bas
         if self.last_direction == "h": return 0 #on ne peut pas aller dans la direction opposée
         self.direction = "b"
      if self.start_move == 0:
         self.start_move = 1
   
   def send_to_client(self):
      #exemple : id = 1, direction = "g", couleur = "bleu", tete = [1, 2], queues = [[1, 3]]
      to_send = "snake " + str(self.client.id) + " " + self.direction + " " + self.couleur + " " #"snake 1 g bleu"
      to_send += (str(self.tete[0]) + "," + str(self.tete[1])) #t = "snake 1 g bleu 1,2"
      for i in range(len(self.queues)):
         to_send += (";" + str(self.queues[i][0]) + "," + str(self.queues[i][1])) #t = "snake 1 g bleu 1,2;1,3"
      return to_send




class Murs():
   
   def __init__(self): #pour le nom des maps, on commence à 1
      #self.found_maps() # remplis la liste self.maps
      self.list = []
      self.start_pos = []
      self.new_map()
      #[x1, y1, x2, y2]
   
   def search_map(self, nom):
      for x in os.listdir("maps/"):
         crc = get_crc(open('maps/' + x, "r").read())
         try:
            n = x[: x.index(crc + ".map")-1 ]
         except ValueError:
            continue
         if nom == n:
            return x, crc
   
   def load_map(self, config):
      #Murs:
      i = 0
      while 1:
         i += 1
         try:
            self.list.append( eval(config.get("Walls", "wall" + str(i))) )
         except:
            break
      #StartPos :
      i = 0
      while 1:
         i += 1
         try:
            self.start_pos.append( eval(config.get("StartPos", "player"+str(i))) )
         except:
            break
   
   def new_map(self, id = -1):
      if id == -1:
         id = randrange(0, len(MAPS))
      file, self.crc = self.search_map(MAPS[id])
      config = ConfigParser.RawConfigParser()
      try: config.read("maps/"+file)
      except:
         log("Map not found, please change the \"maps\" option in config.ini", "Map")
         return 0
         
      self.load_map(config)
      log("MAP : " + MAPS[id], "Map")
      self.map = MAPS[id]
      for i in clients:
         client = clients[i]
         client.envoyer("serv MAP:_" + MAPS[id], i, 0)
         #Send the new map crc:
         client.envoyer("map_crc " + self.crc, i, 0)
   
#   def send_to_client(self):
#      to_send = "murs "
#      for m in self.list:
#         x1 = m[0]
#         y1 = m[1]
#         x2 = m[2]
#         y2 = m[3]
#         if to_send=="murs ": to_send += str(x1)+","+str(y1)+","+str(x2)+","+str(y2)
#         else: to_send += ";"+str(x1)+","+str(y1)+","+str(x2)+","+str(y2)
#      return to_send
   
   def clean(self):
      self.list = []
      self.start_pos = []




class MasterServer(threading.Thread):
   
   def __init__(self):
      threading.Thread.__init__(self, target = self.run)
    
   def run(self):
      url = "http://pysnake.franceserv.com/masterserveur_serveur.php"
      while 1:
         log_debug("Request on the masterserver", "MasterServer")
         req = urllib2.Request(url)
         handle = urllib2.urlopen(req)
         time.sleep(30) #suppr du master si pas actif pdt 1min
      



class Client(threading.Thread):
   """Objet thread gerant le client"""
   
   def __init__(self, connexion, id):
      global conn_client
      global clients
      global ids
      threading.Thread.__init__(self, target = self.run) #on init le thread
      self.id = id
      self.instance_jeu = Jeu(self)
      self.instance_jeu.start()
      self.connexion = connexion
      self.chat_time = -1
   
   def envoyer(self, msg, id_voulu = -1, filtre = 1): # Si filtre == 1, on envois qu'aux ids[id] == 2
      msg += "|" * (LENGTH_MAX_SERVER - len(msg))
      if id_voulu == -1:
         for id in range(4):
            try: conn = conn_client[id]
            except KeyError: 0
            else:
               if filtre:
                  if ids[id] == 2:
                     try: conn_client[id].send(msg)
                     except socket.error:
                        log("Broken pipe", "Client's Connection")
                        self.connexion.close()
                        break
                  else: log_debug("Filtred for" + str(id), "Client's Connection")
               else:
                  try: conn_client[id].send(msg)
                  except socket.error:
                     log("Broken pipe", "Client's Connection")
                     self.connexion.close()
                     break
      else: 
         while 1:
            try:
               conn_client[id_voulu].send(msg)
            except KeyError:
               log("Connexion client pas encore prête...", "Client's Connection")
               time.sleep(0.1)
            except socket.error:
               log("Broken pipe", "Client's Connection")
               self.connexion.close()
               break
            else: break
   
   def say(self, n):
      dt = datetime.now()
      sec = dt.second
      if sec < self.chat_time: sec += 60
      if sec >= self.chat_time+TIME_BETWEEN_CHAT:
         self.chat_time = -1
      else:
         log_debug(str(self.id) + " wants to flood", "Client's Connection")
         self.envoyer("serv You're_not_allowed_to_flood_!", self.id, 0)
      if self.chat_time == -1:
         log_debug(self.nom + " (" + self.pseudo + ") want to say the " + str(n) + " sentence", "Client's Connection")
         msg = "say " + str(self.id) + " " + str(n)
         for i in conn_client:
            self.envoyer(msg, i)
         #On l'empèche de flooder:
         dt = datetime.now()
         sec = dt.second
         self.chat_time = sec
   
   def change_dir(self, dir):
      self.instance_jeu.change_dir(dir)
   
   def connect(self):
      for i in clients:
         c = clients[i]
         msg = "connect "+str(self.id)+" "+self.pseudo
         self.envoyer(msg, c.id)
         if c.id != self.id:
            msg = self.instance_jeu.send_to_client()
            self.envoyer(msg, c.id)
            log_debug("Snake of "+str(self.id)+" sent to "+str(c.id), "Client's Connection")
   
   def disconnect(self):
      msg = "disconnect "+str(self.id)
      for i in conn_client:
         self.envoyer(msg, i)
      log(str(self.id) + " disconnected", "Client's Connection")
   
   def response_joueurs(self):
      log_debug("Request joueurs received", "Client's Connection")
      for i in clients:
         c = clients[i]
         msg = "response joueur "+str(c.id)+" "+c.pseudo+" "+str(c.instance_jeu.score)
         self.envoyer(msg, self.id, 0)
         log_debug("Reply joueur of "+str(c.id)+" sent to "+str(self.id), "Client's Connection")
   
   def response_snakes(self):
      log_debug("Request snake received", "Client's Connection")
      for i in clients:
         c = clients[i]
         msg = "response " #réponse à la requête
         msg += c.instance_jeu.send_to_client()
         self.envoyer(msg, self.id, 0)
         log_debug("Reply snake of "+str(c.id)+" sent to "+str(self.id), "Client's Connection")
   
   def response_objets(self):
      log_debug("Request objets received", "Client's Connection")
      msg = "response "
      msg += objets.send_to_client()
      self.envoyer(msg, self.id, 0)
      log_debug("Reply objets sent to "+str(self.id), "Client's Connection")
   
   def response_map_crc(self):
      log_debug("Request map_crc received", "Client's Connection")
      msg = "map_crc " + murs.crc
      self.envoyer(msg, self.id, 0)
      log_debug("Reply map_crc sent to "+str(self.id), "Client's Connection")
   
   def response_map(self):
      log_debug("Request map received", "Client's Connection")
      log("Send the map", "Client's Connection")
      file = murs.map + "_" + murs.crc + ".map"
      for line in open("maps/" + file, "r").readlines():
         msg = "map " +file+" "+ line.replace(" ", "_")
         self.envoyer(msg, self.id, 0)
      log_debug("Reply map sent to "+str(self.id), "Client's Connection")
   
#   def response_murs(self):
#      log_debug("Request murs received", "Client's Connection")
#      msg = "response "
#      msg += murs.send_to_client()
#      self.envoyer(msg, self.id, 0)
#      log_debug("Reply murs sent to "+str(self.id), "Client's Connection")
   
   
   
   def check(self, msg_recu):
      msg = msg_recu.split(" ")
      #               /========================================================\
      #               |IndexError : paramètres non définis (exemple : "say")|
      #               |ValueError : paramètres incorrects (exemple : "say a")  |
      #               \========================================================/
      
      if msg[0] == "say": #"say {num}"
         if len(msg) != 2:
            print "Wrong number of parameters in : \""+msg_recu+"\" : "+str(len(msg)-1)+" for 1."
            return 0
         if msg[1] == "":
            print "Invalid server message : \""+msg_recu+"\""
            return 0
         try: int(msg[1])
         except ValueError:
            print "Wrong parameter in : \""+msg_recu+"\" : \""+msg[1]+"\" is not a number."
            return 0
         return 1
      
      elif msg[0] == "dir": #"dir {direction}"
         if len(msg) != 2:
            print "Wrong number of parameters in : \""+msg_recu+"\" : "+str(len(msg)-1)+" for 1."
            return 0
         if msg[1] == "":
            print "Invalid server message : \""+msg_recu+"\""
            return 0
         if msg[1] != "h" and msg[1] != "g" and msg[1] != "d" and msg[1] != "b":
            print "Unknown direction given in : \""+msg_recu+"\""
            return 0
         return 1
      
      elif msg[0] == "connect": #"connect {pseudo}"
         #if len(msg) != 2:
         #   print "Wrong number of parameters in : \""+msg_recu+"\" : \""+str(len(msg)-1)+"\" for 1."
         #   return 0
         #if msg[1] == "":
         #   print "Invalid server message in : \""+msg_recu+"\""
         #   return 0
         return 1
      
      elif msg[0] == "close": #"close"
         if len(msg) != 1:
            print "Wrong number of parameters in : \""+msg_recu+"\" : "+str(len(msg)-1)+" for 0."
            return 0
         return 1
      
      elif msg[0] == "request":
         if len(msg) != 2:
            print "Wrong number of parameters in : \""+msg_recu+"\" : "+str(len(msg)-1)+" for 1."
            return 0
         if msg[1] != "joueurs" and msg[1] != "snakes" and msg[1] != "objets" and msg[1] != "murs" and msg[1] != "all" and msg[1] != "map_crc" and msg[1] != "map":
            print "Unknown request given in : \""+msg_recu+"\""
            return 0
         return 1
      
      print "Unknown message : \""+msg_recu+"\""
      return 0
   
   
   def run(self): #partie éxécutée par le thread automatiquement
      self.pseudo = "Player"
      self.nom = self.getName() #nom du thread
      while True:
         try: msgClient=self.connexion.recv(LENGTH_MAX_CLIENT)
         except: 
            log("Le client a quitté pendant que le serveur écoutait son msg", "Client's Connection")
            break
         if msgClient == "":
            log("Connection interrompue", "Client's Connection")
            break
         #log_debug(msgClient)
         try: msgClient = msgClient[:msgClient.index('|')]
         except: pass #ça marche ça ?
         
         if self.check(msgClient):
            msgClient = msgClient.split(" ")
            
            if msgClient[0] == "close":
               to_send = "serv "+self.pseudo+"_has_left_:(."
               self.envoyer(to_send)
               self.disconnect()
               break
            
            elif msgClient[0] == "say":
               self.say(int(msgClient[1]))
            
            elif msgClient[0] == "dir": #"dir d" anciennement "move x y"
               dir = msgClient[1]
               self.change_dir(dir)
            
            elif msgClient[0] == "connect":
               self.pseudo = msgClient[1]
               #A NETTOYER :
               doit_pas_rester_ici_sous_peine_de_violentes_insultes = 0
               try: msgClient[2]
               except: log("His nickname : " + self.pseudo, "Client's Connection")
               else:
                  doit_pas_rester_ici_sous_peine_de_violentes_insultes = 1; print "?"
               if len(self.pseudo) > 12 or " " in self.pseudo:
                  doit_pas_rester_ici_sous_peine_de_violentes_insultes = 1; print "??"
               for i in self.pseudo:
                  if ord(i) >= 128:
                     doit_pas_rester_ici_sous_peine_de_violentes_insultes = 1; print "???"
               if doit_pas_rester_ici_sous_peine_de_violentes_insultes:
                  print "Celui là on le sort, pas de discution possible !"
                  break
               if self.pseudo == "":
                  self.pseudo = "Player_" + str(self.id)
               self.envoyer("OK "+str(self.id), self.id)
               self.envoyer("serv "+self.pseudo+"_joins_the_game.")
               self.envoyer("serv Welcome_!_Have_Fun_!_:)", self.id)
               #self.envoyer("serv You_can_post_a_message_for_"+str(TIME_BETWEEN_CHAT)+"_seconds", self.id)
               if TIME_BETWEEN_CHAT:
                  self.envoyer("serv ANTI_SPAM_ACTIVED:", self.id)
                  self.envoyer("serv "+str(TIME_BETWEEN_CHAT)+"_seconds_between_each_message", self.id)
               self.connect()
            
            elif msgClient[0] == "request":
            
               if msgClient[1] == "all":
                  log_debug("Request all received", "Client's Connection")
                  self.response_snakes()
                  self.response_joueurs()
                  self.response_objets()
                  self.response_map_crc()
                  ids[self.id] = 2
                  log_debug("Requetes envoyées à " +str(self.id)+ ", donc il passe en \"2\"", "Client's Connection")
               
               elif msgClient[1] == "joueurs":
                  self.response_joueurs()
               
               if msgClient[1] == "snakes":
                  self.response_snakes()
               
               elif msgClient[1] == "objets":
                  self.response_objets()
               
       #        elif msgClient[1] == "murs":
       #           self.response_murs()
               
               elif msgClient[1] == "map_crc":
                  self.response_map_crc()
               
               elif msgClient[1] == "map":
                  self.response_map()
      
      self.instance_jeu.deco = 1
      self.connexion.close()
      log_debug(str(self.id) + " deco")
      del conn_client[self.id]
      del clients[self.id].instance_jeu
      del clients[self.id]
      ids[self.id] = 0


class Quit(threading.Thread):
   def __init__(self, sock):
      threading.Thread.__init__(self, target = self.run)
      self.sock = sock
   
   def run(self):
      while 1:
         rp = raw_input("Enter \"debug\" to set on/off the debug mode\nEnter \"close\" to close\n")
         if rp.upper() == "DEBUG":
            global DEBUG
            DEBUG = not DEBUG
            log(DEBUG, "Debug")
         if rp.upper() == "CLOSE":
            for id in range(CLIENTS_MAX):
               try: 
                  c = clients[id]
                  c.envoyer("serv Server_shuts_down_:(")
                  c.envoyer("close", id, 0)
               except KeyError: 0
            break
      #Logout from masterserver:
      log_debug("Logout from masterserver:", "Quit", 1)
      url = "http://pysnake.franceserv.com/masterserveur_serveur_quit.php"
      req = urllib2.Request(url)
      handle = urllib2.urlopen(req)
      log_debug("Done", "")
      os._exit(0) # Solution miracle :D




def ip_ask(): #unused
   while 1:
      demande = raw_input("Enter IP (keep empty for \"127.0.0.1\" as IP): ")
      if demande != "":
         return demande
         break
      else: return "127.0.0.1"

def main():
   #ip = ip_ask()
   ip = "127.0.0.1" #et pas le choix :p
   port = 4000 #et pas le choix ! ;) ^^
   mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   log_debug(ip +" "+ str(port), "Bind ip")
   try: mySocket.bind((ip, port))
   except socket.error:
      log(socket.error, "Bind ip")
      log("Failure", "Bind ip")
      sys.exit()
   log("Ready")
   MasterServer().start()
   mySocket.listen(CLIENTS_MAX)
   global conn_client
   conn_client = {} #initialisation de la "dictionnaire" des clients
   global clients
   clients = {}
   global murs
   murs = Murs()
   global ids #par exemple : si le client d'id 1 se déconnecte, un nouveau client doit prendre l'id 1
   ids = ['', 0, 0, 0, 0] #liste les ids pris, 0=libre, 1=utilisé, 2=prêt à jouer!
   global objets
   objets = Objets()
   objets.start()
   global sending
   sending = 0
   Quit(mySocket).start()
   while True:
      connexion, addresse = mySocket.accept()
      log("New client : " + addresse[0])
      id = 0
      for i in range(CLIENTS_MAX+1):
         if ids[i] == 0:
            id = i
            break
      ids[id] = 1
      th = Client(connexion, id) #thread client
      clients[id] = th
      th.start() #démarre le run()
      conn_client[id] = connexion #on ajoute le client à la list
      #it = th.getName()
      if len(clients) == 1: #donc forcement l'id 1
         clients[1].instance_jeu.game_start()
   return 0

if __name__ == '__main__': main()
