#!/usr/bin/env python
# -*- coding:Utf-8 -*-

PORT = 4000
IP = "192.168.1.20"

import sys, socket, threading

class FalseMsg(threading.Thread):
   def __init__(self, connection):
      self.connection = connection
      threading.Thread.__init__(self)
   
   def send(self, msg):
      global conn_client
      for i in conn_client:
         conn_client[i].send(msg)
   
   def run(self):
      while 1:
         msg = raw_input('msg ?')
         self.send(msg)


class Jeu(threading.Thread): #reste les fonctions solide, bouffe et snake, ce qui nécessite de faire d'autres classes...

   def __init__(self):
      global conn_client
      threading.Thread.__init__(self)
      self.direction = "h"
      self.tete = (1, 1)
      self.queues = []
      self.queues.append((1, 2))
      self.queues.append((1, 3))
      self.queues.append((1, 4))
      
   def run(self):
      while True:
         print "Game !"


   def check(self, x, y)
      if solide(x, y): return "die"
      if bouffe(x, y): return "eat"
      if snake(x, y): return "hit"
      return 0
   
   
   def solide(self, x, y):
      #murs...


   def bouffe(self, x, y):
      #bouffe...


   def snake(self, x, y):
      #snakes... #vérifier pour TOUS les snakes !


   def change_dir(self, dir)
   
      direction = dir #g, h, d, b
      if self.direction == direction: #le snake va déjà dans cette direction
         return 0
         
      if direction == "g": #gauche      
         if self.direction == "d": return 0 #on ne peut pas aller dans la direction opposée
         self.tete[0] -= 1
         self.tete[1] += 0
         self.direction = "g"
      
      if direction == "h": #haut      
         if self.direction == "b": return 0 #on ne peut pas aller dans la direction opposée
         self.tete[0] += 0
         self.tete[1] -= 1
         self.direction = "h"
      
      if direction == "d": #droite      
         if self.direction == "g": return 0 #on ne peut pas aller dans la direction opposée
         self.tete[0] += 1
         self.tete[1] += 0
         self.direction = "d"
      
      if direction == "b": #bas
      
         if self.direction == "h": return 0 #on ne peut pas aller dans la direction opposée
         self.tete[0] += 0
         self.tete[1] += 1
         self.direction = "b"
      
      #chaque queue prend la place de la précédente :
      for i in range(len(self.queues)):
         if i == 0: #si c'est la 1ère queue
            0 #pareil qu'après en remplaçant self.queues[i-1] par self.tete
         else:
            diff_x = self.queues[i][0] - self.queues[i-1][1]
            diff_y = self.queues[i][1] - self.queues[i-1][1]
            if diff_x == 1: #la queue d'avant est à gauche de celle-ci
               self.queues[i][0] -= 1
            elif diff_x == -1: #la queue d'avant est à droite de celle-ci
               self.queues[i][0] += 1
            elif diff_y == 1: #la queue d'avant est en haut de celle-ci
               self.queues[i][1] -= 1
            else: #la queue d'avant est en bas de celle-ci
               self.queues[i][1] += 1
      
      check = self.check(self.tete_x, self.tete_y): #si prend un mur, de la bouffe, ou un snake
      if check: return check
      
      return 1





class Client(threading.Thread):

   """Objet thread gerant le client"""
   def __init__(self, connexion, id):
      global conn_client
      threading.Thread.__init__(self, target = self.run) # on init le thread
      self.connexion = connexion
      self.id = id
     
   def say(self, n):
      print self.nom, "(", self.pseudo, ") want to say the", n, "sentence"   
      msg = "say " + str(self.id) + " " + str(n)
      for i in conn_client:
         conn_client[i].send(msg)

   def change_dir(self, dir):
      print self.nom, ": dir = ", dir
      Jeu.change_dir(dir)
      ###A FAIRE###
      #Change la direction du joueur#
      #Provisoire: Envois "machin change de dir"
      # pour tester !
      # Apres: il faudra que le serveur calcule les nouvelles positions et les envois, mais PAS pas la !!!
      # => Jeu.bouge(dir) ?
          
      msg = self.nom + " change sa direction: " + dir
      for i in conn_client:
         conn_client[i].send(msg)

     def run(self): #partie executee par le thread automatiquement
          self.pseudo = "Unknown"
          self.nom = self.getName() #nom du thread
          self.id = 0
          while True:
               msgClient=self.connexion.recv(1024)
               msg Client = msgClient.split(" ")
               if msgClient[0] == "close" or msgClient == "": break
               elif msgClient[0] == "say":
                    self.say(int(msgClient[1:]))
               elif msgClient[0] == "move":
                    self.change_dir(str(msgClient[1])) #dir (g, h, d, b)
               elif msgClient[0] == "pseudo":
                    self.pseudo = msgClient[1]
                    ####...####
                    print self.pseudo
                    
               
          self.connexion.close()
          del conn_client[self.nom]
          print self.nom, "deco"

def main():
	mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
	     mySocket.bind((IP, PORT))
	except socket.error:
	     print "Erreur"
	     sys.exit()
	print "Pret"
	thFalseMsg = FalseMsg(mySocket)
	thFalseMsg.start()
	mySocket.listen(4) #on accepte 4 clients max
	global conn_client
	conn_client={} #initialisation de la "dictionnaire" des clients
	id = 0
	while True:
	     connexion, addresse = mySocket.accept()
	     id += 1
	     th = Client(connexion, id) #thread client
	     th.start() #démmare le run()
	     it = th.getName()
	     conn_client[it] = connexion #on ajoute le client a la liste
	     print it, "connecte", "ip:", addresse
	     if id < 0: Jeu(connection).start()
	return 0

if __name__ == '__main__': main()
