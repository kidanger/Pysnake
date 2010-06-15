#!/usr/bin/env python
# -*- coding:Utf-8 -*-


#TODO:
#- Map name with crc
#- Change maps data system


#DOC : http://gnuprog.info/prog/python/pwidget.php


import sys, os, ConfigParser
from Tkinter import *


CASES_X = 32
CASES_Y = 24
TAILLE_CASE = 20
MAPS_DIR = os.getcwd() + "/maps/"
COLORS = ["blue", "red", "green", "yellow", "orange", "pink", "purple"]

ELEMENT_WALL = 1
ELEMENT_HEAD = 2
ELEMENT_TAIL = 3

DIRECTIONS = {"g": "left", "h": "up", "d": "right", "b": "down"}





def Clamp(Int, Min, Max):
	if Int < Min:
		return Min
	elif Int > Max:
		return Max
	return Int



class CSelectionListbox():
	
	def __init__(self, L):
		self.m_Listbox = L
		self.m_Selected = -1
		L.bind('<ButtonRelease-1>', self.Select)
	
	def Reset(self):
		self.m_Listbox.delete(0, END)
		self.m_Selected = -1
	
	def Select(self, event):
		Index = self.m_Listbox.curselection()
		if len(Index) == 0: return
		self.m_Selected = int(Index[0])





class CWalls():
	
	def __init__(self):
		self.Reset()
	
	def Reset(self):
		self.m_List = []
	
	def Initialize(self):
		self.m_List = []
	
	def Add(self, Coords):
		self.m_List.append(Coords)
		Display()
	
	def Remove(self, WallId):
		del self.m_List[WallId]
		Display()
	
	def Modify(self, WallId, Coords):
		self.m_List[WallId] = Coords
		Display()
	
	def Str(self, WallId):
		X1, Y1, X2, Y2 = self.m_List[WallId]
		return str(X1) + ", " + str(Y1) + ", " + str(X2) + ", " + str(Y2)
	
	def Load(self, Filename):
		Map = ConfigParser.RawConfigParser()
		try: Map.read(MAPS_DIR+Filename)
		except ConfigParser.MissingSectionHeaderError:
			DisplayMessage("Can't find walls.")
			return 0
		Id = 1
		while 1:
			try: Wall = eval(Map.get("Walls", "wall"+str(Id)))
			except ConfigParser.NoSectionError:
				DisplayMessage("Can't read walls.")
				return 0
			except ConfigParser.NoOptionError:
				break
			except NameError:
				DisplayMessage("Can't read walls.")
				return 0
			if type(Wall) != list:
				DisplayMessage("Can't read walls.")
				return 0
			if len(Wall) != 4:
				DisplayMessage("Can't read walls.")
				return 0
			if type(Wall[0]) != int or type(Wall[1]) != int or type(Wall[2]) != int or type(Wall[3]) != int:
				DisplayMessage("Can't read walls.")
				return 0
			if Wall[2] < Wall[0] or Wall[3] < Wall[1]:
				DisplayMessage("Can't read walls.")
				return 0
			if Wall[0] < 0 or Wall[2] >= CASES_X or Wall[1] < 0 or Wall[3] >= CASES_Y:
				DisplayMessage("Can't read walls.")
				return 0
			self.m_List.append(Wall)
			Id += 1
		return 1





class CStartPos():

	def __init__(self):
		self.Reset()
	
	def Reset(self):
		self.m_Players = []
	
	def Initialize(self):
		self.m_Players = []
		for Id in range(4):
			self.m_Players.append(["blue", "g", [0, 0]])
	
	def Add(self, PlayerId, Coords):
		self.m_Players[PlayerId].append(Coords)
		Display()
	
	def Modify(self, PlayerId, ElementId, Coords):
		self.m_Players[PlayerId][ElementId] = Coords
		Display()
	
	def Remove(self, PlayerId, TailId):
		del self.m_Players[PlayerId][TailId]
		Display()
	
	def Str(self, PlayerId, ElementId):
		if ElementId == 0:
			return "Color : " + self.m_Players[PlayerId][0]
		elif ElementId == 1:
			return "Direction : " + DIRECTIONS[self.m_Players[PlayerId][1]]
		elif ElementId == 2:
			X, Y = self.m_Players[PlayerId][2]
			return "Head : " + str(X) + ", " + str(Y)
		else:
			X, Y = self.m_Players[PlayerId][ElementId]
			return "Tail : " + str(X) + ", " + str(Y)
	
	def Load(self, Filename):
		Map = ConfigParser.RawConfigParser()
		try: Map.read(MAPS_DIR+Filename)
		except ConfigParser.MissingSectionHeaderError:
			DisplayMessage("Can't find start positions.")
			return 0
		Id = 1
		while 1:
			try: Player = eval(Map.get("StartPos", "player"+str(Id)))
			except ConfigParser.NoSectionError:
				DisplayMessage("Can't read start positions.")
				return 0
			except ConfigParser.NoOptionError:
				break
			if type(Player) != list:
				DisplayMessage("Can't read start positions.")
				return 0
			if len(Player) < 3: #color, direction, head
				DisplayMessage("Can't read start positions.")
				return 0
			for ElementId in range(len(Player)):
				Element = Player[ElementId]
				if ElementId == 0: #color
					if not Element in COLORS:
						DisplayMessage("Can't read start positions.")
						return 0
				elif ElementId == 1: #direction
					if Element != "g" and Element != "h" and Element != "d" and Element != "b":
						DisplayMessage("Can't read start positions.")
						return 0
				else: #head or tail
					if type(Element) != list:
						DisplayMessage("Can't read start positions.")
						return 0
					if len(Element) != 2:
						DisplayMessage("Can't read start positions.")
						return 0
					if type(Element[0]) != int or type(Element[1]) != int:
						DisplayMessage("Can't read start positions.")
						return 0
			self.m_Players.append(Player)
			Id += 1
		return 1
	
	def SetPlayersNumber(self, Number):
		if len(self.m_Players) > Number:
			del self.m_Players[Number:]
		elif len(self.m_Players) < Number:
			for Id in range(Number-len(self.m_Players)):
				self.m_Players.append(["blue", "g", [0, 0]])
		Display()





