#!/usr/bin/env python
#coding=utf-8

import random

class Terrain:
  def __init__(self, initial, final, random = None, quarter_turns = True, filename = None, facing = 0):
    self.quarter_turns = quarter_turns
    self.values = {}
    self.start = Node(self, initial, facing = facing)
    self.goal = Node(self, final)

    if random is not None:
      self.randomize(random[0], random[1], random[2])
    else:
      f = open(filename)
      l = f.readline().split()
      self.size_x = int(l[0])
      self.size_y = int(l[1])
      for i in range(0, self.size_x):
        l = f.readline().split()
        for j in range(0, self.size_y):
          self.values[(i,j)] = int(l[j])
      f.close()

  def randomize(self, size_x, size_y, diffs):
    self.size_x = size_x;
    self.size_y = size_y;

    for i in range(0, self.size_x):
      for j in range(0, self.size_y):
        self.values[(i,j)] = 1
    
    diffs = min(diffs, size_x*size_y)
    i = 0
    while i < diffs:
      randx = random.randint(0, size_x-1)
      randy = random.randint(0, size_y-1)
      if self.values[(randx, randy)] != 1: i = i-1 # otro intento
      self.values[(randx,randy)] = random.randint(2,5)
      i = i+1

  def __repr__(self):
    s = ""
    for i in range(0, self.size_x):
      for j in range(0, self.size_y):
        s = s + str(self.values[(i,j)]) + " "
      s += "\n"
    s += "Start = " + str(self.start) + "\n"
    s += "Goal = " + str(self.goal)
    return s

class Node:
  def __init__(self, terrain, position, value = 0, facing = 0, prev = None):
    self.terrain = terrain
    self.position = position
    self.value = value
    self.facing = facing
    self.prev = prev

  def get_neighbours(self):
    turn_cost = 1
    turn_size = 1 if self.terrain.quarter_turns else 2
    l = [Node(self.terrain, self.position, self.value+turn_cost, (self.facing-turn_size) % 8, self)]
    l += [Node(self.terrain, self.position, self.value+turn_cost, (self.facing+turn_size) % 8, self)]

    new_pos = None
    if(self.facing == 0) and self.position[0] > 0: #top
      new_pos = (self.position[0]-1, self.position[1])
    elif (self.facing == 2) and self.position[1]+1 < self.terrain.size_y: #right
      new_pos = (self.position[0], self.position[1]+1)
    elif (self.facing == 4) and self.position[0]+1 < self.terrain.size_x: #bot
      new_pos = (self.position[0]+1, self.position[1])
    elif (self.facing == 6) and self.position[1] > 0: #left
      new_pos = (self.position[0], self.position[1]-1)
    elif (self.facing == 1) and self.position[0] > 0 and self.position[1]+1 < self.terrain.size_y: #topright
      new_pos = (self.position[0]-1, self.position[1]+1)
    elif (self.facing == 3) and self.position[0]+1 < self.terrain.size_x and self.position[1]+1 < self.terrain.size_y: #botright
      new_pos = (self.position[0]+1, self.position[1]+1)
    elif (self.facing == 5) and self.position[0]+1 < self.terrain.size_x and self.position[1] > 0: #botleft
      new_pos = (self.position[0]+1, self.position[1]-1)
    elif (self.facing == 7) and self.position[0] > 0 and self.position[1] > 0: #topleft
      new_pos = (self.position[0]-1, self.position[1]-1)

    if new_pos:
      l += [Node(self.terrain, new_pos, self.value + self.terrain.values[new_pos], self.facing, self)]
    return l

  def is_goal(self, goal):
    return self.position == goal.position

  def reconstruct_path(self):
    n = self
    l = []
    while n.prev is not None:
      l.append(n)
      n = n.prev
    l.append(n)
    l.reverse()
    return l

  def __eq__(self, other):
    return self.position == other.position and self.facing == other.facing

  def __hash__(self):
    return self.position[0] * self.terrain.size_x + self.position[1] + self.facing * self.terrain.size_x * self.terrain.size_y

  def __ne__(self, other):
    return not self.__eq__(other)

  def __repr__(self):
    return "(" + str(self.position) + "," + str(self.facing) + ")"

class Bfs:
  def __init__(self, terrain):
    self.terrain = terrain

  def search(self):
    visited = []
    q = [self.terrain.start]
    ret = []
    while q:
      ret.append([n for n in q])
      n = q.pop(0)
      if n.is_goal(self.terrain.goal):
        n.reconstruct_path()
        return ret
      q.extend(filter(lambda x: x not in visited and x not in q, n.get_neighbours()))
      visited.append(n)
    return ret

class AStar:
  def __init__(self, terrain, heuristic = "chebyshev"):
    self.terrain = terrain
    self.heuristic = self.chebyshev if heuristic == "chebyshev" else self.distance_substraction

  def chebyshev(self, node):
    return max(abs(self.terrain.goal.position[0]-node.position[0]), abs(self.terrain.goal.position[1]-node.position[1]))

  def distance_substraction(self, node):
    return abs(abs(self.terrain.goal.position[0]-node.position[0]) - abs(self.terrain.goal.position[1]-node.position[1]))

  def format_nodes(self, l, g, h):
    ret = []
    for n in l:
      ret.append((n, g[n], h[n]))
    return ret

  def search(self):
    ret = []
    s = self.terrain.start
    closedset = []
    openset = [s]
    g_score = {}
    h_score = {}
    f_score = {}

    g_score[s] = 0
    h_score[s] = self.heuristic(s)
    f_score[s] = h_score[s]

    while openset:
      best = min([(f_score[x], x) for x in filter(lambda y: y in openset, f_score)])[1]
      if best.is_goal(self.terrain.goal):
        tmp = [self.format_nodes(openset, g_score, h_score)]
        tmp.append(self.format_nodes([best], g_score, h_score));
        tmp.append(self.format_nodes(best.reconstruct_path(), g_score, h_score))
        tmp.append([]) # neighbours
        ret.append(tmp)
        return ret

      openset.remove(best)
      closedset.append(best)
      new_neighbours = []
      for n in best.get_neighbours():
        if n in closedset: continue
        tentative_g_score = g_score[best] + n.value - best.value
        if n not in openset:
          openset.append(n)
          new_neighbours.append(n)
          h_score[n] = self.heuristic(n)
          g_score[n] = tentative_g_score
          f_score[n] = g_score[n] + h_score[n]
        elif tentative_g_score < g_score[n]:
          n.prev = best
          g_score[n] = tentative_g_score
          f_score[n] = g_score[n] + h_score[n]
      
      tmp = [self.format_nodes(openset, g_score, h_score)]
      tmp[0].extend(self.format_nodes([best], g_score, h_score)) # was removed
      tmp.append((self.format_nodes([best], g_score, h_score)))
      tmp.append(self.format_nodes(best.reconstruct_path(), g_score, h_score))
      tmp.append(self.format_nodes(new_neighbours, g_score, h_score))
      ret.append(tmp)
    return ret
