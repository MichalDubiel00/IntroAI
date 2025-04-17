from prettytable import PrettyTable
from utils import *   # This should include helper functions like getNode()

# -------------------------------
# Define the Node and Edge classes
# -------------------------------
class Node:
    def __init__(self, name):
        self.parent = None    # pointer to parent Node in the search tree
        self.name = name
        self.edges = []
        self.value = 0        # used for cost in UCS

class Edge:
    def __init__(self, edge):
        self.start = edge[0]
        self.end = edge[1]
        self.value = edge[2]
def getNode(name, l):
   return next(( i for i in l if i.name == name), -1)
# -------------------------------
# Graph class as provided, slightly reformatted
# -------------------------------
class Graph:
    def __init__(self, node_list, edges):
        self.nodes = []
        for name in node_list:
            self.nodes.append(Node(name))
        for e in edges:
            # Convert the node names to Node objects
            node1 = getNode(e[0], self.nodes)
            node2 = getNode(e[1], self.nodes)
            e = (node1, node2, e[2])
            # Append edge from node1 to node2 ...
            idx = next((i for i,v in enumerate(self.nodes) if v.name == node1.name), -1)
            self.nodes[idx].edges.append(Edge(e))
            # ... and symmetric edge for an undirected graph
            idx2 = next((i for i,v in enumerate(self.nodes) if v.name == node2.name), -1)
            self.nodes[idx2].edges.append(Edge((node2, node1, e[2])))

    def print(self):
        node_list = self.nodes
        t = PrettyTable(['  '] + [i.name for i in node_list])
        for node in node_list:
            edge_values = ['X'] * len(node_list)
            for edge in node.edges:
                pos = next((i for i,e in enumerate(node_list) if e.name == edge.end.name), -1)
                edge_values[pos] = edge.value           
            t.add_row([node.name] + edge_values)
        print(t)

# -------------------------------
# Queue Data Structure with three modes: FIFO, LIFO, and Priority (for UCS)
# -------------------------------
class Queue:
    def __init__(self, mode='FIFO'):
        self.mode = mode      # mode can be 'FIFO', 'LIFO', or 'PRIO'
        self.list = []

    def push(self, item, priority=0):
        if self.mode == 'PRIO':
            # In UCS, priority is the path cost.
            self.list.append((priority, item))
            self.list.sort(key=lambda x: x[0])
        else:
            self.list.append(item)

    def pop(self):
        if self.mode == 'FIFO':
            return self.list.pop(0)
        elif self.mode == 'LIFO':
            return self.list.pop()
        elif self.mode == 'PRIO':
            return self.list.pop(0)[1]

    def isEmpty(self):
        return len(self.list) == 0

# -------------------------------
# Helper function: reconstruct path from goal to start using parent pointers.
# -------------------------------
def reconstruct_path(node):
    path = []
    while node is not None:
        path.append(node.name)
        node = node.parent
    return path[::-1]

# -------------------------------
# Search algorithms
# -------------------------------

def bfs(graph, start_name, goal_name):
    # Reset the parent pointer for every node.
    for node in graph.nodes:
        node.parent = None

    start = getNode(start_name, graph.nodes)
    goal  = getNode(goal_name, graph.nodes)

    q = Queue(mode='FIFO')
    q.push(start)
    visited = {start.name}

    while not q.isEmpty():
        current = q.pop()
        if current.name == goal.name:
            return reconstruct_path(current)
        for edge in current.edges:
            if edge.end.name not in visited:
                visited.add(edge.end.name)
                edge.end.parent = current
                q.push(edge.end)
    return None

def dfs(graph, start_name, goal_name):
    for node in graph.nodes:
        node.parent = None

    start = getNode(start_name, graph.nodes)
    goal  = getNode(goal_name, graph.nodes)

    q = Queue(mode='LIFO')
    q.push(start)
    visited = set([start.name])
    
    while not q.isEmpty():
        current = q.pop()
        if current.name == goal.name:
            return reconstruct_path(current)
        # Note: here the order of neighbor expansion depends on the order in the edges list.
        for edge in current.edges:
            if edge.end.name not in visited:
                visited.add(edge.end.name)
                edge.end.parent = current
                q.push(edge.end)
    return None