class CGlobals():
	
	def __init__(self):
		self.Walls = CWalls()
		self.StartPos = CStartPos()
		self.MapName = ""
		self.Holding = None
		self.Maping = 0
		self.Saved = 0
		self.SaveChoice = 0
		self.ReplaceChoice = 0



g = CGlobals()





def Main():
	
	Window_Game = Tk()
	Window_Game.title("Pysnake Map Editor")
	Window_Game.grab_set()
	Window_Game.focus_set()
	
	#create menu :
	Menus = Menu(Window_Game)
	
	#create Options menu :
	global MenuOptions
	MenuOptions = Menu(Menus, tearoff=0)
	MenuOptions.add_command(label="Choose Name", command=MenuOptions_ChooseName, underline=6)
	MenuOptions.add_command(label="Set Players Number", command=MenuOptions_SetPlayersNumber, underline=6)
	MenuOptions.add_command(label="Add Map to Server Config", command=MenuOptions_ConfigAdd, underline=0)
	MenuOptions.add_command(label="Quit", command=MenuOptions_Quit, accelerator="Ctrl+Q", underline=0)
	Window_Game.bind("<Control-q>", MenuOptions_Quit)
	Window_Game.bind("<Control-Q>", MenuOptions_Quit)
	
	#create Map menu :
	global MenuMap
	MenuMap = Menu(Menus, tearoff=0)
	MenuMap.add_command(label="New", command=MenuMap_New, accelerator="Ctrl+N", underline=0)
	Window_Game.bind("<Control-n>", MenuMap_New)
	Window_Game.bind("<Control-N>", MenuMap_New)
	MenuMap.add_command(label="Load", command=MenuMap_Load, accelerator="Ctrl+O", underline=0)
	Window_Game.bind("<Control-o>", MenuMap_Load)
	Window_Game.bind("<Control-O>", MenuMap_Load)
	MenuMap.add_command(label="Save", command=MenuMap_Save, accelerator="Ctrl+S", underline=0)
	Window_Game.bind("<Control-s>", MenuMap_Save)
	Window_Game.bind("<Control-S>", MenuMap_Save)
	MenuMap.add_command(label="Close", command=MenuMap_Close, accelerator="Ctrl+W", underline=0)
	Window_Game.bind("<Control-w>", MenuMap_Close)
	Window_Game.bind("<Control-W>", MenuMap_Close)
	
	#create Edit menu :
	global MenuEdit
	MenuEdit = Menu(Menus, tearoff=0)
	MenuEdit.add_command(label="New Wall", command=MenuEdit_NewWall, underline=0)
	MenuEdit.add_command(label="Remove Wall", command=MenuEdit_RemoveWall, underline=0)
	MenuEdit.add_command(label="Modify Wall", command=MenuEdit_ModifyWall, underline=0)
	MenuEdit.add_command(label="Define Start Position", command=MenuEdit_DefineStartPos, underline=0)
	
	Menus.add_cascade(label="Options", menu=MenuOptions, underline=0)
	Menus.add_cascade(label="Map", menu=MenuMap, underline=0)
	Menus.add_cascade(label="Edit", menu=MenuEdit, underline=0)
	Window_Game.config(menu=Menus)
	
	global Canevas
	Canevas = Canvas(Window_Game, bg="white", width=CASES_X*TAILLE_CASE, height=CASES_Y*TAILLE_CASE)
	Canevas.grid(row=0, padx=0)
	
	Canevas.bind('<Button-1>', StartHolding)
	Canevas.bind('<ButtonRelease-1>', StopHolding)
	Canevas.bind('<Double-Button-1>', DoubleClick)
	Canevas.bind('<ButtonRelease-3>', RightClick)
	
	QuickBar = Frame(Window_Game)
	
	global ButtonNewWall
	ButtonNewWall = Button(QuickBar, text="New Wall", command=MenuEdit_NewWall)
	ButtonNewWall.pack(side=LEFT, padx=10, pady=5)
	
	global ButtonRemoveWall
	ButtonRemoveWall = Button(QuickBar, text="Remove Wall", command=MenuEdit_RemoveWall)
	ButtonRemoveWall.pack(side=LEFT, padx=10, pady=5)
	
	global ButtonModifyWall
	ButtonModifyWall = Button(QuickBar, text="Modify Wall", command=MenuEdit_ModifyWall)
	ButtonModifyWall.pack(side=LEFT, padx=10, pady=5)
	
	global ButtonDefineStartPos
	ButtonDefineStartPos = Button(QuickBar, text="Define Start Position", command=MenuEdit_DefineStartPos)
	ButtonDefineStartPos.pack(side=LEFT, padx=10, pady=5)
	
	QuickBar.grid(row=1)
	
	LoadImg()
	Display()
	
	SetMaping(0)
	SetSaved(1)
	
	Window_Game.mainloop()
	
	try: Window_Game.destroy()
	except: 0

def LoadImg():
	global ImageWall
	ImageWall = PhotoImage(file = "img/walls/wall.gif", master = Canevas)
	global ImageWallBig
	ImageWallBig = PhotoImage(file = "img/walls/wall_big.gif", master = Canevas)
	
	global SnakeImages
	SnakeImages = {}
	Parts = ["tail", "b", "h", "g", "d"]
	for Color in COLORS:
		SnakeImages[Color] = {}
		for Part in Parts:
			SnakeImages[Color][Part] = PhotoImage(file = "img/snakes/"+Color+"/"+Part+".gif", master = Canevas)





