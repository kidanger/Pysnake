#!/usr/bin/env python
# -*- coding:Utf-8 -*-


from client_needed import *
from update import *
import threading, sys, socket, urllib2, time, os
from datetime import datetime
from Tkinter import *

#Map's crc:
from crc import *


CASES_X = 32
CASES_Y = 24
TAILLE_CASE = 20 #changeable bien sûr

dir_ = os.getcwd() + "/"
dir = dir_ + "img/objets/"
SRC_OBJET = {}
SRC_OBJET[0] = dir + "pomme.gif"
SRC_OBJET[1] = dir + "accel.gif"
SRC_OBJET[2]= dir + "decel.gif"
SRC_OBJET[3] = dir + "nocontrol.gif"
SRC_OBJET[4] = dir + "demi-tour.gif"
SRC_OBJET[5] = dir + "arma-powa.gif"
SRC_OBJET[6] = dir + "apocalypse.gif"

dir = dir_ + "img/snakes/"
SRC_SNAKES = {}
COULEURS = []
for i in os.listdir(dir):
   COULEURS.append(i)
   SRC_SNAKES[i] = dir + i + "/"

dir = dir_ + "img/murs/"
SRC_MURS = dir + "murs.gif"
SRC_MURS_BIG = dir + "murs_big.gif"

LENGTH_MAX_SERVER = 256
LENGTH_MAX_CLIENT = 50

CLIENTS_MAX = 4
CHAT_MAX_MSG = 10



class Preappli():
   def __init__(self):
      self.Sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # On init dès içi la connection !
      self.fenetre = Tk()
      self.fenetre.title("Pysnake")
      self.fenetre.configure(width = 500, height = 500)

      #Nickname label:
      Label(self.fenetre, text = "Nickname : ").grid(row=3, column=0)
      
      #Some buttons:
      Button(self.fenetre, text = "Quit", command = sys.exit).grid(row=4, column = 0)
      self.update_button = Button(self.fenetre, text = "Update the game", fg = "red", bg = "black", command = self.update)
      self.fenetre.after(100, self.check_update)
      Button(self.fenetre, text = "Validate", command = self.valid).grid(row=3, column=2)
      Button(self.fenetre, text = "Refresh the list", command = self.actualise).grid(row=4,column=1)
      
      #Servermaster list
      self.f1 = Frame(self.fenetre)
      self.s1 = Scrollbar(self.f1)
      self.l1 = Listbox(self.f1)
      self.s1.config(command = self.l1.yview)
      self.l1.config(yscrollcommand = self.s1.set)
      self.l1.pack(side = LEFT, fill = Y)
      self.s1.pack(side = RIGHT, fill = Y)
      self.f1.grid(row=2, column=1)
      
      #IP entry:
      self.entry1 = Entry(self.fenetre)
      self.entry1.grid(row=1, column=1)
      self.entry1.insert(0, "127.0.0.1")
      
      #Nickname entry:
      self.entry2 = Entry(self.fenetre)
      self.entry2.grid(row=3, column=1)
      
      #Radio:
      self.v=IntVar()
      Radiobutton(self.fenetre, text="Log on the IP :", variable=self.v, value= 1).grid(row=1, column=0) #IP PRECISE
      Radiobutton(self.fenetre, text="Masterserver", variable=self.v, value= 2).grid(row=2, column=0) #MASTER
      self.v.set(2)
      self.l1.bind('<ButtonRelease-1>', self.clic)  #on associe l'évènement "relachement du bouton gauche de la souris" à la listbox
      self.clicked = 0
      
      #Loop:
      self.fenetre.after(100, self.actualise)
      self.fenetre.mainloop()

   def check_update(self):
      if check_for_update():
         self.update_button.grid(row = 4, column = 2)
      else:
         self.update_button.grid_forget()
   
   def update(self):
      do_update()
      self.check_update()

   def clic(self, evt):
       i=self.l1.curselection()  #Récupération de l'index de l'élément sélectionné
       self.clicked = self.l1.get(i)  #On retourne l'élément (une string) sélectionné
       print self.clicked

   def get_our_ip(self):
      the_url = "http://pysnake.franceserv.com/masterserveur_client_ip.php"
      req = urllib2.Request(the_url)
      handle = urllib2.urlopen(req)
      return handle.read()

   def valid(self):
      p = self.entry2.get()
      if p == "" or len(p) > 12: return 0
      for i in range(len(p)):
         if p[i] == " ": #HACKERS : Don't change this or the server won't accept you !
            print "Espaces : non permis !"
            return 0
         if ord(p[i]) >= 128:
            print "Caractère(s) non désiré(s) !"
            return 0
      if self.v.get() == 1:
         if self.entry1.get() == "": return 0
         wanted = 1
      elif self.v.get() == 2:
         wanted = 2
      if wanted == 1:
         try: self.Sock.connect((self.entry1.get(), 4000))
         except:
            return 0
         else:
            self.glob()
            self.connection = Connection(self.Sock, self.entry2.get())
            self.connection.start()
            self.fenetre.destroy()
            Application(self.connection)
      elif wanted == 2 and self.clicked != 0:
         try: ip = self.get_our_ip() #on empèche au client de se co à sa propre ip
         except:
            None
         else:
            if ip == self.clicked:
               self.clicked = "127.0.0.1"
         try:
            print "Connection à", self.clicked
            self.Sock.connect((self.clicked, 4000))
         except: return 0
         else: 
            self.glob()
            self.connection = Connection(self.Sock, self.entry2.get())
            self.connection.start()
            self.fenetre.destroy()
            appli = Application(self.connection)
   
   def glob(self):
      print "-OK-\nJoueurs :",
      global inst_joueurs
      inst_joueurs = Joueurs()
      print "Snakes :",
      global snakes
      snakes = {} #DICO ! des instances des snakes
      print "-OK-\nObjets :",
      global inst_objets
      inst_objets = Objets()
      print "-OK-\nMurs :",
      global inst_murs
      inst_murs = Murs()
      print "-OK-"
   
   def actualise(self):
      self.l1.delete(0, END)
      #Recuperer les serveurs depuis la page puis les inserer dans listbox
      the_url = "http://pysnake.franceserv.com/masterserveur_client.php"
      req = urllib2.Request(the_url)
      handle = urllib2.urlopen(req)
      the_page = handle.read()
      y,x=0,0
      for i in range(len(the_page)):
         if the_page[i] == " ":
            x+=1
            self.l1.insert(x, the_page[y:i])
            y=i+1


