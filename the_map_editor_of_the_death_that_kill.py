#!/usr/bin/env python
# -*- coding:Utf-8 -*-


#TODO :
#RIEN :)

#DOC : http://gnuprog.info/prog/python/pwidget.php


import sys, os, ConfigParser
from Tkinter import *


CASES_X = 32
CASES_Y = 24
TAILLE_CASE = 20
C_MUR = "grey"
C_QUEUE = "black"
MAPS_DIR = os.getcwd() + "/maps/"
COULEURS = ["blue", "red", "green", "yellow", "orange", "pink", "purple"]







class Application():
   
   
   def __init__(self):
      global murs
      murs = Murs()
      global start_pos
      start_pos = Start_Pos()
      self.map_name = ""
      self.holding = None #le réinit quand nv_map/load_map/close_map ?
   
   
   def initialize(self):
      murs.initialize()
      start_pos.initialize(4) #4 joueurs
      self.set_maping(1) #map créée
      self.set_saved(0) #map non sauvegardée
   
   
   
   def set_maping(self, maping):
      self.maping = maping
      if maping == 0: s = "disabled"
      else: s = "normal"
      self.menu_options.entryconfigure("Chose Name", state=s)
      self.menu_options.entryconfigure("Chose Players Number", state=s)
      self.menu_options.entryconfigure("Add Map to Server Config", state=s)
      self.menu_map.entryconfigure("Save", state=s)
      self.menu_map.entryconfigure("Close", state=s)
      self.menu_edit.entryconfigure("New Wall", state=s)
      self.menu_edit.entryconfigure("Remove Wall", state=s)
      self.menu_edit.entryconfigure("Modify Wall", state=s)
      self.menu_edit.entryconfigure("Define Start Position", state=s)
      self.bouton_new.configure(state=s)
      self.bouton_remove.configure(state=s)
      self.bouton_modify.configure(state=s)
      self.bouton_define.configure(state=s)
   
   
   def set_saved(self, saved):
      self.saved = saved
      if saved == 0: s = "normal"
      else: s = "disabled"
      self.menu_map.entryconfigure("Save", state=s)
   
   
   def message(self, msg):
      self.fenetre_msg = Toplevel()
      self.fenetre_msg.title("Pysnake Map Editor")
      self.fenetre_msg.grab_set()
      self.fenetre_msg.focus_set()
      
      Label(self.fenetre_msg, text=msg).pack(side=TOP, pady=3)
      Button(self.fenetre_msg, text="OK", command=self.fenetre_msg.quit).pack(side=BOTTOM, pady=3)
      
      self.fenetre_msg.mainloop()
      
      try: self.fenetre_msg.destroy()
      except: 0
   
   
   
   def main(self):
      self.fenetre_jeu = Tk()
      self.fenetre_jeu.title("Pysnake Map Editor")
      self.fenetre_jeu.grab_set()
      self.fenetre_jeu.focus_set()
      
      #Création de la barre de menu :
      menus = Menu(self.fenetre_jeu)
      
      #Création du menu Options :
      options = Menu(menus, tearoff=0)
      menus.add_cascade(label="Options", menu=options, underline=0)
      options.add_command(label="Chose Name", command=self.menu_options_chose, underline=6)
      options.add_command(label="Chose Players Number", command=self.menu_options_players, underline=6)
      options.add_command(label="Add Map to Server Config", command=self.menu_options_add, underline=0)
      options.add_command(label="Quit", command=self.menu_options_quit, accelerator="Ctrl+Q", underline=0)
      self.fenetre_jeu.bind("<Control-q>", sys.exit)
      self.fenetre_jeu.bind("<Control-Q>", sys.exit)
      self.menu_options = options
      
      
      #Création du menu Map :
      map = Menu(menus, tearoff=0)
      menus.add_cascade(label="Map", menu=map, underline=0)
      map.add_command(label="New", command=self.menu_map_new, accelerator="Ctrl+N", underline=0)
      self.fenetre_jeu.bind("<Control-n>", self.menu_map_new)
      self.fenetre_jeu.bind("<Control-N>", self.menu_map_new)
      map.add_command(label="Load", command=self.menu_map_load, accelerator="Ctrl+O", underline=0)
      self.fenetre_jeu.bind("<Control-o>", self.menu_map_load)
      self.fenetre_jeu.bind("<Control-O>", self.menu_map_load)
      map.add_command(label="Save", command=self.menu_map_save, accelerator="Ctrl+S", underline=0)
      self.fenetre_jeu.bind("<Control-s>", self.menu_map_save)
      self.fenetre_jeu.bind("<Control-S>", self.menu_map_save)
      map.add_command(label="Close", command=self.menu_map_close, accelerator="Ctrl+W", underline=0)
      self.fenetre_jeu.bind("<Control-w>", self.menu_map_close)
      self.fenetre_jeu.bind("<Control-W>", self.menu_map_close)
      self.menu_map = map
      
      #Création du menu Edit :
      edit = Menu(menus, tearoff=0)
      menus.add_cascade(label="Edit", menu=edit, underline=0)
      edit.add_command(label="New Wall", command=self.menu_edit_new, underline=0)
      edit.add_command(label="Remove Wall", command=self.menu_edit_remove, underline=0)
      edit.add_command(label="Modify Wall", command=self.menu_edit_modify, underline=0)
      edit.add_command(label="Define Start Position", command=self.menu_edit_define, underline=0)
      self.menu_edit = edit
      
      self.fenetre_jeu.config(menu=menus)
      
      self.canevas = Canvas(self.fenetre_jeu, bg="white", width=CASES_X*TAILLE_CASE, height=CASES_Y*TAILLE_CASE)
      self.canevas.grid(row=0, padx=0)
      
      self.canevas.bind('<ButtonRelease-3>', self.clic_droit)
      self.canevas.bind('<Button-1>', self.start_holding)
      self.canevas.bind('<ButtonRelease-1>', self.stop_holding)
      
      frame = Frame(self.fenetre_jeu)
      
      self.bouton_new = Button(frame, text="New Wall", command=self.menu_edit_new)
      self.bouton_new.pack(side=LEFT, padx=10, pady=5)
      
      self.bouton_remove = Button(frame, text="Remove Wall", command=self.menu_edit_remove)
      self.bouton_remove.pack(side=LEFT, padx=10, pady=5)
      
      self.bouton_modify = Button(frame, text="Modify Wall", command=self.menu_edit_modify)
      self.bouton_modify.pack(side=LEFT, padx=10, pady=5)
      
      self.bouton_define = Button(frame, text="Define Start Position", command=self.menu_edit_define)
      self.bouton_define.pack(side=LEFT, padx=10, pady=5)
      
      frame.grid(row=1)
      
      self.affiche()
      
      self.set_maping(0) #pas de map créée/chargée
      self.set_saved(1) #pas de map
      
      self.fenetre_jeu.mainloop()
      
      try: self.fenetre_jeu.destroy()
      except: 0
   
   
   
   def element(self, mouse_x, mouse_y):
      case_x = mouse_x/TAILLE_CASE
      case_y = mouse_y/TAILLE_CASE
      print "case_x : "+str(case_x) + ", case_y : " + str(case_y)
      for i_j in range(len(start_pos.list)):
         j = start_pos.list[i_j]
         if case_x == j[2][0] and case_y == j[2][1]:
            return ["tete", i_j]
         for i in range(len(j[3:])):
            i += 3
            if case_x == j[i][0] and case_y == j[i][1]:
               return ["queue", i_j, i]
      for i in range(len(murs.list)):
         xs = range(murs.list[i][0], murs.list[i][2]+1)
         ys = range(murs.list[i][1], murs.list[i][3]+1)
         if (case_x in xs) and (case_y in ys):
            return ["mur", i, case_x, case_y]
      return None
   
   def clic_droit(self, event):
      e = self.element(event.x, event.y)
      if e == None: return
      if e[0] == "mur":
         del murs.list[e[1]]
         self.affiche()
      elif e[0] == "tete":
         self.start_pos2(e[1])
      elif e[0] == "queue":
         del start_pos.list[e[1]][e[2]]
         self.affiche()
   
   def start_holding(self, event):
      e = self.element(event.x, event.y)
      self.holding = e
   
   def stop_holding(self, event):
      case_x = event.x/TAILLE_CASE
      case_y = event.y/TAILLE_CASE
      coords = [case_x, case_y]
      h = self.holding
      if h == None: return
      if h[0] == "mur":
         m = murs.list[h[1]]
         dif_x = case_x-h[2]
         dif_y = case_y-h[3]
         m[0] += dif_x
         m[1] += dif_y
         m[2] += dif_x
         m[3] += dif_y
         murs.modif(h[1], m)
      elif h[0] == "tete":
         start_pos.modif(h[1], 2, coords)
      elif h[0] == "queue":
         start_pos.modif(h[1], h[2], coords)
   
   
   
   def menu_options_chose(self):
      self.fenetre_name = Toplevel()
      self.fenetre_name.title("Pysnake Map Editor")
      self.fenetre_name.grab_set()
      self.fenetre_name.focus_set()
      
      name = Entry(self.fenetre_name, width=12)
      name.insert(0, self.map_name)
      name.grid(row=0, column=1)
      
      ok = Button(self.fenetre_name, text="OK", command=lambda e=name: self.change_name(e))
      ok.grid(row=1, column=0, pady=5)
      
      cancel = Button(self.fenetre_name, text="Cancel", command=self.fenetre_name.quit)
      cancel.grid(row=1, column=2, pady=5)
      
      self.fenetre_name.mainloop()
      
      try: self.fenetre_name.destroy()
      except: 0
   
   def change_name(self, entry):
      name = entry.get()
      if name == "": return
      maps = os.listdir(MAPS_DIR)
      if name in maps and self.verif_chose(name) == 0: return #si veut pas remplacer fichier
      self.map_name = name
      self.set_saved(0) #pas sauvegardée
      self.fenetre_name.quit()
   
   
   def menu_options_players(self):
      self.fenetre_players = Toplevel()
      self.fenetre_players.title("Pysnake Map Editor")
      self.fenetre_players.grab_set()
      self.fenetre_players.focus_set()
      
      number = Entry(self.fenetre_players, width=1)
      number.insert(0, len(start_pos.list))
      number.grid(row=0, column=0, pady=3, padx=3)
      
      ok = Button(self.fenetre_players, text="OK", command=lambda e=number: self.change_number(e))
      ok.grid(row=1, column=0, pady=3, padx=3)
      
      cancel = Button(self.fenetre_players, text="Cancel", command=self.fenetre_players.quit)
      cancel.grid(row=1, column=1, pady=3, padx=3)
      
      self.fenetre_players.mainloop()
      
      try: self.fenetre_players.destroy()
      except: 0
   
   
   def change_number(self, entry):
      number = entry.get()
      if number == "": return
      try: start_pos.number(int(number))
      except ValueError: return
      self.fenetre_players.quit()
   
   
   def menu_options_add(self):
      config = ConfigParser.RawConfigParser()
      try: config.read("config")
      except:
         self.message("Can't find server config.")
         return
      
      if self.map_name == "":
         self.menu_map_save()
         if self.map_name == "": #Cancel
            self.message("Map not added to server config.")
            return
      
      maps = eval(config.get("Game", "maps"))
      if self.map_name in maps:
         self.message("Map already in server config.")
         return
      
      maps.append(self.map_name)
      config.set("Game", "maps", maps)
      file = open("config", "wb")
      config.write()
      self.message("Map added to server config.")
   
   
   def menu_options_quit(self):
      if self.verif_save():
         sys.exit()
   
   
   
   def verif_chose(self, name): #quand on souhaite changer le nom d'une map, vérifie si ce nom n'existe pas déjà
      self.fen_verif = Toplevel()
      self.fen_verif.title("Pysnake Map Editor")
      self.fen_verif.grab_set()
      self.fen_verif.focus_set()
      
      Label(self.fen_verif, text=name+" already exists. Would you replace it when saved ?").grid(row=0, column=0)
      self.choix = 0
      
      frame = Frame(self.fen_verif)
      
      oui = Button(frame, text="Yes", command=lambda c=0: self.verif_chose2(c))
      oui.pack(side=LEFT, padx=10, pady=5)
      
      non = Button(frame, text="Cancel", command=lambda c=1: self.verif_chose2(c))
      non.pack(side=LEFT, padx=10, pady=5)
      
      frame.grid(row=1, column=0)
      
      self.fen_verif.mainloop()
      
      try: self.fen_verif.destroy()
      except: return 0 #si on ferme la fenetre c'est comme si on annule
      return self.choix
   
   def verif_chose2(self, c):
      if c == 0: #oui
         self.choix = 1
      elif c == 1: #annuler
         self.choix = 0
      self.fen_verif.quit()
   
   
   
   
   def menu_map_new(self, event=0):
      if self.menu_map_close():
         self.initialize()
         self.affiche()
   
   
   def menu_map_load(self, event=0):
      self.fenetre_load = Toplevel()
      self.fenetre_load.title("Pysnake Map Editor")
      self.fenetre_load.grab_set()
      self.fenetre_load.focus_set()
      
      frame = Frame(self.fenetre_load)
      scrollbar = Scrollbar(frame)
      self.listbox = Listbox(frame)
      scrollbar.config(command = self.listbox.yview)
      self.listbox.config(yscrollcommand = scrollbar.set)
      self.listbox.pack(side = LEFT, fill = Y)
      scrollbar.pack(side = RIGHT, fill = Y)
      frame.grid(row=0, column=1)
      self.listbox.bind('<ButtonRelease-1>', self.clic)
      self.actualise_load_map()
      
      modify = Button(self.fenetre_load, text="Load", command=self.load)
      modify.grid(row=1, column=0, pady=5)
      
      modify = Button(self.fenetre_load, text="Refresh", command=self.actualise_load_map)
      modify.grid(row=1, column=1, pady=5)
      
      cancel = Button(self.fenetre_load, text="Cancel", command=self.fenetre_load.quit)
      cancel.grid(row=1, column=2, pady=5)
      
      self.fenetre_load.mainloop()
      
      try: self.fenetre_load.destroy()
      except: 0
   
   def actualise_load_map(self):
      self.clicked = -1
      self.listbox.delete(0, END)
      list = os.listdir(MAPS_DIR)
      for i in range(len(list)):
         self.listbox.insert(i, list[i])
   
   def load(self):
      if self.menu_map_close():
         i = self.clicked
         if i == -1: return
         filename = self.listbox.get(i)
         if murs.load(filename) == 0: return #murs inlisables
         if start_pos.load(filename) == 0: return #start pos inlisables
         print "Loaded : "+filename
         self.map_name = filename
         try: self.fenetre_load.destroy()
         except: 0
         self.affiche()
         self.set_maping(1)
         self.set_saved(1) #sauvegardée
   
   
   def menu_map_close(self, event=0):
      if self.verif_save():
         self.__init__()
         self.affiche()
         self.set_maping(0) #pas de map
         self.set_saved(1) #pas de map
         return 1
      return 0
   
   
   def menu_map_save(self, event=0):
      dir = "maps/"
      if self.map_name == "": #map non loadée
         self.menu_options_chose()
         if self.map_name == "": #Cancel
            return
      f = file(dir + self.map_name, "w")
      to_write = "[Murs]"
      for i in range(len(murs.list)):
         to_write += "\nmurs" + str(i+1) + " = [" + murs.str(i) + "]"
      to_write += "\n\n[StartPos]"
      for id in range(len(start_pos.list)):
         to_write += "\njoueur" + str(id+1) + " = ["
         j = start_pos.list[id]
         for i in j:
            if j.index(i) == 0: #couleur
               to_write += "\""+i+"\""
            elif j.index(i) == 1: #direction
               to_write += ", \""+i+"\""
            else: #tête ou queue
               to_write += ", [" + str(i[0]) + ", " + str(i[1]) + "]"
         to_write += "]"
      f.write(to_write)
      f.close()
      self.set_saved(1) #sauvegardée
   
   
   
   def verif_save(self): #quand on souhaite fermer une map, vérifie si celle-ci a bien été sauvegardée
      if self.maping == 0: return 1 #tu peux y aller toute façon y a rien à fermer ;)
      if self.saved == 1: return 1 #déjà sauvegardée
      
      self.fen_verif = Toplevel()
      self.fen_verif.title("Pysnake Map Editor")
      self.fen_verif.grab_set()
      self.fen_verif.focus_set()
      
      Label(self.fen_verif, text="Save changes ?").grid(row=0, column=0)
      self.choix = 0
      
      frame = Frame(self.fen_verif)
      
      oui = Button(frame, text="Yes", command=lambda c=0: self.verif_save2(c))
      oui.pack(side=LEFT, padx=10, pady=5)
      
      non = Button(frame, text="No", command=lambda c=1: self.verif_save2(c))
      non.pack(side=LEFT, padx=10, pady=5)
      
      annuler = Button(frame, text="Cancel", command=lambda c=2: self.verif_save2(c))
      annuler.pack(side=LEFT, padx=10, pady=5)
      
      frame.grid(row=1, column=0)
      
      self.fen_verif.mainloop()
      
      try: self.fen_verif.destroy()
      except: return 0 #si on ferme la fenetre c'est comme si on annule
      return self.choix
   
   def verif_save2(self, c):
      if c == 0: #oui
         self.menu_map_save()
         self.choix = 1
      elif c == 1: #non
         self.choix = 1
      elif c == 2: #annuler
         self.choix = 0
      self.fen_verif.quit()
   
   
   
   
   #NEW WALL :
   
   def menu_edit_new(self):
      self.fen = Toplevel()
      self.fen.title("Pysnake Map Editor")
      self.fen.grab_set()
      self.fen.focus_set()
      
      Label(self.fen, text="x1 :").grid(row=0, column=0)
      x1 = Entry(self.fen, width=2)
      x1.grid(row=0, column=1)
      
      Label(self.fen, text="y1 :").grid(row=1, column=0)
      y1 = Entry(self.fen, width=2)
      y1.grid(row=1, column=1)
      
      Label(self.fen, text="x2 :").grid(row=0, column=2)
      x2 = Entry(self.fen, width=2)
      x2.grid(row=0, column=3)
      
      Label(self.fen, text="y2 :").grid(row=1, column=2)
      y2 = Entry(self.fen, width=2)
      y2.grid(row=1, column=3)
      
      entries = [x1, y1, x2, y2]
      
      create = Button(self.fen, text="Create", command=lambda e=entries: self.ajout_murs(e))
      create.grid(row=2, column=0, pady=5)
      
      cancel = Button(self.fen, text="Cancel", command=self.fen.quit)
      cancel.grid(row=2, column=2, pady=5)
      
      self.fen.mainloop()
      
      try: self.fen.destroy()
      except: 0
   
   def ajout_murs(self, entries):
      e_x1, e_y1, e_x2, e_y2 = entries
      try: x1, y1, x2, y2 = int(e_x1.get()), int(e_y1.get()), int(e_x2.get()), int(e_y2.get())
      except ValueError: return
      if x2 < x1 or y2 < y1: return
      if x1 < 0 or x2 >= CASES_X or y1 < 0 or y2 >= CASES_Y: return
      murs.ajout([x1, y1, x2, y2])
      self.fen.quit()
      self.affiche()
   
   
   
   
   #REMOVE WALL :
   
   def menu_edit_remove(self):
      self.fen2 = Toplevel()
      self.fen2.title("Pysnake Map Editor")
      self.fen2.grab_set()
      self.fen2.focus_set()
      
      frame = Frame(self.fen2)
      scrollbar = Scrollbar(frame)
      self.listbox = Listbox(frame)
      scrollbar.config(command = self.listbox.yview)
      self.listbox.config(yscrollcommand = scrollbar.set)
      self.listbox.pack(side = LEFT, fill = Y)
      scrollbar.pack(side = RIGHT, fill = Y)
      frame.grid(row=2, column=1)
      self.listbox.bind('<ButtonRelease-1>', self.clic)
      self.actualise_remove_murs()
      
      delete = Button(self.fen2, text="Remove", command=self.suppr_murs)
      delete.grid(row=2, column=0, pady=5)
      
      cancel = Button(self.fen2, text="Cancel", command=self.fen2.quit)
      cancel.grid(row=2, column=2, pady=5)
      
      self.fen2.mainloop()
      
      try: self.fen2.destroy()
      except: 0
   
   def actualise_remove_murs(self):
      self.clicked = -1
      self.listbox.delete(0, END)
      for i in range(len(murs.list)):
         self.listbox.insert(i, murs.str(i))
   
   def suppr_murs(self):
      id = self.clicked
      if id == -1: return
      print "Wall removed : "+str(murs.list[id])
      murs.suppr(id)
      self.actualise_remove_murs()
      self.affiche()
   
   
   
   
   #MODIFY WALL :
   
   def menu_edit_modify(self):
      self.fen3 = Toplevel()
      self.fen3.title("Pysnake Map Editor")
      self.fen3.grab_set()
      self.fen3.focus_set()
      
      frame = Frame(self.fen3)
      scrollbar = Scrollbar(frame)
      self.listbox = Listbox(frame)
      scrollbar.config(command = self.listbox.yview)
      self.listbox.config(yscrollcommand = scrollbar.set)
      self.listbox.pack(side = LEFT, fill = Y)
      scrollbar.pack(side = RIGHT, fill = Y)
      frame.grid(row=0, column=1)
      self.listbox.bind('<ButtonRelease-1>', self.clic)
      self.actualise_modif_murs()
      
      modify = Button(self.fen3, text="Modify", command=self.modif_murs)
      modify.grid(row=1, column=0, pady=5)
      
      cancel = Button(self.fen3, text="Cancel", command=self.fen3.quit)
      cancel.grid(row=1, column=2, pady=5)
      
      self.fen3.mainloop()
      
      try: self.fen3.destroy()
      except: 0
   
   def actualise_modif_murs(self):
      self.clicked = -1
      self.listbox.delete(0, END)
      for i in range(len(murs.list)):
         self.listbox.insert(i, murs.str(i))
   
   def modif_murs(self):
      id = self.clicked
      if id == -1: return
      print id
      self.modif2(id)
   
   
   def modif2(self, id):
      self.fen4 = Toplevel()
      self.fen4.title("Pysnake Map Editor")
      self.fen4.grab_set()
      self.fen4.focus_set()
      
      mur = murs.list[id]
      
      Label(self.fen4, text="x1 :").grid(row=0, column=0)
      x1 = Entry(self.fen4, width=2)
      x1.insert(0, mur[0])
      x1.grid(row=0, column=1)
      
      Label(self.fen4, text="y1 :").grid(row=1, column=0)
      y1 = Entry(self.fen4, width=2)
      y1.insert(0, mur[1])
      y1.grid(row=1, column=1)
      
      Label(self.fen4, text="x2 :").grid(row=0, column=2)
      x2 = Entry(self.fen4, width=2)
      x2.insert(0, mur[2])
      x2.grid(row=0, column=3)
      
      Label(self.fen4, text="y2 :").grid(row=1, column=2)
      y2 = Entry(self.fen4, width=2)
      y2.insert(0, mur[3])
      y2.grid(row=1, column=3)
      
      id_and_entries = [id, x1, y1, x2, y2]
      
      modify = Button(self.fen4, text="Modify", command=lambda e=id_and_entries: self.modif_murs2(e))
      modify.grid(row=2, column=0, padx=2, pady=5)
      
      cancel = Button(self.fen4, text="Cancel", command=self.fen4.quit)
      cancel.grid(row=2, column=2, padx=2, pady=5)
      
      self.fen4.mainloop()
      
      try: self.fen4.destroy()
      except: return
      self.actualise_modif_murs()
   
   def modif_murs2(self, id_and_entries):
      id, e_x1, e_y1, e_x2, e_y2 = id_and_entries
      try: x1, y1, x2, y2 = int(e_x1.get()), int(e_y1.get()), int(e_x2.get()), int(e_y2.get())
      except ValueError: return
      if x2 < x1 or y2 < y1: return
      if x1 < 0 or x2 >= CASES_X or y1 < 0 or y2 >= CASES_Y: return
      murs.modif(id, [x1, y1, x2, y2])
      self.fen4.quit()
      self.affiche()
   
   
   
   
   #DEFINE START POS :
   
   def menu_edit_define(self):
      self.fen5 = Toplevel()
      self.fen5.title("Pysnake Map Editor")
      self.fen5.grab_set()
      self.fen5.focus_set()
      
      frame = Frame(self.fen5)
      scrollbar = Scrollbar(frame)
      self.listbox = Listbox(frame)
      scrollbar.config(command = self.listbox.yview)
      self.listbox.config(yscrollcommand = scrollbar.set)
      self.listbox.pack(side = LEFT, fill = Y)
      scrollbar.pack(side = RIGHT, fill = Y)
      frame.grid(row=0, column=1)
      self.listbox.bind('<ButtonRelease-1>', self.clic)
      self.actualise_start_pos()
      
      define = Button(self.fen5, text="Define", command=self.define_start_pos)
      define.grid(row=1, column=0, padx=2, pady=5)
      
      cancel = Button(self.fen5, text="Cancel", command=self.fen5.quit)
      cancel.grid(row=1, column=2, padx=2, pady=5)
      
      self.fen5.mainloop()
      
      try: self.fen5.destroy()
      except: 0
   
   def actualise_start_pos(self):
      self.clicked = -1
      self.listbox.delete(0, END)
      for i in range(len(start_pos.list)):
         self.listbox.insert(i+1, "Joueur "+str(i+1))
   
   def define_start_pos(self):
      j = self.clicked
      if j == -1: return
      print j
      self.start_pos2(j)
   
   
   def start_pos2(self, j):
      self.fen6 = Toplevel()
      self.fen6.title("Pysnake Map Editor")
      self.fen6.grab_set()
      self.fen6.focus_set()
      
      frame = Frame(self.fen6)
      scrollbar = Scrollbar(frame)
      self.listbox2 = Listbox(frame)
      scrollbar.config(command = self.listbox2.yview)
      self.listbox2.config(yscrollcommand = scrollbar.set)
      self.listbox2.pack(side = LEFT, fill = Y)
      scrollbar.pack(side = RIGHT, fill = Y)
      frame.grid(row=0, column=1)
      self.listbox2.bind('<ButtonRelease-1>', self.clic2)
      self.actualise_start_pos2(j)
      
      create = Button(self.fen6, text="Create", command=lambda id=j: self.create_start_pos(id))
      create.grid(row=1, column=0, padx=2, pady=5)
      
      define = Button(self.fen6, text="Modify", command=lambda id=j: self.define_start_pos2(id))
      define.grid(row=1, column=1, padx=2, pady=5)
      
      delete = Button(self.fen6, text="Delete", command=lambda id=j: self.suppr_start_pos(id))
      delete.grid(row=2, column=0, padx=2, pady=5)
      
      cancel = Button(self.fen6, text="Cancel", command=self.fen6.quit)
      cancel.grid(row=1, column=2, padx=2, pady=5)
      
      self.fen6.mainloop()
      
      try: self.fen6.destroy()
      except: 0
   
   def actualise_start_pos2(self, j):
      self.clicked2 = -1
      self.listbox2.delete(0, END)
      for i in range(len(start_pos.list[j])):
         self.listbox2.insert(i, start_pos.str(j, i))
   
   
   def suppr_start_pos(self, j):
      i = self.clicked2
      if i == -1: return
      if i == 0 or i == 1 or i == 2: return
      print i
      start_pos.suppr(j, i)
      self.actualise_start_pos2(j)
   
   
   def create_start_pos(self, j):
      self.fen7 = Toplevel()
      self.fen7.title("Pysnake Map Editor")
      self.fen7.grab_set()
      self.fen7.focus_set()
      
      Label(self.fen7, text="x :").grid(row=0, column=0)
      x = Entry(self.fen7, width=2)
      x.grid(row=0, column=1)
      
      Label(self.fen7, text="y :").grid(row=1, column=0)
      y = Entry(self.fen7, width=2)
      y.grid(row=1, column=1)
      
      id_and_entries = [j, x, y]
      
      create = Button(self.fen7, text="Create", command=lambda e=id_and_entries: self.create_start_pos2(e))
      create.grid(row=2, column=0, pady=5)
      
      cancel = Button(self.fen7, text="Cancel", command=self.fen7.quit)
      cancel.grid(row=2, column=2, pady=5)
      
      self.fen7.mainloop()
      
      try: self.fen7.destroy()
      except: return
      self.actualise_start_pos2(j)
   
   def create_start_pos2(self, entries):
      j, e_x, e_y = entries
      try: x, y = int(e_x.get()), int(e_y.get())
      except ValueError: return
      if x < 0 or x >= CASES_X or y < 0 or y >= CASES_Y: return
      start_pos.ajout(j, [x, y])
      self.fen7.quit()
   
   
   def define_start_pos2(self, j):
      i = self.clicked2
      if i == -1: return
      print i
      self.modif_start_pos(j, i)
   
   def modif_start_pos(self, j, i):
      self.fen8 = Toplevel()
      self.fen8.title("Pysnake Map Editor")
      self.fen8.grab_set()
      self.fen8.focus_set()
      
      sp = start_pos.list[j][i]
      
      if i == 0: #couleur
         frame = Frame(self.fen8)
         scrollbar = Scrollbar(frame)
         self.listbox3 = Listbox(frame)
         scrollbar.config(command = self.listbox3.yview)
         self.listbox3.config(yscrollcommand = scrollbar.set)
         self.listbox3.pack(side = LEFT, fill = Y)
         scrollbar.pack(side = RIGHT, fill = Y)
         frame.grid(row=0, column=0)
         self.listbox3.bind('<ButtonRelease-1>', self.clic3)
         self.actualise_modif_start_pos()
         
         id_and_entries = [j, i]
         r = 1
      
      elif i == 1: #direction
         Label(self.fen8, text="Direction :").grid(row=0, column=0)
         var = StringVar(value=sp)
         Radiobutton(self.fen8, text="Up  ", variable=var, value="h").grid(row=1, column=0)
         Radiobutton(self.fen8, text="Right", variable=var, value="d").grid(row=1, column=1)
         Radiobutton(self.fen8, text="Left", variable=var, value="g").grid(row=2, column=0)
         Radiobutton(self.fen8, text="Down", variable=var, value="b").grid(row=2, column=1)
         id_and_entries = [j, i, var]
         r = 3
      
      else: #tête ou queue
         Label(self.fen8, text="x :").grid(row=0, column=0)
         x = Entry(self.fen8, width=2)
         x.insert(0, sp[0])
         x.grid(row=0, column=1)
         
         Label(self.fen8, text="y :").grid(row=1, column=0)
         y = Entry(self.fen8, width=2)
         y.insert(0, sp[1])
         y.grid(row=1, column=1)
         
         id_and_entries = [j, i, x, y]
         r = 2
         
      modify = Button(self.fen8, text="Modify", command=lambda e=id_and_entries: self.modif_start_pos2(e))
      modify.grid(row=r, column=0, padx=5, pady=5)
      
      cancel = Button(self.fen8, text="Cancel", command=self.fen8.quit)
      cancel.grid(row=r, column=1, padx=5, pady=5)
      
      self.fen8.mainloop()
      
      try: self.fen8.destroy()
      except: return
      self.actualise_start_pos2(j)
   
   def actualise_modif_start_pos(self):
      self.clicked3 = -1
      self.listbox3.delete(0, END)
      for i in range(len(COULEURS)):
         self.listbox3.insert(i, COULEURS[i])
   
   def modif_start_pos2(self, id_and_entries):
      if id_and_entries[1] == 0: #couleur
         j, i = id_and_entries
         c = self.clicked3
         if c == -1: return
         print c
         start_pos.modif(j, i, COULEURS[c])
      elif id_and_entries[1] == 1: #direction
         j, i, var = id_and_entries
         d = var.get()
         print d
         start_pos.modif(j, i, d)
      else: #tête ou queue
         j, i, e_x, e_y = id_and_entries
         try: x, y = int(e_x.get()), int(e_y.get())
         except ValueError: return
         if x < 0 or x >= CASES_X or y < 0 or y >= CASES_Y: return
         start_pos.modif(j, i, [x, y])
      self.fen8.quit()
   
   
   
   
   def clic(self, event):
      i = self.listbox.curselection()
      if len(i) == 0: return
      self.clicked = int(i[0])
      print self.clicked
   
   
   def clic2(self, event):
      i = self.listbox2.curselection()
      self.clicked2 = int(i[0])
      print self.clicked2
   
   
   def clic3(self, event):
      i = self.listbox3.curselection()
      self.clicked3 = int(i[0])
      print self.clicked3
   
   
   def affiche(self):
      self.canevas.delete(ALL)
      
      for m in murs.list:
         for x in range(m[0], m[2]+1):
            for y in range(m[1], m[3]+1):
               x1 = x * TAILLE_CASE
               y1 = y * TAILLE_CASE
               x2 = x1 + TAILLE_CASE
               y2 = y1 + TAILLE_CASE
               self.canevas.create_rectangle((x1, y1, x2, y2), fill=C_MUR, width=0)
      
      for j in start_pos.list:
         for queue in j[3:]:
            x1 = queue[0] * TAILLE_CASE
            y1 = queue[1] * TAILLE_CASE
            x2 = x1 + TAILLE_CASE
            y2 = y1 + TAILLE_CASE
            self.canevas.create_rectangle((x1, y1, x2, y2), fill=C_QUEUE, width=0)
         c_tete = start_pos.traduire(j[0])
         tete = j[2]
         x1_tete = tete[0] * TAILLE_CASE
         y1_tete = tete[1] * TAILLE_CASE
         x2_tete = x1_tete + TAILLE_CASE
         y2_tete = y1_tete + TAILLE_CASE
         self.canevas.create_rectangle((x1_tete, y1_tete, x2_tete, y2_tete), fill=c_tete, width=0)
      
      self.set_saved(0)