def Display():
	Canevas.delete(ALL)
	
	for Wall in g.Walls.m_List:
		if Wall[2] - Wall[0] == 1 and Wall[3] - Wall[1] == 1:
			Canevas.create_image(Wall[0]* TAILLE_CASE, Wall[1]* TAILLE_CASE, anchor = NW, image=ImageWallBig)
		else:
			for X in range(Wall[0], Wall[2]+1):
				for Y in range(Wall[1], Wall[3]+1):
					Canevas.create_image(X*TAILLE_CASE, Y*TAILLE_CASE, anchor = NW, image=ImageWall)
	
	for Player in g.StartPos.m_Players:
		Color = Player[0]
		Direction = Player[1]
		Head = Player[2]
		Canevas.create_image(Head[0]*TAILLE_CASE, Head[1]*TAILLE_CASE, anchor = NW, image=SnakeImages[Color][Direction])
		for Tail in Player[3:]:
			Canevas.create_image(Tail[0]*TAILLE_CASE, Tail[1]*TAILLE_CASE, anchor = NW, image=SnakeImages[Color]["tail"])
	
	SetSaved(0)





def SetMaping(M): #enable some menus when we open/create a map
	g.Maping = M
	if g.Maping == 0: State = "disabled"
	else: State = "normal"
	MenuOptions.entryconfigure("Choose Name", state=State)
	MenuOptions.entryconfigure("Set Players Number", state=State)
	MenuOptions.entryconfigure("Add Map to Server Config", state=State)
	MenuMap.entryconfigure("Save", state=State)
	MenuMap.entryconfigure("Close", state=State)
	MenuEdit.entryconfigure("New Wall", state=State)
	MenuEdit.entryconfigure("Remove Wall", state=State)
	MenuEdit.entryconfigure("Modify Wall", state=State)
	MenuEdit.entryconfigure("Define Start Position", state=State)
	ButtonNewWall.configure(state=State)
	ButtonRemoveWall.configure(state=State)
	ButtonModifyWall.configure(state=State)
	ButtonDefineStartPos.configure(state=State)

def SetSaved(S): #enable Save menu when we the map isn't saved yet
	g.Saved = S
	if g.Saved == 0: State = "normal"
	else: State = "disabled"
	MenuMap.entryconfigure("Save", state=State)
  


def GetElement(MouseX, MouseY):
	CaseX = MouseX/TAILLE_CASE
	CaseY = MouseY/TAILLE_CASE
	
	for PlayerId in range(len(g.StartPos.m_Players)):
		Player = g.StartPos.m_Players[PlayerId]
		if CaseX == Player[2][0] and CaseY == Player[2][1]:
			return [ELEMENT_HEAD, PlayerId]
		for TailId in range(len(Player[3:])):
			Tail = Player[TailId]
			if CaseX == Tail[0] and CaseY == Tail[1]:
				return [ELEMENT_TAIL, PlayerId, TailId]
	
	for WallId in range(len(g.Walls.m_List)):
		Wall = g.Walls.m_List[WallId]
		RangeX = range(Wall[0], Wall[2]+1)
		RangeY = range(Wall[1], Wall[3]+1)
		if (CaseX in RangeX) and (CaseY in RangeY):
			return [ELEMENT_WALL, WallId, CaseX, CaseY]
	
	return None

def DoubleClick(event):
	0

def RightClick(event):
	Element = GetElement(event.x, event.y)
	if Element == None:
		return
	elif Element[0] == ELEMENT_WALL:
		g.Walls.Remove(Element[1])
	elif Element[0] == ELEMENT_HEAD:
		0 #self.start_pos2(Element[1])
	elif Element[0] == ELEMENT_TAIL:
		g.StartPos.Remove(Element[1], Element[2])

def StartHolding(event):
	g.Holding = GetElement(event.x, event.y)

def StopHolding(event):
	CaseX = Clamp(event.x/TAILLE_CASE, 0, CASES_X-1)
	CaseY = Clamp(event.y/TAILLE_CASE, 0, CASES_Y-1)
	Coords = [CaseX, CaseY]
	if g.Holding == None:
		return
	elif g.Holding[0] == ELEMENT_WALL:
		Wall = g.Walls.m_List[g.Holding[1]]
		DifX = CaseX-g.Holding[2]
		DifY = CaseY-g.Holding[3]
		Wall[0] += DifX
		Wall[0] = Clamp(Wall[0], 0, CASES_X-1)
		Wall[1] += DifY
		Wall[1] = Clamp(Wall[1], 0, CASES_Y-1)
		Wall[2] += DifX
		Wall[2] = Clamp(Wall[2], 0, CASES_X-1)
		Wall[3] += DifY
		Wall[3] = Clamp(Wall[3], 0, CASES_Y-1)
		g.Walls.Modify(g.Holding[1], Wall)
	elif g.Holding[0] == ELEMENT_HEAD:
		g.StartPos.Modify(g.Holding[1], 2, Coords)
	elif g.Holding[0] == ELEMENT_TAIL:
		g.StartPos.Modify(g.Holding[1], g.Holding[2], Coords)
	g.Holding = None





#DISPLAY MESSAGE :

def DisplayMessage(Message):
	Window_Message = Toplevel()
	Window_Message.title("Pysnake Map Editor")
	Window_Message.grab_set()
	Window_Message.focus_set()
	
	Label(Window_Message, text=Message).pack(side=TOP, pady=3)
	Button(Window_Message, text="OK", command=Window_Message.quit).pack(side=BOTTOM, pady=3)
	
	Window_Message.mainloop()
	
	try: Window_Message.destroy()
	except: 0



#CHECK SAVE :