class Application():
   
   def __init__(self, connection):
      self.connection = connection
      self.marche = 1
      self.fen = Tk()
      self.fen.title('Pysnake')
      hauteur = 700
      largeur = 830
      xpos = 10
      ypos = 10
      self.fen.wm_geometry("%dx%d+%d+%d" % (largeur, hauteur, xpos, ypos))
      #self.list_pseudo_score = [[None, None], [None, None], [None, None], [None, None]] #liste des labels des pseudo
      self.list_pseudo_score = []
      for i in range(CLIENTS_MAX):
         self.list_pseudo_score.append([None, None])
      self.place_tout()
      self.affichage()
      self.fen.mainloop()
      self.marche = 0
      try: self.fen.destroy()
      except: print "..."
      self.connection.envoyer("close")
      self.connection.Sock.close() # On ferme la connection, ce qui "ferme" le thread
      sys.exit()
   
   def affichage(self):
      if self.marche == 0: return
      self.canevas.delete(ALL) # on nettoie, et on réaffiche tout
      self.affiche_murs()
      self.affiche_snakes()
      self.affiche_objets()
      self.chat_update()
      self.update_tableau() #Appelons tableau les pseudos & les scores
      self.fen.after(50, self.affichage) # Et c'est reparti au bout de 0.05 secs !
   
   def place_tout(self):
      #Frame pour l'affichage des joueurs:
      self.frame = Frame(self.fen)
      self.frame.grid(row=0,column=1)
         
      #Canevas
      self.canevas = Canvas(self.fen, bg="white", width=CASES_X*TAILLE_CASE, height=CASES_Y*TAILLE_CASE)
      self.canevas.grid(row = 0, column = 0)
      
      #Quitter
      Button(self.fen, text='Quit', command=self.fen.quit).grid(row=1,column=1)
      
      #Chat
      self.cnv = Canvas(self.fen)
      self.cnv.grid(row=1, column=0, sticky='nswe')
      self.frm = Frame(self.cnv)
      self.labels = []
      for i in range(CHAT_MAX_MSG):
         self.labels.append(None)
      for i in range(len(self.labels)):
         self.labels[i] = Label(self.frm, text= " ")
         self.labels[i].grid(row=i, sticky = W)
      self.chat_entry = Entry(self.frm)
      self.chat_entry.grid(row = i+1)
      self.fen.bind("<Return>", self.say)
      
      #Joueurs:
      Label(self.frm, text= "                                    ").grid(row = 0, column = 1)
      for i in range(CLIENTS_MAX): #Initialisation des labels pour les pseudo et score des joueurs
         self.list_pseudo_score[i][0] = Label(self.frm, text = "")
         self.list_pseudo_score[i][0].grid(row=i*2, column = 2)
         
         self.list_pseudo_score[i][1] = Label(self.frm, text = "")
         self.list_pseudo_score[i][1].grid(row=i+(i+1), column = 2)
      
      #Aide mémoire
      aide=[""]*len(PHRASES)
      for i in range(len(PHRASES)):
         aide[i] = 'F%s: "%s"' % (str(i+1), PHRASES[i])
         Label(self.frame, text = aide[i]).grid(column = 0, row = 10+i, sticky = W)
      
      self.cnv.create_window(0, 0, window=self.frm, anchor=NW)
      self.cnv.configure(scrollregion=self.cnv.bbox(ALL))
      
      #Events
      self.fen.bind("<Left>", self.connection.move)
      self.fen.bind("<Right>", self.connection.move)
      self.fen.bind("<Up>", self.connection.move)
      self.fen.bind("<Down>", self.connection.move)
      for i in range(len(PHRASES)):
         self.fen.bind('<F' + str(i+1) + '>', self.connection._say)
         
      #On init les images:
      self.image_murs = PhotoImage(file = SRC_MURS, master = self.canevas)
      self.image_murs_big = PhotoImage(file = SRC_MURS_BIG, master = self.canevas)
      self.image_objet = {}
      for i in range(7):
         self.image_objet[i] = PhotoImage(file = SRC_OBJET[i], master = self.canevas)
      self.image_snake = {}
      parties = ["corps", "tete_b", "tete_h", "tete_g", "tete_d"]
      for c in COULEURS:
         self.image_snake[c] = {}
         for p in parties:
            file = SRC_SNAKES[c] + p + ".gif"
            self.image_snake[c][p] = PhotoImage(file = file, master = self.canevas)
      self.frm.update()
      self.frame.update()
      self.fen.update()
   
   def say(self, event):
      s = self.chat_entry.get()
      if s != "":
         self.connection.say(s)
   
   def chat_update(self):
      #On reconfigure les labels
      for i in range(len(self.labels)):
         if inst_joueurs.texts[i][1] != "":
            id = inst_joueurs.texts[i][0]
            msg = inst_joueurs.texts[i][1]
            pseudo = ""
            couleur = "black"
            bg = "white"
            for j in inst_joueurs.list:
               if j[0] == id:
                  pseudo = j[1]
            if pseudo == "":
               pseudo = "unknown"
            if id != -1:
               try: 
                  snake = snakes[id]
               except KeyError:
                  0
               else:
                  couleur, bg = self.traduire(snake.couleur)
            else:
               pseudo = "SERVER"
            text = "<" + pseudo + "> " + msg
            self.labels[i].configure(text=text, fg=couleur, bg=bg)
            
      ## Pour etre sur que les dimensions sont calculees
      self.frm.update()
   
   
   def affiche_objets(self):
      objets = inst_objets.list #{id=>[x,y,type,id], id=>[x,y,type,id]}
      if objets == []:
         self.connection.send_request("objets")
         return 0
      ids = objets.keys()
      if ids == []: return
      last_id = ids[-1]
      for id in range(last_id+1):
      #for o in objets: #id
         try: o = objets[id] #[x,y,type,id]
         except KeyError: 0
         else:
            x1 = o[0]*TAILLE_CASE
            y1 = o[1]*TAILLE_CASE
            self.canevas.create_image(x1, y1, anchor = NW, image=self.image_objet[o[2]])
   
   def affiche_snakes(self):
      for id in range(CLIENTS_MAX):
         try: snake = snakes[id+1]

         except KeyError: 0
         else: # on affiche la tête après pour par qu'elle se retrouve sous la queue quelque fois
            dir = snake.direction
            couleur = snake.couleur
            tete = snake.tete #[x, y]
            x1_tete = tete[0] * TAILLE_CASE
            y1_tete = tete[1] * TAILLE_CASE
            self.canevas.create_image(x1_tete, y1_tete, anchor = NW, image=self.image_snake[couleur]['tete_'+dir])
            for queue in snake.queues: #[x, y]
               x1 = queue[0] * TAILLE_CASE
               y1 = queue[1] * TAILLE_CASE
               self.canevas.create_image(x1, y1, anchor = NW, image=self.image_snake[couleur]['corps'])
   
   def affiche_murs(self):
      if inst_murs.list == []:
         self.connection.send_request("map_crc")
         return 0
      for m in inst_murs.list:
         #Détéction de carré 2x2 murs :
         if m[2] - m[0] == 2 and m[3] - m[1] == 2:
            self.canevas.create_image(m[0]* TAILLE_CASE, m[1]* TAILLE_CASE, anchor = NW, image=self.image_murs_big)
         else:
            for x in range(m[0], m[2]+1):
               for y in range(m[1], m[3]+1):
                  x1 = x * TAILLE_CASE
                  y1 = y * TAILLE_CASE
                  self.canevas.create_image(x1, y1, anchor = NW, image=self.image_murs)

   def update_tableau(self):
      for i in range(CLIENTS_MAX):
         try: j = inst_joueurs.list[i]
         except:
            self.list_pseudo_score[i][0].configure(text = "")
            self.list_pseudo_score[i][1].configure(text = "")
         else:
            try:
               snake = snakes[i+1]
               couleur, bg = self.traduire(snake.couleur)
               self.list_pseudo_score[i][0].configure(text = j[1], fg = couleur, bg=bg)      #Affichage du pseudo du joueur en couleur
               self.list_pseudo_score[i][1].configure(text = "%s points" % str(j[2]))          #Affichage de son score
            except:
               self.list_pseudo_score[i][0].configure(text = j[1], fg = "black")      #Affichage du pseudo du joueur sans couleur
               self.list_pseudo_score[i][1].configure(text = "%s points" % str(j[2]))          #Affichage de son score

   def traduire(self, coul):
      if coul == "bleu": return "blue", "white"
      if coul == "rouge": return "red", "white"
      if coul == "vert": return "green", "white"
      if coul == "jaune": return "yellow", "black"
      if coul == "orange": return "orange", "white"
      if coul == "rose": return "pink", "black"
      if coul == "violet": return "purple", "white"




