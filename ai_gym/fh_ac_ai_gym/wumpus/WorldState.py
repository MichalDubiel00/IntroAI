import random as r
import json
from enum import Enum
import os


class Location:

    def __init__(self,x,y):
        self.x = x
        self.y = y


class Perception:

    def __init__(self):
        self.stench = False
        self.breeze = False
        self.glitter = False
        self.bump = False
        self.scream = False


class Direction(Enum):
    NORTH =0
    EAST =1
    SOUTH = 2
    WEST =3


class Action:
    WALK = 0
    TURNLEFT = 1
    TURNRIGHT = 2
    GRAB = 3
    SHOOT = 4
    CLIMB = 5


def localize(x):
    if type(x) is list:
        x = Location(x[0], x[1])
    return x



class World_State:

    def __init__(self):
        self.world_size = 4
        self.pit_prob = 0.2
        # x , y 
        self.agent_location = Location(0,0)
        self.agent_direction = Direction.EAST
        self.load_json() 

        if not self.json:
            self.wumpus_location = self.init_wumpus_location()
            self.pit_locations = self.init_pit_locations()
            self.gold_location = self.init_gold_location()
        self.agent_alive = True
        self.has_arrow = True
        self.has_gold = False
        self.in_cave = True
        self.wumpus_alive = True
    
    def load_json(self):

        path_to_file = os.path.realpath(__file__)[:-13]
        json_file = open(path_to_file + 'conf.json')
        config = json.load(json_file)
        config = config['Config']
        include = eval(config['Include'])
        self.json = include
        if include:
            vals = list(config['Pit'])
            self.pit_locations = list(map(localize, vals))
            self.wumpus_location = localize(config['Wumpus'])
            self.gold_location =   localize(config['Gold'])

    def reset(self):
        self.agent_location = Location(0,0)
        self.agent_direction = Direction.EAST
        self.agent_alive = True
        self.has_arrow = True
        self.has_gold = False
        self.in_cave = True
        self.wumpus_alive = True




    def init_wumpus_location(self,x=0,y=0):
        while x == y == 0:
            x ,y = r.randint(0,self.world_size-1), r.randint(0,self.world_size-1)
        return Location(x,y)


    def init_pit_locations(self):
        pits = []
        for x in range(0,self.world_size):
            for y in range(0,self.world_size):
                if x != 0 or y != 0:
                    if r.random() < self.pit_prob:
                        pits.append(Location(x,y))
        return pits

    def init_gold_location(self,x=0,y=0):
        while True:
            if next((False for e in self.pit_locations if e.x == x and e.y == y),True):
                if x !=0 and y != 0:
                    return Location(x,y)
            x ,y = r.randint(0,self.world_size - 1), r.randint(0,self.world_size - 1)