def CheckSave(): #when we wish close the map, we check that we want to save it or not
	if g.Maping == 0: return 1
	if g.Saved == 1: return 1
	
	global Window_CheckSave
	Window_CheckSave = Toplevel()
	Window_CheckSave.title("Pysnake Map Editor")
	Window_CheckSave.grab_set()
	Window_CheckSave.focus_set()
	
	Label(Window_CheckSave, text="Save changes ?").grid(row=0, column=0)
	g.SaveChoice = 0
	
	Frame_CheckSave = Frame(Window_CheckSave)
	
	ButtonYes = Button(Frame_CheckSave, text="Yes", command=lambda C="Yes": SetSaveChoice(C))
	ButtonYes.pack(side=LEFT, padx=10, pady=5)
	
	ButtonNo = Button(Frame_CheckSave, text="No", command=lambda C="No": SetSaveChoice(C))
	ButtonNo.pack(side=LEFT, padx=10, pady=5)
	
	ButtonCancel = Button(Frame_CheckSave, text="Cancel", command=lambda C="Cancel": SetSaveChoice(C))
	ButtonCancel.pack(side=LEFT, padx=10, pady=5)
	
	Frame_CheckSave.grid(row=1, column=0)
	
	Window_CheckSave.mainloop()
	
	try: Window_CheckSave.destroy()
	except: g.SaveChoice = 0 #close the window = "Cancel"
	return g.SaveChoice

def SetSaveChoice(C):
	if C == "Yes":
		MenuMap_Save()
		g.SaveChoice = 1
	elif C == "No":
		g.SaveChoice = 1
	elif C == "Cancel":
		g.SaveChoice = 0
	Window_CheckSave.quit()



#CHECK REPLACE :

def CheckReplace(Name): #when we wish change the name of the map, check if there isn't already a map with this name
	Window_CheckReplace = Toplevel()
	Window_CheckReplace.title("Pysnake Map Editor")
	Window_CheckReplace.grab_set()
	Window_CheckReplace.focus_set()
	
	Label(Window_CheckReplace, text=Name+" already exists. Do you want to replace it ?").grid(row=0, column=0)
	g.ReplaceChoice = 0
	
	Frame_CheckReplace = Frame(Window_CheckReplace)
	
	ButtonYes = Button(Frame_CheckReplace, text="Yes", command=lambda C="Yes": SetReplaceChoice(C))
	ButtonYes.pack(side=LEFT, padx=10, pady=5)
	
	ButtonNo = Button(Frame_CheckReplace, text="Cancel", command=lambda C="Cancel": SetReplaceChoice(C))
	ButtonNo.pack(side=LEFT, padx=10, pady=5)
	
	ButtonFrame.grid(row=1, column=0)
	
	Window_CheckReplace.mainloop()
	
	try: Window_CheckReplace.destroy()
	except: g.ReplaceChoice = 0 #close the window = "Cancel"
	return g.ReplaceChoice

def SetReplaceChoice(C):
	if C == "Yes":
		g.ReplaceChoice = 1
	elif C == "Cancel":
		g.ReplaceChoice = 0
	Window_CheckReplace.quit()





#CHOOSE NAME :

def MenuOptions_ChooseName():
	global Window_ChooseName
	Window_ChooseName = Toplevel()
	Window_ChooseName.title("Pysnake Map Editor")
	Window_ChooseName.grab_set()
	Window_ChooseName.focus_set()
	
	EntryName = Entry(Window_ChooseName, width=12)
	EntryName.insert(0, g.MapName)
	EntryName.grid(row=0, column=1)
	
	ButtonOk = Button(Window_ChooseName, text="OK", command=lambda N=EntryName: ChangeName(N))
	ButtonOk.grid(row=1, column=0, pady=5)
	
	Cancel = Button(Window_ChooseName, text="Cancel", command=Window_ChooseName.quit)
	Cancel.grid(row=1, column=2, pady=5)
	
	Window_ChooseName.mainloop()
	
	try: Window_ChooseName.destroy()
	except: 0

def ChangeName(EntryName):
	Name = EntryName.get()
	if Name == "": return
	Maps = os.listdir(MAPS_DIR)
	if Name in Maps:
		if CheckReplaceMap(Name) == 0:
			return #if we don't want to replace
	g.MapName = Name
	SetSaved(0)
	Window_ChooseName.quit()



#SET PLAYERS NUMBER :

def MenuOptions_SetPlayersNumber():
	global Window_SetPlayersNumber
	Window_SetPlayersNumber = Toplevel()
	Window_SetPlayersNumber.title("Pysnake Map Editor")
	Window_SetPlayersNumber.grab_set()
	Window_SetPlayersNumber.focus_set()
	
	EntryNumber = Entry(Window_SetPlayersNumber, width=1)
	EntryNumber.insert(0, len(g.StartPos.m_Players))
	EntryNumber.grid(row=0, column=0, pady=3, padx=3)
	
	ButtonOk = Button(Window_SetPlayersNumber, text="OK", command=lambda N=EntryNumber: ChangePlayersNumber(N))
	ButtonOk.grid(row=1, column=0, pady=3, padx=3)
	
	ButtonCancel = Button(Window_SetPlayersNumber, text="Cancel", command=Window_SetPlayersNumber.quit)
	ButtonCancel.grid(row=1, column=1, pady=3, padx=3)
	
	Window_SetPlayersNumber.mainloop()
	
	try: Window_SetPlayersNumber.destroy()
	except: 0

def ChangePlayersNumber(EntryNumber):
	Number = EntryNumber.get()
	if Number == "": return
	try: g.StartPos.SetPlayersNumber(int(Number))
	except ValueError: return
	Window_SetPlayersNumber.quit()



#ADD MAP TO CONFIG :

def MenuOptions_ConfigAdd():
	Config = ConfigParser.RawConfigParser()
	try: Config.read("autoexec.cfg")
	except:
		DisplayMessage("Can't find server config.")
		return
	
	if g.MapName == "":
		MenuMap_Save()
		if g.MapName == "": #Cancel
			DisplayMessage("The map has not been added to server config.")
			return
	
	Maps = eval(Config.get("Game", "maps"))
	if g.MapName in Maps:
		DisplayMessage("Map already in server config.")
		return
	
	Maps.append(g.MapName)
	Config.set("Game", "maps", Maps)
	File = open("autoexec.cfg", "w")
	Config.write(File)
	File.close()
	DisplayMessage("The map has been added to server config.")



