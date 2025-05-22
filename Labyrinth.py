import pygame
import math

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

WIDTH = 22
HEIGHT = 22
MARGIN = 3

WALL = 0
PATH = 1
START = 9

GRID_SIZE = 20

# ---
# Initialize your classes etc. here
class Node:
    parent = None 
    def __init__(self,walkable = True,x = 0,y = 0):
        self.walkable = walkable
        self.x = x
        self.y = y
        self.g_cost = 0
        self.h_cost =0

    @property
    def f_cost(self):
        return self.g_cost + self.h_cost

    def get_f_cost(self) :
        return self.g_cost + self.h_cost

        
    
class Grid:
    # GRID PATTERN FROM TASK DESCRIPTION
    A = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1,], 
         [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1,], 
         [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1,], 
         [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1,], 
         [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1,], 
         [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1,], 
         [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1,], 
         [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1,], 
         [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1,], 
         [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1,], 
         [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1,], 
         [1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,], 
         [1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,], 
         [1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,], 
         [1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,], 
         [1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,], 
         [1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,], 
         [1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,], 
         [1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,], 
         [1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,]]
    path = [] 
    def __init__(self,obsticleGrid = A):
        self.grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.obsticleGrid = obsticleGrid
        for x in range(0,GRID_SIZE) :
            for y in range(0,GRID_SIZE) :
                if self.obsticleGrid[x][y] == PATH :
                    self.grid[x][y] = Node(True,x,y)
                elif self.obsticleGrid[x][y] == WALL :
                    self.grid[x][y] = Node(False,x,y)
                elif self.obsticleGrid[x][y] == START:
                    self.grid[x][y] = Node(True, x, y) 
        pass 
    ## return 3 x 3 neighbours of grid
    def get_neighbours(self, node):
        neighbours = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = node.x + dx, node.y + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    neighbours.append(self.grid[nx][ny])
        return neighbours
    def get_node(self,x,y) :
        return self.grid[x][y]

# ---
## A star
def pathfind(grid, start, target):
    open_set = [start]
    closed_set = []

    while open_set:
        current = min(open_set, key=lambda n: (n.f_cost, n.h_cost))
        open_set.remove(current)
        closed_set.append(current)

        if current is target:
            return retrace_path(start, target)

        for neigh in grid.get_neighbours(current):
            if not neigh.walkable or neigh in closed_set:
                continue

            tentative_g = current.g_cost + get_distance(current, neigh)
            if tentative_g < neigh.g_cost or neigh not in open_set:
                neigh.g_cost = tentative_g
                neigh.h_cost = get_distance(neigh, target)
                neigh.parent = current
                if neigh not in open_set:
                    open_set.append(neigh)

    return []  # no path found

def pathfind_step_by_step(grid, start, target):
    open_set = [start]
    closed_set = []
    current = None

    while open_set:
        current = min(open_set, key=lambda n: (n.f_cost, n.h_cost))
        open_set.remove(current)
        closed_set.append(current)

        if current is target:
            yield retrace_path(start, target), current
            return

        for neigh in grid.get_neighbours(current):
            if not neigh.walkable or neigh in closed_set:
                continue

            tentative_g = current.g_cost + get_distance(current, neigh)
            if tentative_g < neigh.g_cost or neigh not in open_set:
                neigh.g_cost = tentative_g
                neigh.h_cost = get_distance(neigh, target)
                neigh.parent = current
                if neigh not in open_set:
                    open_set.append(neigh)

        yield [], current

def initialize_pathfinding(grid,startNode) :
    openSet = []
    openSet.append(startNode)
    return openSet

def retrace_path(start, end):
    path = []
    cur = end
    while cur is not start:
        path.append(cur)
        cur = cur.parent
    path.reverse()
    return path
## to work with full numbers we multiply the distance time 10
## distence between two cells is 1 we set the weight times 10
## distance on diagonal axis is sqrt(2) * 10 is ~14
def get_distance(a, b):
    dx, dy = abs(a.x - b.x), abs(a.y - b.y)
    if dx > dy:
        return 14 * dy + 10 * (dx - dy)
    return 14 * dx + 10 * (dy - dx)

##
pygame.init()

size = (500, 500)
screen = pygame.display.set_mode(size)

pygame.display.set_caption("My Game")

done = False

clock = pygame.time.Clock()

grid = Grid()
nodeA = grid.get_node(19,0)
nodeB = grid.get_node(0,19)

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    path = pathfind(grid,nodeA,nodeB)

    screen.fill(BLACK)

    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            node = grid.grid[x][y]
            color = WHITE if node.walkable else BLACK

            if path :
                if node in path :
                    color = BLUE

            if node is nodeA:
                color = GREEN
            elif node is nodeB:
                color = RED


            pygame.draw.rect(
                screen,
                color,
                [(MARGIN + WIDTH) * y + MARGIN, (MARGIN + HEIGHT) * x + MARGIN, WIDTH, HEIGHT]
            )
    

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