class Murs():

   def __init__(self):
      self.list = []

   def initialize(self):
      self.list = []

   def ajout(self, coords):
      print coords
      self.list.append(coords)
      appli.affiche()

   def suppr(self, id):
      del self.list[id]
      appli.affiche()

   def modif(self, id, coords):
      self.list[id] = coords
      appli.affiche()
   
   def str(self, i):
      x1, y1, x2, y2 = self.list[i]
      return str(x1) + ", " + str(y1) + ", " + str(x2) + ", " + str(y2)
   
   def load(self, filename):
      map = ConfigParser.RawConfigParser()
      try: map.read(MAPS_DIR+filename)
      except ConfigParser.MissingSectionHeaderError:
         appli.message("Can't find walls.")
         return 0
      i = 1
      while 1:
         try: m = eval(map.get("Murs", "murs"+str(i)))
         except ConfigParser.NoOptionError: break
         except NameError:
            appli.message("Can't read walls.")
            return 0
         if type(m) != list:
            appli.message("Can't read walls.")
            return 0
         if len(m) != 4:
            appli.message("Can't read walls.")
            return 0
         if type(m[0]) != int or type(m[1]) != int or type(m[2]) != int or type(m[3]) != int:
            appli.message("Can't read walls.")
            return 0
         self.list.append(m)
         i += 1