#QUIT :

def MenuOptions_Quit(event=0):
	if CheckSave():
		sys.exit()





#NEW MAP :

def MenuMap_New(event=0):
	if MenuMap_Close():
		g.Walls.Initialize()
		g.StartPos.Initialize()
		Display()
		SetMaping(1)
		SetSaved(0)



#LOAD MAP :

def MenuMap_Load(event=0):
	global Window_LoadMap
	Window_LoadMap = Toplevel()
	Window_LoadMap.title("Pysnake Map Editor")
	Window_LoadMap.grab_set()
	Window_LoadMap.focus_set()
	
	Frame_LoadMap = Frame(Window_LoadMap)
	Scrollbar_LoadMap = Scrollbar(Frame_LoadMap)
	Listbox_LoadMap = Listbox(Frame_LoadMap)
	Scrollbar_LoadMap.config(command = Listbox_LoadMap.yview)
	Listbox_LoadMap.config(yscrollcommand = Scrollbar_LoadMap.set)
	Listbox_LoadMap.pack(side = LEFT, fill = Y)
	Scrollbar_LoadMap.pack(side = RIGHT, fill = Y)
	Frame_LoadMap.grid(row=0, column=1)
	
	SelList = CSelectionListbox(Listbox_LoadMap)
	UpdateLoadMap(SelList)
	
	ButtonLoad = Button(Window_LoadMap, text="Load", command=lambda SL=SelList: LoadMap(SL))
	ButtonLoad.grid(row=1, column=0, pady=5)
	
	ButtonRefresh = Button(Window_LoadMap, text="Refresh", command=lambda SL=SelList: UpdateLoadMap(SL))
	ButtonRefresh.grid(row=1, column=1, pady=5)
	
	ButtonCancel = Button(Window_LoadMap, text="Cancel", command=Window_LoadMap.quit)
	ButtonCancel.grid(row=1, column=2, pady=5)
	
	Window_LoadMap.mainloop()
	
	try: Window_LoadMap.destroy()
	except: 0

def UpdateLoadMap(SelList):
	SelList.Reset()
	Maps = os.listdir(MAPS_DIR)
	for Index in range(len(Maps)):
		SelList.m_Listbox.insert(Index, Maps[Index])

def LoadMap(SelList):
	if SelList.m_Selected < 0: return
	if MenuMap_Close():
		Filename = SelList.m_Listbox.get(SelList.m_Selected)
		if g.Walls.Load(Filename) == 0: return
		if g.StartPos.Load(Filename) == 0: return
		print "Loaded map : "+Filename
		g.MapName = Filename
		Display()
		SetMaping(1)
		SetSaved(1)
		Window_LoadMap.quit()



#SAVE MAP :

def MenuMap_Save(event=0):
	if g.MapName == "":
		MenuOptions_ChooseName()
		if g.MapName == "": #Cancel
			return
	File = file(MAPS_DIR + g.MapName + ".map", "w")
	Content = "[Walls]"
	for WallId in range(len(g.Walls.m_List)):
		Content += "\nwall" + str(WallId+1) + " = [" + g.Walls.str(WallId) + "]"
	Content += "\n\n[StartPos]"
	for PlayerId in range(len(g.StartPos.m_Players)):
		Content += "\nplayer" + str(PlayerId+1) + " = ["
		for PartId in range(len(g.StartPos.m_Players[PlayerId])):
			Part = g.StartPos.m_Players[PlayerId][PartId]
			if PartId == 0: #color
				Content += "\""+Part+"\""
			elif PartId == 1: #direction
				Content += ", \""+Part+"\""
			else: #head or tail
				Content += ", [" + str(Part[0]) + ", " + str(Part[1]) + "]"
		Content += "]"
	File.write(Content)
	File.close()
	SetSaved(1)



#CLOSE MAP :

def MenuMap_Close(event=0):
	if CheckSave():
		g.Walls.Reset()
		g.StartPos.Reset()
		Display()
		SetMaping(0)
		SetSaved(1)
		g.MapName = ""
		return 1
	return 0





#NEW WALL :

def MenuEdit_NewWall():
	global Window_NewWall
	Window_NewWall = Toplevel()
	Window_NewWall.title("Pysnake Map Editor")
	Window_NewWall.grab_set()
	Window_NewWall.focus_set()
	
	Label(Window_NewWall, text="x1 :").grid(row=0, column=0)
	EntryX1 = Entry(Window_NewWall, width=2)
	EntryX1.grid(row=0, column=1)
	
	Label(Window_NewWall, text="y1 :").grid(row=1, column=0)
	EntryY1 = Entry(Window_NewWall, width=2)
	EntryY1.grid(row=1, column=1)
	
	Label(Window_NewWall, text="x2 :").grid(row=0, column=2)
	EntryX2 = Entry(Window_NewWall, width=2)
	EntryX2.grid(row=0, column=3)
	
	Label(Window_NewWall, text="y2 :").grid(row=1, column=2)
	EntryY2 = Entry(Window_NewWall, width=2)
	EntryY2.grid(row=1, column=3)
	
	Entries = [EntryX1, EntryY1, EntryX2, EntryY2]
	
	ButtonCreate = Button(Window_NewWall, text="Create", command=lambda E=Entries: AddWall(E))
	ButtonCreate.grid(row=2, column=0, pady=5)
	
	ButtonCancel = Button(Window_NewWall, text="Cancel", command=Window_NewWall.quit)
	ButtonCancel.grid(row=2, column=2, pady=5)
	
	Window_NewWall.mainloop()
	
	try: Window_NewWall.destroy()
	except: 0