class Connection(threading.Thread): # (!) Ne pas confondre Sock (sous forme self.Sock) pour l'ancient "connection" et Connection (qui va être sous forme self.connection) pour l'instance de Connection
   
   def __init__(self, sock, pseudo):
      threading.Thread.__init__(self, target=self.run)
      self.Sock = sock
      self.pseudo = pseudo
      self.texts = [""]*15
      self.waiting_for_response = 0
      self.chat_time = -1
   
   def envoyer(self, message): #méthode pour envoyer tous les messages au serveur
      message += "|"*(LENGTH_MAX_CLIENT -len(message))
      self.Sock.send(message)
   
   def send_request(self, request):
      self.envoyer("request "+request)
   
   def _say(self, event):
      n = event.keysym[1:]
      n = PHRASES[int(n)-1]
      self.say(n)
   
   def say(self, phrase):
      dt = datetime.now()
      sec = dt.second
      if sec < self.chat_time: sec += 60
      if sec >= self.chat_time+1:
         self.chat_time = -1
      if self.chat_time == -1:
         self.envoyer("say "+phrase.replace(" ", "_"))
         dt = datetime.now()
         sec = dt.second
   
   def move(self, event):
      if event.keysym == "Up": dir="h"
      if event.keysym == "Left": dir="g"
      if event.keysym == "Right": dir="d"
      if event.keysym == "Down": dir="b"
      self.envoyer("dir "+dir)
   
   def decode_snake(self, msg):
      #exemple : msg = "1,2;1,3"
      s = msg.split(";") #["1,2", "1,3"]
      tete = s[0].split(",") #["1", "2"]
      queues = []
      for i in range(len(s)-1):
         queues.append(s[i+1].split(",")) #[[1,3]]
      return tete, queues
   
   
   
   def check(self, msg_recu):
      msg_recu = msg_recu[:msg_recu.index('|')]
      msg = msg_recu.split(" ")
      
      #               /========================================================\
      #               |IndexError : paramètres non définis (exemple : "say")   |
      #               |ValueError : paramètres incorrects (exemple : "say a")  |
      #               \========================================================/
      
      if msg[0] == "close": #"close"
         if len(msg) != 1:
            print "Wrong number of parameters in : \""+msg_recu+"\" : "+str(len(msg)-1)+" for 0."
            return 0
         return 1
      
      elif msg[0] == "say": #"say {id} {num}"
         if len(msg) != 3:
            print "Wrong number of parameters in : \""+msg_recu+"\" : "+str(len(msg)-1)+" for 2."
            return 0
         if msg[1] == "" or msg[2] == "":
            print "Invalid server message : \""+msg_recu+"\""
            return 0
         try:
            int(msg[1])
          #  int(msg[2])
         except ValueError:
            print "Wrong parameter in : \""+msg_recu+"\" : \""+msg[1]+"\" or \""+msg[2]+"\" is not a number."
            return 0
         return 1
      
      elif msg[0] == "serv": #"serv {phrase}"
         if len(msg) != 2:
            print "Wrong number of parameters in : \""+msg_recu+"\" : "+str(len(msg)-1)+" for 1."
            return 0
         if msg[1] == "":
            print "Invalid server message : \""+msg_recu+"\""
            return 0
         return 1
      
      elif msg[0] == "score": #"score {id} {score}"
         if len(msg) != 3:
            print "Wrong number of parameters in : \""+msg_recu+"\" : "+str(len(msg)-1)+" for 2."
            return 0
         if msg[1] == "" or msg[2] == "":
            print "Invalid server message : \""+msg_recu+"\""
            return 0
         try:
            int(msg[1])
            int(msg[2])
         except ValueError:
            print "Wrong parameter in : \""+msg_recu+"\" : \""+msg[1]+"\" or \""+msg[2]+"\" is not a number."
            return 0
         return 1
      
      elif msg[0] == "connect": #"connect {id} {pseudo}"
         if len(msg) != 3:
            print "Wrong number of parameters in : \""+msg_recu+"\" : \""+str(len(msg)-1)+"\" for 2."
            return 0
         if msg[1] == "" or msg[2] == "":
            print "Invalid server message : \""+msg_recu+"\""
            return 0
         try: int(msg[1])
         except ValueError:
            print "Wrong parameter in : \""+msg_recu+"\" : \""+msg[1]+"\" is not a number."
            return 0
         return 1
      
      elif msg[0] == "disconnect": #"disconnect {id}"
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
      
      elif msg[0] == "objets" or msg[0] == "ts": #"objets {x},{y},{type},{id};{x},{y},{type},{id}"
         if len(msg) != 2:
            print "Wrong number of parameters in : \""+msg_recu+"\" : "+str(len(msg)-1)+" for 1."
            return 0
         if msg[1] == "":
            print "Invalid server message : \""+msg_recu+"\""
            return 0
         if msg[1] == "EMPTY":
            return 1
         objets = msg[1].split(";") #["x,y,type,id", "x,y,type,id"]
         try:
            for o in objets:
               o = o.split(",")
               if len(o) != 4:
                  print "Wrong number of object parameters in : \""+msg_recu+"\" : "+str(len(o))+" for 4."
                  return 0
               int(o[0]) + int(o[1]) + int(o[2]) + int(o[3])
         except ValueError:
            print "Wrong parameter in : \""+msg_recu+"\" : x, y type or id is not a number."
            return 0
         return 1
      
      
      elif msg[0] == "move": #"move {id} {x} {y}"
         if len(msg) != 4:
            print "Wrong number of parameters in : \""+msg_recu+"\" : "+str(len(msg)-1)+" for 3."
            return 0
         if msg[1] == "" or msg[2] == "" or msg[3] == "":
            print "Invalid server message : \""+msg_recu+"\""
            return 0
         try: int(msg[1]) + int(msg[2]) + int(msg[3])
         except ValueError:
            print "Wrong parameter in : \""+msg_recu+"\" : \""+msg[1]+"\" or \""+msg[2]+"\" or \""+msg[3]+"\" is not a number."
            return 0
         try: snakes[int(msg[1])]
         except KeyError:
            print "Snake " + msg[1] + " not created."
            return 0
         return 1
           
      
      #snake : vérifier la couleur
      elif msg[0] == "snake" or msg[0] == "e": #"snake {id} {dir} {couleur} {x},{y};{x},{y}"
         if len(msg) != 5:
            print "Wrong number of parameters in : \""+msg_recu+"\" : "+str(len(msg)-1)+" for 4."
            return 0
         try:
            int(msg[1])
            snakes
         except ValueError:
            print "Wrong parameter in : \""+msg_recu+"\" : \""+msg[1]+"\" is not a number."
            return 0
         except NameError:
            print "Snake "+msg[1]+" not given in response snake."
            return 0
         if msg[2] != "g" and msg[2] != "h" and msg[2] != "d" and msg[2] != "b":
            print "Wrong direction in : \""+msg_recu+"\" : \""+msg[2]+"."
            return 0
         try: tete, queues = self.decode_snake(msg[4])
         except IndexError: 
            print "Undefined parameter(s) in : \""+msg_recu+"\""
            return 0
         try:
            if len(tete) != 2:
               print "Wrong number of head parameters in : \""+msg_recu+"\" : "+str(len(tete))+" for 2."
               return 0
            int(tete[0]) + int(tete[1])
            for q in queues: #x, y
               if len(q) != 2:
                  print "Wrong number of tail parameters in : \""+msg_recu+"\" : "+str(len(q))+" for 2."
                  return 0
               int(q[0]) + int(q[1])
         except ValueError:
            print "Wrong parameter in : \""+msg_recu+"\" : x or y is not a number."
            return 0
         return 1
      
      elif msg[0] == "OK":
         if len(msg) != 2:
            print "Wrong number of parameters in : \""+msg_recu+"\" : "+str(len(msg)-1)+" for 2."
            return 0
         try: int(msg[1])
         except:
            print "Invalid server message : \""+msg_recu+"\""
            return 0
         return 1
      
      elif msg[0] == "map_crc":
            if len(msg) != 2:
               print "Wrong number of parameters in : \""+msg_recu[9:]+"\" : "+str(len(msg)-1-1)+" for 3."
               return 0
            try: int(msg[1])
            except ValueError:
               print "Blabla.."
               return 0
            return 1
      
      elif msg[0] == "map":
         return 1
            
      elif msg[0] == "response":
         try: type = msg[1]
         except IndexError: 
            print "Undefined parameter(s) in : \""+msg_recu+"\""
            return 0
         if type == "":
            print "Invalid server message : \""+msg_recu+"\""
            return 0
         
         elif type == "joueur":
            if len(msg) != 5:
               print "Wrong number of parameters in : \""+msg_recu[9:]+"\" : "+str(len(msg)-1-1)+" for 3."
               return 0
            try: int(msg[2]) + int(msg[4])
            except ValueError:
               print "Wrong parameter in : \""+msg_recu[9:]+"\" : \""+msg[2]+"\" or \""+msg[4]+"\" is not a number."
               return 0
            return 1
         
         elif type == "murs":
            if len(msg) != 3:
               print "Wrong number of parameters in : \""+msg_recu[9:]+"\" : "+str(len(msg)-1-1)+" for 1."
               return 0
            murs = msg[2].split(";") #["x1,y1,x2,y2", "x1,y1,x2,y2"]
            try:
               for m in murs:
                  m = m.split(",")
                  if len(m) != 4:
                     print "Wrong number of wall parameters in : \""+msg_recu+"\" : "+str(len(m))+" for 4."
                     return 0
                  int(m[0]) + int(m[1]) + int(m[2]) + int(m[3])
            except ValueError:
               print "Wrong parameter in : \""+msg_recu+"\" : x1, y1, x2 or y2 is not a number."
               return 0
            return 1
         
         elif type == "snake": #"response snake {id} {dir} {couleur} {x},{y};{x},{y}"
            if len(msg) != 6:
               print "Wrong number of parameters in : \""+msg_recu+"\" : "+str(len(msg)-1)+" for 5."
               return 0
            try:
               int(msg[2])
               snakes
            except ValueError:
               print "Wrong parameter in : \""+msg_recu+"\" : \""+msg[2]+"\" is not a number."
               return 0
            except NameError:
               print "Snake "+msg[2]+" not given in response snake."
               return 0
            if msg[3] != "g" and msg[3] != "h" and msg[3] != "d" and msg[3] != "b":
               print "Wrong direction in : \""+msg_recu+"\" : \""+msg[3]+"."
               return 0
            try: tete, queues = self.decode_snake(msg[5])
            except IndexError: 
               print "Undefined parameter(s) in : \""+msg_recu+"\""
               return 0
            try:
               if len(tete) != 2:
                  print "Wrong number of head parameters in : \""+msg_recu+"\" : "+str(len(tete))+" for 2."
                  return 0
               int(tete[0]) + int(tete[1])
               for q in queues: #x, y
                  if len(q) != 2:
                     print "Wrong number of tail parameters in : \""+msg_recu+"\" : "+str(len(q))+" for 2."
                     return 0
                  int(q[0]) + int(q[1])
            except ValueError:
               print "Wrong parameter in : \""+msg_recu+"\" : x or y is not a number."
               return 0
               
            return 1
            
         elif type == "objets": ##############Eh ? mouais faudra que je fasse le quasi copié/collé
            return 1
            
         else:
            print "Unknown response given in : \""+msg_recu+"\""
            return 0
      
      print "Unknown message : \""+msg_recu+"\""
      if self.waiting_for_response == 1: return 0
      for param in msg: #"1,2,3,4;1,2,3,4"
         trucs = param.split(";") #["1,2,3,4", ...]
         for t in trucs: #"1,2,3,4"
            if trucs.index(t) != 0: #le 1er peut etre coupé donc faux
               t = t.split(",")
               if len(t) == 4: #p-e un objet
                  self.send_request("objets")
                  self.waiting_for_response = 1
                  return 0
               elif len(t) == 2: #p-e un snake
                  self.send_request("snakes")
                  self.waiting_for_response = 1
                  return 0
      return 0
   
   
   
   def run(self):
      time.sleep(0.1)
      self.envoyer("connect " + self.pseudo)
      while 1:
         
         try: msg_recu = self.Sock.recv(LENGTH_MAX_SERVER)
         except:
            print "Connexion interrompue avec le serveur"
            break
         if msg_recu == "": break
         #print msg_recu
         
         if "|" in msg_recu and self.check(msg_recu):
            msg_recu = msg_recu[:msg_recu.index('|')]
            msg_recu = msg_recu.split(" ")
            
            if msg_recu[0] == "close":
               print "Déconnecté par le serveur"
               break
            
            if msg_recu[0] == "say":
               qui = msg_recu[1] #identifiant de celui qui parle
               quoi = msg_recu[2].replace("_", " ") #phrase dite
               inst_joueurs.dit(qui, quoi)
            
            elif msg_recu[0] == "score":
               qui = msg_recu[1]
               combien = msg_recu[2]
               inst_joueurs.change_score(qui, combien)
            
            elif msg_recu[0] == "serv":
               phrase = msg_recu[1]
               phrase = phrase.replace("_", " ")
               print phrase
               inst_joueurs.dit(0, phrase)
            
            elif msg_recu[0] == "OK":
               self.id = int(msg_recu[1])
               print "OK recu, on est l'id", self.id
               self.send_request("all")
            
            elif msg_recu[0] == "connect":
               qui = msg_recu[1]
               pseudo = msg_recu[2]
               if pseudo != self.pseudo: #sinon donné dans request
                  print "Nouveau joueur:", pseudo
                  inst_joueurs.ajout(qui, pseudo)
            
            elif msg_recu[0] == "objets" or msg_recu[0] == "ts":
               objets = msg_recu[1].split(";") #["x,y,type,id", "x,y,type,id"] ou ["EMPTY"]
               inst_objets.update(objets)
            
            elif msg_recu[0] == "disconnect":
               id = int(msg_recu[1])
               if id == self.id: break
               else:
                  print msg_recu[1]+" deco"
                  inst_joueurs.suppr(id)
                  try: snakes[id]
                  except KeyError: 0
                  else:
                     snakes[id].suppr()
                     del snakes[id]
            
            elif msg_recu[0] == "move":
               id = int(msg_recu[1])
               x, y = int(msg_recu[2]), int(msg_recu[3])
               snakes[id].move(x, y)
            
            elif msg_recu[0] == "snake" or msg_recu[0] == "e": #delete the "e" ?
               id = int(msg_recu[1])
               dir = msg_recu[2]
               couleur = msg_recu[3]
               tete, queues = self.decode_snake(msg_recu[4])
               try: snakes[id].update(dir, couleur, tete, queues)
               except KeyError:
                  snakes[id] = Snake(dir, couleur, tete, queues)
            
            elif msg_recu[0] == "map_crc":
               crc = msg_recu[1]
               nom = inst_murs.got_map(crc)
               if nom and inst_murs.check_map(nom):
                  inst_murs.load_map(nom)
               else:
                  self.envoyer("request map")
            
            elif msg_recu[0] == "map":
               if not inst_murs.check_map(msg_recu[1]):
                  open("maps/" +msg_recu[1], "a").write(msg_recu[2].replace("_", " "))
            
            elif msg_recu[0] == "response":
               
               if msg_recu[1] == "snake":
                  print "réponse à la requête snake reçue"
                  id = int(msg_recu[2])
                  dir = msg_recu[3]
                  couleur = msg_recu[4]
                  tete, queues = self.decode_snake(msg_recu[5])
                  snakes[id] = Snake(dir, couleur, tete, queues)
                  self.waiting_for_response = 0
               
               elif msg_recu[1] == "joueur":
                  print "réponse à la requête joueur reçue"
                  #exemple : msg_recu = "response joueur 1 test"
                  id = int(msg_recu[2])
                  pseudo = msg_recu[3]
                  score = msg_recu[4]
                  inst_joueurs.ajout(id, pseudo, score)
               
               elif msg_recu[1] == "objets":
                  print "réponse à la requête objets reçue"
                  #exemple : msg_recu = "response objets x,y,type,id;x,y,type,id"
                  objets = msg_recu[2].split(";") #["x,y,type,id", "x,y,type,id"]
                  inst_objets.update(objets)
                  self.waiting_for_response = 0
               
           #    elif msg_recu[1] == "murs": #To remove
           #       print "réponse à la requête murs reçue"
           #       #exemple : msg_recu = "response murs x1,y1,x2,y2;x1,y1,x2,y2"
           #       murs = msg_recu[2].split(";") #["x1,y1,x2,y2", "x1,y1,x2,y2"]
           #       inst_murs.update(murs)
               
      
      
      print "Connection fermée"
      self.co = 0
      self.Sock.close()



if __name__ == "__main__": Preappli()