class Start_Pos():

   def __init__(self):
      self.list = []

   def initialize(self, clients):
      self.list = []
      for i in range(clients):
         self.list.append(["bleu", "g", [0, 0]])
   
   def ajout(self, j, coords):
      self.list[j].append(coords)
      appli.affiche()

   def modif(self, j, i, coords):
      if i == 0: #couleur
         coords = self.translate(coords)
      self.list[j][i] = coords
      appli.affiche()

   def suppr(self, j, i):
      del self.list[j][i]
      appli.affiche()
   
   def str(self, j, i):
      if i == 0:
         c = self.list[j][0]
         return "Color : " + self.traduire(c)
      elif i == 1:
         d = self.list[j][1]
         return "Direction : " + self.traduire(d)
      elif i == 2:
         x, y = self.list[j][2]
         return "Head : " + str(x) + ", " + str(y)
      else:
         x, y = self.list[j][i]
         return "Tail : " + str(x) + ", " + str(y)
   
   def translate(self, color):
      if color == "blue": return "bleu"
      if color == "red": return "rouge"
      if color == "green": return "vert"
      if color == "yellow": return "jaune"
      if color == "orange": return "orange"
      if color == "pink": return "rose"
      if color == "purple": return "violet"
   
   def traduire(self, fr):
      if fr == "bleu": return "blue"
      if fr == "rouge": return "red"
      if fr == "vert": return "green"
      if fr == "jaune": return "yellow"
      if fr == "orange": return "orange"
      if fr == "rose": return "pink"
      if fr == "violet": return "purple"
      if fr == "g": return "left"
      if fr == "h": return "up"
      if fr == "d": return "right"
      if fr == "b": return "down"
   
   def load(self, filename):
      map = ConfigParser.RawConfigParser()
      try: map.read(MAPS_DIR+filename)
      except ConfigParser.MissingSectionHeaderError:
         appli.message("Can't find start position.")
         return 0
      i = 1
      while 1:
         try: j = eval(map.get("StartPos", "joueur"+str(i)))
         except ConfigParser.NoOptionError: break
         if self.check(j) == 0: return 0
         self.list.append(j)
         i += 1
      return 1 #chargement OK
      
   def check(self, j):
      if type(j) != list:
         appli.message("Can't read start position.")
         return 0
      if len(j) < 3: #si y a pas couleur, pas direction ou pas tête
         appli.message("Can't read start position.")
         return 0
      for i in range(len(j)):
         l = j[i]
         if i == 0: #couleur
            if self.traduire(l) == 0: #si la couleur n'est pas une couleur
               appli.message("Can't read start position.")
               return 0
         elif i == 1: #direction
            if l != "g" and l != "h" and l != "d" and l != "b":
               appli.message("Can't read start position.")
         else: #tête ou queue
            if type(l) != list:
               appli.message("Can't read start position.")
               return 0
            if len(l) != 2:
               appli.message("Can't read start position.")
               return 0
            if type(l[0]) != int or type(l[1]) != int:
               appli.message("Can't read start position.")
               return 0
      return 1 #chargement OK
   
   def number(self, number):
      if len(self.list) > number:
         del self.list[:number]
      elif len(self.list) < number:
         for i in range(number-len(self.list)):
            self.list.append(["blue", "g", [0, 0]])





if __name__ == "__main__":
   global appli
   appli = Application()
   appli.main()