def AddWall(Entries):
	EntryX1, EntryY1, EntryX2, EntryY2 = Entries
	try: X1, Y1, X2, Y2 = int(EntryX1.get()), int(EntryY1.get()), int(EntryX2.get()), int(EntryY2.get())
	except ValueError: return
	if X2 < X1 or Y2 < Y1: return
	X1 = Clamp(X1, 0, CASES_X-1)
	Y1 = Clamp(Y1, 0, CASES_Y-1)
	X2 = Clamp(X2, 0, CASES_X-1)
	Y2 = Clamp(Y2, 0, CASES_Y-1)
	g.Walls.Add([X1, Y1, X2, Y2])
	Window_NewWall.quit()



#REMOVE WALL :

def MenuEdit_RemoveWall():
	Window_RemoveWall = Toplevel()
	Window_RemoveWall.title("Pysnake Map Editor")
	Window_RemoveWall.grab_set()
	Window_RemoveWall.focus_set()
	
	Frame_RemoveWall = Frame(Window_RemoveWall)
	Scrollbar_RemoveWall = Scrollbar(Frame_RemoveWall)
	Listbox_RemoveWall = Listbox(Frame_RemoveWall)
	Scrollbar_RemoveWall.config(command = Listbox_RemoveWall.yview)
	Listbox_RemoveWall.config(yscrollcommand = Scrollbar_RemoveWall.set)
	Listbox_RemoveWall.pack(side = LEFT, fill = Y)
	Scrollbar_RemoveWall.pack(side = RIGHT, fill = Y)
	Frame_RemoveWall.grid(row=2, column=1)
	
	SelList = CSelectionListbox(Listbox_RemoveWall)
	UpdateRemoveWall(SelList)
	
	ButtonRemove = Button(Window_RemoveWall, text="Remove", command=lambda SL=SelList: RemoveWall(SL))
	ButtonRemove.grid(row=2, column=0, pady=5)
	
	ButtonCancel = Button(Window_RemoveWall, text="Cancel", command=Window_RemoveWall.quit)
	ButtonCancel.grid(row=2, column=2, pady=5)
	
	Window_RemoveWall.mainloop()
	
	try: Window_RemoveWall.destroy()
	except: 0

def UpdateRemoveWall(SelList):
	SelList.Reset()
	for WallId in range(len(g.Walls.m_List)):
		SelList.m_Listbox.insert(WallId, g.Walls.Str(WallId))

def RemoveWall(SelList):
	if SelList.m_Selected < 0: return
	g.Walls.Remove(SelList.m_Selected)
	UpdateRemoveWall(SelList)





#MODIFY WALL :
   
def MenuEdit_ModifyWall():
	Window_ModifyWall = Toplevel()
	Window_ModifyWall.title("Pysnake Map Editor")
	Window_ModifyWall.grab_set()
	Window_ModifyWall.focus_set()
	
	Frame_ModifyWall = Frame(Window_ModifyWall)
	Scrollbar_ModifyWall = Scrollbar(Frame_ModifyWall)
	Listbox_ModifyWall = Listbox(Frame_ModifyWall)
	Scrollbar_ModifyWall.config(command = Listbox_ModifyWall.yview)
	Listbox_ModifyWall.config(yscrollcommand = Scrollbar_ModifyWall.set)
	Listbox_ModifyWall.pack(side = LEFT, fill = Y)
	Scrollbar_ModifyWall.pack(side = RIGHT, fill = Y)
	Frame_ModifyWall.grid(row=0, column=1)
	
	SelList = CSelectionListbox(Listbox_ModifyWall)
	UpdateModifyWall(SelList)
	
	ButtonModify = Button(Window_ModifyWall, text="Modify", command=lambda SL=SelList: ModifyWallSelected(SL))
	ButtonModify.grid(row=1, column=0, pady=5)
	
	ButtonCancel = Button(Window_ModifyWall, text="Cancel", command=Window_ModifyWall.quit)
	ButtonCancel.grid(row=1, column=2, pady=5)
	
	Window_ModifyWall.mainloop()
	
	try: Window_ModifyWall.destroy()
	except: 0

def UpdateModifyWall(SelList):
	SelList.Reset()
	for WallId in range(len(g.Walls.m_List)):
		SelList.m_Listbox.insert(WallId, g.Walls.Str(WallId))

def ModifyWallSelected(SelList):
	if SelList.m_Selected < 0: return
	
	global Window_ModifyWallSelected
	Window_ModifyWallSelected = Toplevel()
	Window_ModifyWallSelected.title("Pysnake Map Editor")
	Window_ModifyWallSelected.grab_set()
	Window_ModifyWallSelected.focus_set()
	
	WallId = SelList.m_Selected
	Wall = g.Walls.m_List[WallId]
	
	Label(Window_ModifyWallSelected, text="x1 :").grid(row=0, column=0)
	EntryX1 = Entry(Window_ModifyWallSelected, width=2)
	EntryX1.insert(0, Wall[0])
	EntryX1.grid(row=0, column=1)
	
	Label(Window_ModifyWallSelected, text="y1 :").grid(row=1, column=0)
	EntryY1 = Entry(Window_ModifyWallSelected, width=2)
	EntryY1.insert(0, Wall[1])
	EntryY1.grid(row=1, column=1)
	
	Label(Window_ModifyWallSelected, text="x2 :").grid(row=0, column=2)
	EntryX2 = Entry(Window_ModifyWallSelected, width=2)
	EntryX2.insert(0, Wall[2])
	EntryX2.grid(row=0, column=3)
	
	Label(Window_ModifyWallSelected, text="y2 :").grid(row=1, column=2)
	EntryY2 = Entry(Window_ModifyWallSelected, width=2)
	EntryY2.insert(0, Wall[3])
	EntryY2.grid(row=1, column=3)
	
	Entries = [EntryX1, EntryY1, EntryX2, EntryY2]
	
	ButtonModify = Button(Window_ModifyWallSelected, text="Modify", command=lambda W=WallId, E=Entries, SL=SelList: ModifyWall(W, E, SL))
	ButtonModify.grid(row=2, column=0, padx=2, pady=5)
	
	ButtonCancel = Button(Window_ModifyWallSelected, text="Cancel", command=Window_ModifyWallSelected.quit)
	ButtonCancel.grid(row=2, column=2, padx=2, pady=5)
	
	Window_ModifyWallSelected.mainloop()
	
	try: Window_ModifyWallSelected.destroy()
	except: 0

