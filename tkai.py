#!/usr/bin/env python
#coding=utf-8

from random import randint
from searchers import *
from Tkinter import *

class App:
  def __init__(self, master):
    options = Frame(master)

    subframe = Frame(options)
    subsubframe = Frame(subframe)
    Label(subsubframe, text="Posición inicial:").pack(side=LEFT)
    self.initial = Entry(subsubframe, width="4")
    self.initial.insert(0, "0,0,0")
    self.initial.pack(side=LEFT)
    subsubframe.pack(side=TOP)

    subsubframe = Frame(subframe)
    Label(subsubframe, text="Posición final:  ").pack(side=LEFT)
    self.final = Entry(subsubframe, width="4")
    self.final.insert(0, "1,1")
    self.final.pack(side=LEFT)
    subsubframe.pack(side=TOP)
    subframe.pack(side=LEFT)

    subsubframe = Frame(subframe)
    self.read_turns = IntVar()
    Checkbutton(subframe, text="¿Giros de 45º?", variable=self.read_turns).pack(side=BOTTOM)
    subsubframe.pack(side=TOP)
    subframe.pack(side=LEFT)
    options.pack(side=TOP)

    subframe = Frame(options)
    self.method = StringVar(options)
    self.add_dropdown(subframe, self.method, "Método de búsqueda:", "Anchura", "A*")
    self.heuristic = StringVar(options)
    self.add_dropdown(subframe, self.heuristic, "Heurística empleada:", "Chebyshev", "Resta distancias")
    subframe.pack(side=LEFT)

    subframe = Frame(options)
    subsubframe = Frame(subframe)
    Label(subsubframe, text="Mapa aleatorio (N,M,D):").pack(side=LEFT)
    self.randomterrain = Entry(subsubframe, width="4")
    self.randomterrain.insert(0, "3,4,5")
    self.randomterrain.pack(side=LEFT)
    subsubframe.pack(side=TOP)

    subsubframe = Frame(subframe)
    self.read_terrain = IntVar()
    Checkbutton(subframe, text="¿Leer mapa de 'terrain.1'?", variable=self.read_terrain).pack(side=BOTTOM)
    subsubframe.pack(side=TOP)
    subframe.pack(side=LEFT)
    options.pack(side=TOP)

    subframe = Frame(master)
    text_scroll = Scrollbar(subframe)
    text_scroll.pack(side=RIGHT, fill=Y)
    self.text = Text(subframe, wrap=WORD, yscrollcommand=text_scroll.set)
    self.text.pack(side=TOP)
    text_scroll.config(command=self.text.yview)
    subframe.pack(side=TOP)

    Button(master, text="Start", command=self.do_work).pack(side=TOP)

  def add_dropdown(self, frame, var, text, *values):
    # First value is default
    subframe = Frame(frame)
    Label(subframe, text=text).pack(side=LEFT)
    var.set(values[0]) # TODO try?
    OptionMenu(subframe, var, *values).pack(side=RIGHT)
    subframe.pack(side=TOP)

  def do_work(self):
    i = [int(x) for x in self.initial.get().split(",")]
    initial = (i[0], i[1]) 
    f = 0
    if len(i) == 3: f = i[2]
    final = tuple([int(x) for x in self.final.get().split(",")])

    quarter_turns = True if self.read_turns.get() else False

    if self.read_terrain.get():
      terrain = Terrain(initial, final, filename = "terrain.1", facing = f, quarter_turns = quarter_turns)
    else:
      terrain = Terrain(initial, final, random = [int(x) for x in self.randomterrain.get().split(",")], facing = f, quarter_turns = quarter_turns)
    
    if self.heuristic.get() == "Chebyshev":
      heur = "chebyshev"
    else:
      heur = "distance_substraction"

    if self.method.get() == "Anchura":
      s = Bfs(terrain)
    else:
      s = AStar(terrain, heur)

    self.text.delete(1.0, END)

    info = s.search()
    for i, step in enumerate(info):
      self.text.insert(END, "PASO "+ str(i+1) + "\n")
      if self.method.get() == "Anchura":
        self.text.insert(END, "Nivel de exploración:\n")
        self.text.insert(END, str(step) + "\n")
      else:
        self.text.insert(END, "Estados candidatos para continuar:\n")
        self.text.insert(END, str(step[0]) + "\n")
        self.text.insert(END, "Mejor nodo de entre los candidatos:\n")
        self.text.insert(END, str(step[1]) + "\n")
        self.text.insert(END, "Camino actual hasta el mejor nodo:\n")
        self.text.insert(END, str(step[2]) + "\n")
        self.text.insert(END, "Nuevos descendientes generados:\n")
        self.text.insert(END, str(step[3]) + "\n")
      self.text.insert(END, "\n")

root = Tk()
app = App(root)
root.mainloop()