def ucs(graph, start_name, goal_name):
    # For UCS we track the cost so far in the node value.
    for node in graph.nodes:
        node.parent = None
        node.value = float('inf')
    start = getNode(start_name, graph.nodes)
    goal  = getNode(goal_name, graph.nodes)
    start.value = 0

    q = Queue(mode='PRIO')
    q.push(start, priority=0)
    visited = {}

    while not q.isEmpty():
        current = q.pop()
        # If we have reached the goal, we found the optimal path.
        if current.name == goal.name:
            return reconstruct_path(current), current.value
        # To avoid re-expanding a node with a higher cost, check if we have a cheaper route.
        for edge in current.edges:
            new_cost = current.value + edge.value
            # If this path to neighbor is better then use it.
            if new_cost < edge.end.value:
                edge.end.value = new_cost
                edge.end.parent = current
                q.push(edge.end, priority=new_cost)
    return None

# -------------------------------
# Define the Romania Graph
# -------------------------------
romania = Graph(
    ['Or', 'Ne', 'Ze', 'Ia', 'Ar', 'Si', 'Fa', 'Va', 'Ri', 'Ti', 'Lu', 'Pi', 'Ur', 'Hi', 'Me', 'Bu', 'Dr', 'Ef', 'Cr', 'Gi'],
    [
      ('Or', 'Ze', 71), ('Or', 'Si', 151), 
      ('Ne', 'Ia', 87), ('Ze', 'Ar', 75),
      ('Ia', 'Va', 92), ('Ar', 'Si', 140),
      ('Ar', 'Ti', 118), ('Si', 'Fa', 99), 
      ('Si', 'Ri', 80), ('Fa', 'Bu', 211),
      ('Va', 'Ur', 142), ('Ri', 'Pi', 97),
      ('Ri', 'Cr', 146), ('Ti', 'Lu', 111),
      ('Lu', 'Me', 70), ('Me', 'Dr', 75),
      ('Dr', 'Cr', 120), ('Cr', 'Pi', 138),
      ('Pi', 'Bu', 101), ('Bu', 'Gi', 90),
      ('Bu', 'Ur', 85), ('Ur', 'Hi', 98), 
      ('Hi', 'Ef', 86)
    ]
)

# -------------------------------
# Run the searches from Bucharest ('Bu') to Timisoara ('Ti')
# -------------------------------

# BFS: (Search for the shortest number of edges)
bfs_path = bfs(romania, 'Bu', 'Ti')
# Calculate the cost along the path (simply by summing edge values)
def calculate_cost(graph, path):
    cost = 0
    for i in range(len(path)-1):
        node = getNode(path[i], graph.nodes)
        for edge in node.edges:
            if edge.end.name == path[i+1]:
                cost += edge.value
                break
    return cost

bfs_cost = calculate_cost(romania, bfs_path)

# DFS: (May yield a deeper path depending on neighbor ordering)
dfs_path = dfs(romania, 'Bu', 'Ti')
dfs_cost = calculate_cost(romania, dfs_path)

# UCS: (Should yield the lowest total cost path)
ucs_result = ucs(romania, 'Bu', 'Ti')
ucs_path, ucs_cost = ucs_result if ucs_result is not None else (None, None)

# -------------------------------
# Print the results
# -------------------------------
print("BFS:")
print("  Path:", bfs_path)
print("  Total cost: {}".format(bfs_cost))
print("\nDFS:")
print("  Path:", dfs_path)
print("  Total cost: {}".format(dfs_cost))
print("\nUCS:")
print("  Path:", ucs_path)
print("  Total cost: {}".format(ucs_cost))