def ModifyWall(WallId, Entries, SelList):
	if SelList.m_Selected < 0: return
	EntryX1, EntryY1, EntryX2, EntryY2 = Entries
	try: X1, Y1, X2, Y2 = int(EntryX1.get()), int(EntryY1.get()), int(EntryX2.get()), int(EntryY2.get())
	except ValueError: return
	if X2 < X1 or Y2 < Y1: return
	X1 = Clamp(X1, 0, CASES_X-1)
	Y1 = Clamp(Y1, 0, CASES_Y-1)
	X2 = Clamp(X2, 0, CASES_X-1)
	Y2 = Clamp(Y2, 0, CASES_Y-1)
	g.Walls.Modify(WallId, [X1, Y1, X2, Y2])
	Display()
	UpdateModifyWall(SelList)
	Window_ModifyWallSelected.quit()





#DEFINE START POS :

def MenuEdit_DefineStartPos():
	Window_DefineStartPos = Toplevel()
	Window_DefineStartPos.title("Pysnake Map Editor")
	Window_DefineStartPos.grab_set()
	Window_DefineStartPos.focus_set()
	
	Frame_DefineStartPos = Frame(Window_DefineStartPos)
	Scrollbar_DefineStartPos = Scrollbar(Frame_DefineStartPos)
	Listbox_DefineStartPos = Listbox(Frame_DefineStartPos)
	Scrollbar_DefineStartPos.config(command = Listbox_DefineStartPos.yview)
	Listbox_DefineStartPos.config(yscrollcommand = Scrollbar_DefineStartPos.set)
	Listbox_DefineStartPos.pack(side = LEFT, fill = Y)
	Scrollbar_DefineStartPos.pack(side = RIGHT, fill = Y)
	Frame_DefineStartPos.grid(row=0, column=1)
	
	SelList = CSelectionListbox(Listbox_DefineStartPos)
	UpdateDefineStartPos(SelList)
	
	ButtonDefine = Button(Window_DefineStartPos, text="Define", command=lambda SL=SelList: DefinePlayer(SL))
	ButtonDefine.grid(row=1, column=0, padx=2, pady=5)
	
	ButtonCancel = Button(Window_DefineStartPos, text="Cancel", command=Window_DefineStartPos.quit)
	ButtonCancel.grid(row=1, column=2, padx=2, pady=5)
	
	Window_DefineStartPos.mainloop()
	
	try: Window_DefineStartPos.destroy()
	except: 0

def UpdateDefineStartPos(SelList):
	SelList.Reset()
	for PlayerId in range(len(g.StartPos.m_Players)):
		SelList.m_Listbox.insert(PlayerId+1, "Player "+str(PlayerId+1))


def DefinePlayer(SelList_DefineStartPos):
	PlayerId = SelList_DefineStartPos.m_Selected
	if PlayerId < 0: return
	
	Window_DefinePlayer = Toplevel()
	Window_DefinePlayer.title("Pysnake Map Editor")
	Window_DefinePlayer.grab_set()
	Window_DefinePlayer.focus_set()
	
	Frame_DefinePlayer = Frame(Window_DefinePlayer)
	Scrollbar_DefinePlayer = Scrollbar(Frame_DefinePlayer)
	Listbox_DefinePlayer = Listbox(Frame_DefinePlayer)
	Scrollbar_DefinePlayer.config(command = Listbox_DefinePlayer.yview)
	Listbox_DefinePlayer.config(yscrollcommand = Scrollbar_DefinePlayer.set)
	Listbox_DefinePlayer.pack(side = LEFT, fill = Y)
	Scrollbar_DefinePlayer.pack(side = RIGHT, fill = Y)
	Frame_DefinePlayer.grid(row=0, column=1)
	
	SelList = CSelectionListbox(Listbox_DefinePlayer)
	UpdateDefinePlayer(PlayerId, SelList)
	
	ButtonNew = Button(Window_DefinePlayer, text="New tail", command=lambda P=PlayerId, SL=SelList: NewTail(P, SL))
	ButtonNew.grid(row=1, column=0, padx=2, pady=5)
	
	ButtonRemove = Button(Window_DefinePlayer, text="Remove tail", command=lambda P=PlayerId, SL=SelList: RemoveTail(P, SL))
	ButtonRemove.grid(row=1, column=1, padx=2, pady=5)
	
	ButtonModify = Button(Window_DefinePlayer, text="Modify", command=lambda P=PlayerId, SL=SelList: ModifyPart(P, SL))
	ButtonModify.grid(row=1, column=2, padx=2, pady=5)
	
	ButtonCancel = Button(Window_DefinePlayer, text="Cancel", command=Window_DefinePlayer.quit)
	ButtonCancel.grid(row=2, column=1, padx=2, pady=5)
	
	Window_DefinePlayer.mainloop()
	
	try: Window_DefinePlayer.destroy()
	except: 0

def UpdateDefinePlayer(PlayerId, SelList):
	SelList.Reset()
	for PartId in range(len(g.StartPos.m_Players[PlayerId])):
		SelList.m_Listbox.insert(PartId, g.StartPos.Str(PlayerId, PartId))


def NewTail(PlayerId, SelList):
	global Window_NewTail
	Window_NewTail = Toplevel()
	Window_NewTail.title("Pysnake Map Editor")
	Window_NewTail.grab_set()
	Window_NewTail.focus_set()
	
	Label(Window_NewTail, text="x :").grid(row=0, column=0)
	EntryX = Entry(Window_NewTail, width=2)
	EntryX.grid(row=0, column=1)
	
	Label(Window_NewTail, text="y :").grid(row=1, column=0)
	EntryY = Entry(Window_NewTail, width=2)
	EntryY.grid(row=1, column=1)
	
	Entries = [EntryX, EntryY]
	
	ButtonCreate = Button(Window_NewTail, text="Create", command=lambda P=PlayerId, E=Entries, SL=SelList: CreateNewTail(P, E, SL))
	ButtonCreate.grid(row=2, column=0, pady=5)
	
	ButtonCancel = Button(Window_NewTail, text="Cancel", command=Window_NewTail.quit)
	ButtonCancel.grid(row=2, column=2, pady=5)
	
	Window_NewTail.mainloop()
	
	try: Window_NewTail.destroy()
	except: 0

def CreateNewTail(PlayerId, Entries, SelList):
	EntryX, EntryY = Entries
	try: X, Y = int(EntryX.get()), int(EntryY.get())
	except ValueError: return
	X = Clamp(X, 0, CASES_X-1)
	Y = Clamp(Y, 0, CASES_Y-1)
	g.StartPos.Add(PlayerId, [X, Y])
	UpdateDefinePlayer(PlayerId, SelList)
	Window_NewTail.quit()


def RemoveTail(PlayerId, SelList):
	if SelList.m_Selected < 0: return
	if SelList.m_Selected < 3: return #can't delete color/direction/head
	g.StartPos.Remove(PlayerId, SelList.m_Selected)
	UpdateDefinePlayer(PlayerId, SelList)


def ModifyPart(PlayerId, SelList_DefinePlayer):
	if SelList_DefinePlayer.m_Selected < 0: return
	
	global Window_ModifyPart
	Window_ModifyPart = Toplevel()
	Window_ModifyPart.title("Pysnake Map Editor")
	Window_ModifyPart.grab_set()
	Window_ModifyPart.focus_set()
	
	PartId = SelList_DefinePlayer.m_Selected
	Part = g.StartPos.m_Players[PlayerId][PartId]
	
	if PartId == 0: #color
		Frame_ModifyPart = Frame(Window_ModifyPart)
		Scrollbar_ModifyPart = Scrollbar(Frame_ModifyPart)
		Listbox_ModifyPart = Listbox(Frame_ModifyPart)
		Scrollbar_ModifyPart.config(command = Listbox_ModifyPart.yview)
		Listbox_ModifyPart.config(yscrollcommand = Scrollbar_ModifyPart.set)
		Listbox_ModifyPart.pack(side = LEFT, fill = Y)
		Scrollbar_ModifyPart.pack(side = RIGHT, fill = Y)
		Frame_ModifyPart.grid(row=0, column=0)
		
		SelList = CSelectionListbox(Listbox_ModifyPart)
		UpdateModifyColor(SelList)
		
		Entries = [SelList]
		NextRow = 1
	
	elif PartId == 1: #direction
		Label(Window_ModifyPart, text="Direction :").grid(row=0, column=0)
		VarDirection = StringVar(value=Part)
		Radiobutton(Window_ModifyPart, text="Up  ", variable=VarDirection, value="h").grid(row=1, column=0)
		Radiobutton(Window_ModifyPart, text="Right", variable=VarDirection, value="d").grid(row=1, column=1)
		Radiobutton(Window_ModifyPart, text="Left", variable=VarDirection, value="g").grid(row=2, column=0)
		Radiobutton(Window_ModifyPart, text="Down", variable=VarDirection, value="b").grid(row=2, column=1)
		Entries = [VarDirection]
		NextRow = 3
      
	else: #head or tail
		Label(Window_ModifyPart, text="x :").grid(row=0, column=0)
		EntryX = Entry(Window_ModifyPart, width=2)
		EntryX.insert(0, Part[0])
		EntryX.grid(row=0, column=1)
		
		Label(Window_ModifyPart, text="y :").grid(row=1, column=0)
		EntryY = Entry(Window_ModifyPart, width=2)
		EntryY.insert(0, Part[1])
		EntryY.grid(row=1, column=1)
		
		Entries = [EntryX, EntryY]
		NextRow = 2
	
	ButtonModify = Button(Window_ModifyPart, text="Modify", command=lambda P=PlayerId, A=PartId, E=Entries, SL=SelList_DefinePlayer: ModifyModifyPart(P, A, E, SL))
	ButtonModify.grid(row=NextRow, column=0, padx=5, pady=5)
      
	ButtonCancel = Button(Window_ModifyPart, text="Cancel", command=Window_ModifyPart.quit)
	ButtonCancel.grid(row=NextRow, column=1, padx=5, pady=5)
	
	Window_ModifyPart.mainloop()
	
	try: Window_ModifyPart.destroy()
	except: 0

def UpdateModifyColor(SelList):
	for ColorId in range(len(COLORS)):
		SelList.m_Listbox.insert(ColorId, COLORS[ColorId])

def ModifyModifyPart(PlayerId, PartId, Entries, SelList_DefinePlayer):
	if PartId == 0: #color
		if Entries[0].m_Selected < 0: return
		g.StartPos.Modify(PlayerId, PartId, COLORS[Entries[0].m_Selected])
	elif PartId == 1: #direction
		VarDirection = Entries[0]
		g.StartPos.Modify(PlayerId, PartId, VarDirection.get())
	else: #head or tail
		EntryX, EntryY = Entries
		try: X, Y = int(EntryX.get()), int(EntryY.get())
		except ValueError: return
		X = Clamp(X, 0, CASES_X-1)
		Y = Clamp(Y, 0, CASES_Y-1)
		g.StartPos.Modify(PlayerId, PartId, [X, Y])
	UpdateDefinePlayer(PlayerId, SelList_DefinePlayer)
	Window_ModifyPart.quit()
   




if __name__ == "__main__":
   Main()
