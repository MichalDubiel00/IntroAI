import gym
import fh_ac_ai_gym
from itertools import combinations
from collections import defaultdict, deque

WALK = 0
TURNLEFT = 1
TURNRIGHT = 2
GRAB = 3
SHOOT = 4
CLIMB = 5

def Pit(x, y):
    return f"P{x}{y}"

def Wumpus(x, y):
    return f"W{x}{y}"

def Breeze(x, y):
    return f"B{x}{y}"

def Stench(x, y):
    return f"S{x}{y}"

def get_adjacent_cells(x, y):
    adj = []
    if x > 0: adj.append((x - 1, y))
    if x < 3: adj.append((x + 1, y))
    if y > 0: adj.append((x, y - 1))
    if y < 3: adj.append((x, y + 1))
    return adj

wumpus_env = gym.make('Wumpus-v0',disable_env_checker = True)

wumpus_env.reset()
wumpus_env.render()

def Tell(kb,clause) :
    if clause not in kb:
        kb.append(clause)


def negate(literal):
    return literal[1:] if literal.startswith('~') else '~' + literal

def negate_clause(clause):
    return [[negate(lit)] for lit in clause]

def unit_resolution(kb, alpha):
    """
    kb: list of clauses (each clause is a list of literals, e.g., ['~B11', 'P12'])
    alpha: a query clause (e.g., ['P12']) to check entailment
    Returns True if KB ⊨ alpha, i.e., if alpha is entailed by KB
    """
    # Convert KB to frozenset representation
    clauses = set()
    for clause in kb:
        clauses.add(frozenset(clause))
    
    # Negate alpha and add to KB
    neg_alpha = [negate(lit) for lit in alpha]
    for lit in neg_alpha:
        clauses.add(frozenset([lit]))
    
    
    # Build literal index {literal: set(clauses containing it)}
    index = defaultdict(set)
    for clause in clauses:
        for lit in clause:
            index[lit].add(clause)
    
    unit_queue = deque()
    for clause in clauses:
        if len(clause) == 1:
            unit_queue.append(clause)
    
    seen = set(clauses)
    
    while unit_queue:
        unit_clause = unit_queue.popleft()
        if unit_clause not in clauses:
            continue
        L = next(iter(unit_clause))
        negL = negate(L)
        
        # Check for immediate contradiction
        if frozenset([negL]) in clauses:
            return True
        
        # Process clauses containing L
        for clause in list(index[L]):
            if clause in clauses:
                clauses.remove(clause)
                for lit in clause:
                    index[lit].discard(clause)
        
        # Process clauses containing ~L
        for clause in list(index.get(negL, [])):
            if clause not in clauses:
                continue
            new_clause = clause - {negL}
            
            # Skip tautologies
            if any(negate(lit) in new_clause for lit in new_clause):
                continue
                
            if new_clause in seen:
                continue
                
            seen.add(new_clause)
            
            # Found contradiction
            if not new_clause:
                return True
                
            clauses.add(new_clause)
            for lit in new_clause:
                index[lit].add(new_clause)
            if len(new_clause) == 1:
                unit_queue.append(new_clause)
    
    return False

def resolve(ci, cj):
    resolvents = set()
    for di in ci:
        for dj in cj:
            if di == negate(dj):
                new_clause = (ci - {di}) | (cj - {dj})
                # Filter tautologies early
                if not any(negate(lit) in new_clause for lit in new_clause):
                    resolvents.add(frozenset(new_clause))
    return resolvents
#O(n^2)
def pl_resolution(kb, alpha):
    clauses = set(frozenset(c) for c in kb)
    neg_alpha = [negate(lit) for lit in alpha]
    
    for lit in neg_alpha:
        clauses.add(frozenset([lit]))
    
    seen = set(clauses)
    
    while True:
        new = set()
        clause_list = list(clauses)
        for (ci, cj) in combinations(clause_list, 2):
            resolvents = resolve(ci, cj)
            for res in resolvents:
                if not res:  # empty clause
                    return True
                if res not in seen:
                    new.add(res)
                    seen.add(res)
        
        if not new:
            return False
        clauses.update(new)


def pl_fc_entails(kb, q):
    count = {}
    inferred = defaultdict(bool)
    agenda = deque()
    # Map each clause to its premises
    premise_map = defaultdict(list)
    
    # Initialize rules and agenda
    for clause in kb:
        premises = clause['premises']
        conclusion = clause['conclusion']
        key = (tuple(premises), conclusion)
        count[key] = len(premises)
        
        for p in premises:
            premise_map[p].append((premises, conclusion))
        
        if not premises:
            agenda.append(conclusion)

    while agenda:
        p = agenda.popleft()
        
        if p == q:
            return True
            
        if not inferred[p]:
            inferred[p] = True
            for (premises, conclusion) in premise_map.get(p, []):
                key = (tuple(premises), conclusion)
                count[key] -= 1
                if count[key] == 0 and not inferred[conclusion]:
                    agenda.append(conclusion)
                        
    return False


def perceive_and_tell(kb, percept, x, y, horn=False):
    # Always assert current cell is safe
    if horn:
        Fact(kb, f"~{Pit(x, y)}")
        Fact(kb, f"~{Wumpus(x, y)}")
    
        # Handle breeze perception
        if percept['breeze']:
            Fact(kb, Breeze(x, y))
        else:
            # No breeze means no pit in adjacent cells
            for (i, j) in get_adjacent_cells(x, y):
                Fact(kb, f"~{Pit(i, j)}")
        
        # Handle stench perception
        if percept['stench']:
            Fact(kb, Stench(x, y))
        else:
            # No stench means no wumpus in adjacent cells
            for (i, j) in get_adjacent_cells(x, y):
                Fact(kb, f"~{Wumpus(i, j)}")
    else:
        Tell(kb, [f"~{Pit(x, y)}"])
        Tell(kb, [f"~{Wumpus(x, y)}"])
        if percept['breeze']:
            Tell(kb, [Breeze(x, y)])
        else:
            Tell(kb, [f"~{Breeze(x, y)}"])
        if percept['stench']:
            Tell(kb, [Stench(x, y)])
        else:
            Tell(kb, [f"~{Stench(x, y)}"])

def is_safe(kb, x, y):
    no_pit = unit_resolution(kb, [f"~{Pit(x, y)}"])
    no_wumpus = unit_resolution(kb, [f"~{Wumpus(x, y)}"])
    return no_pit and no_wumpus

def print_kb(kb):
    print("Knowledge Base:")
    for clause in kb:
        print(" ∨ ".join(clause))


def populate(): #CNF Clauses
    kb = []
    # At least one wumpus
    at_least_one_wumpus = [f"{Wumpus(x,y)}" for x in range(4) for y in range(4) ]

    Tell(kb,at_least_one_wumpus)

    # At most one wumpus

    cells = [(x, y) for x in range(4) for y in range(4)]

    # Replace at-most-one wumpus with pairwise constraints
    for (x1, y1), (x2, y2) in combinations(cells, 2):
            Tell(kb, [f"~{Wumpus(x1,y1)}", f"~{Wumpus(x2,y2)}"])

    # Breeze Rules

    for x in range(4):
        for y in range(4):
            adj = get_adjacent_cells(x, y)

            # ¬Bxy ∨ P_adj1 ∨ P_adj2 ...
            clause = [f"~{Breeze(x, y)}"] + [Pit(i, j) for (i, j) in adj]
            Tell(kb, clause)

            # For each adjacent: ¬Pij ∨ Bxy
            for (i, j) in adj:
                Tell(kb, [f"~{Pit(i,j)}", Breeze(x, y)])

    # Wumpus Rules same as Breeze but with Stink

    for x in range(4):
        for y in range(4):
            adj = get_adjacent_cells(x, y)

            # ¬Sxy ∨ W_adj1 ∨ W_adj2 ...
            clause = [f"~{Stench(x, y)}"] + [Wumpus(i, j) for (i, j) in adj]
            Tell(kb, clause)

            # For each adjacent: ¬Wij ∨ Sxy
            for (i, j) in adj:
                Tell(kb, [f"~{Wumpus(i,j)}", Stench(x, y)])
    return kb



def print_kb_horn(kb):
    print("Knowledge Base:")
    for clause in kb:
        print(clause)


def populate_horn():
    kb = []
    cells = [(x, y) for x in range(4) for y in range(4)]
    
    # At least one Wumpus must exist
    at_least_one_wumpus = [f"{Wumpus(x,y)}" for x in range(4) for y in range(4)]
    Implication(kb, at_least_one_wumpus, "Wumpus_exists")
    
    # At most one Wumpus
    for (x1, y1), (x2, y2) in combinations(cells, 2):
        Implication(kb, [Wumpus(x1, y1), Wumpus(x2, y2)], "false")
    
    # Breeze Rules
    for x in range(4):
        for y in range(4):
            adj = get_adjacent_cells(x, y)
            
            # Pit in adjacent => Breeze
            for (i, j) in adj:
                Implication(kb, [Pit(i, j)], Breeze(x, y))
            
            # Breeze implies at least one pit in adjacent cells
            pit_options = [Pit(i, j) for (i, j) in adj]
            Implication(kb, [Breeze(x, y)], "Pit_near_" + str(x) + str(y))
            Implication(kb, ["Pit_near_" + str(x) + str(y)] + [f"~{Pit(i, j)}" for (i, j) in adj if (i, j) != adj[0]], Pit(adj[0][0], adj[0][1]))
    
    # Stench Rules
    for x in range(4):
        for y in range(4):
            adj = get_adjacent_cells(x, y)
            
            # Wumpus in adjacent => Stench
            for (i, j) in adj:
                Implication(kb, [Wumpus(i, j)], Stench(x, y))
            
            # Stench implies at least one wumpus in adjacent cells
            wumpus_options = [Wumpus(i, j) for (i, j) in adj]
            Implication(kb, [Stench(x, y)], "Wumpus_near_" + str(x) + str(y))
            Implication(kb, ["Wumpus_near_" + str(x) + str(y)] + [f"~{Wumpus(i, j)}" for (i, j) in adj if (i, j) != adj[0]], Wumpus(adj[0][0], adj[0][1]))
    
    return kb

def Fact(kb,literal):
        kb.append({'premises': [], 'conclusion': literal})

def Implication(kb,premises, conclusion):
        if isinstance(premises, str):
            premises = [premises]
        kb.append({'premises': premises, 'conclusion': conclusion})

# Task 3.3 test
kb = populate()

x, y = 0, 0
percept = wumpus_env.reset()
print(percept)
perceive_and_tell(kb,percept, x, y)
for i in range(4):
    for j in range(4):
        if unit_resolution(kb, [Wumpus(i,j)]):
            print(f"Wumpus FOUND at ({i},{j})")


# Move up
print("One up")

wumpus_env.step(TURNLEFT)
next_state, reward, done, info = wumpus_env.step(WALK)
wumpus_env.render()
print(next_state)
perceive_and_tell(kb,next_state, next_state['x'], next_state['y'])
for i in range(4):
    for j in range(4):
        if unit_resolution(kb, [Wumpus(i,j)]):
            print(f"Wumpus FOUND at ({i},{j})")


#move to the left of the pit
percept = wumpus_env.reset()
# reset kb 
kb = populate()

wumpus_env.step(TURNLEFT)
next_state, reward, done, info = wumpus_env.step(WALK)
next_state, reward, done, info = wumpus_env.step(WALK)
wumpus_env.render()
print(next_state)
perceive_and_tell(kb,next_state, next_state['x'], next_state['y'])
found = False

for i in range(4):
    for j in range(4):
        if unit_resolution(kb, [Pit(i,j)]):
            found = True
            print(f"Pit FOUND at ({i},{j})")
if found is False:
    print("Pit was not Found")

## the agent dosent need to make a full circle the pit to know where is 
next_state, reward, done, info = wumpus_env.step(WALK)
perceive_and_tell(kb,next_state, next_state['x'], next_state['y'])
next_state, reward, done, info = wumpus_env.step(TURNRIGHT)
perceive_and_tell(kb,next_state, next_state['x'], next_state['y'])
next_state, reward, done, info = wumpus_env.step(WALK)
perceive_and_tell(kb,next_state, next_state['x'], next_state['y'])
next_state, reward, done, info = wumpus_env.step(WALK)
perceive_and_tell(kb,next_state, next_state['x'], next_state['y'])
## its enoought if it goes up right and right couse it it feels BREZE on 0,2 not on 0,3 and again on 1,3 this should be enought to deduct that the pit is on 1,2
## but for some reason to be sure the agents needs to go one more time right
next_state, reward, done, info = wumpus_env.step(TURNRIGHT)
perceive_and_tell(kb,next_state, next_state['x'], next_state['y'])
next_state, reward, done, info = wumpus_env.step(WALK)
perceive_and_tell(kb,next_state, next_state['x'], next_state['y'])
next_state, reward, done, info = wumpus_env.step(WALK)
perceive_and_tell(kb,next_state, next_state['x'], next_state['y'])
next_state, reward, done, info = wumpus_env.step(TURNRIGHT)
perceive_and_tell(kb,next_state, next_state['x'], next_state['y'])
next_state, reward, done, info = wumpus_env.step(WALK)
perceive_and_tell(kb,next_state, next_state['x'], next_state['y'])
next_state, reward, done, info = wumpus_env.step(WALK)
perceive_and_tell(kb,next_state, next_state['x'], next_state['y'])
next_state, reward, done, info = wumpus_env.step(TURNRIGHT)
perceive_and_tell(kb,next_state, next_state['x'], next_state['y'])
next_state, reward, done, info = wumpus_env.step(WALK)
perceive_and_tell(kb,next_state, next_state['x'], next_state['y'])
wumpus_env.render()


found = False
for i in range(4):
    for j in range(4):
        if unit_resolution(kb, [Pit(i,j)]):
            found = True
            print(f"Pit FOUND at ({i},{j})")
if found is False:
    print("Pit was not Found")

## HORN
print("HORN")
kb = populate_horn()
print_kb_horn(kb)

x, y = 0, 0
Fact(kb, f"~{Wumpus(x, y)}")
Fact(kb, f"~{Pit(x, y)}")
percept = wumpus_env.reset()
wumpus_env.render()
print(percept)
perceive_and_tell(kb,percept, percept['x'], percept['y'],horn=True)
for i in range(4):
    for j in range(4):
        if pl_fc_entails(kb, Wumpus(i,j)):
            print(f"Wumpus FOUND at ({i},{j})")


# Move up
print("One up")

wumpus_env.step(TURNLEFT)
next_state, reward, done, info = wumpus_env.step(WALK)
wumpus_env.render()
print(next_state)
perceive_and_tell(kb,next_state, next_state['x'], next_state['y'],horn=True)
for i in range(4):
    for j in range(4):
        if pl_fc_entails(kb, Wumpus(i,j)):
            print(f"Wumpus FOUND at ({i},{j})")

#move to the left of the pint
percept = wumpus_env.reset()
# reset kb 
kb = populate_horn()

wumpus_env.step(TURNLEFT)
next_state, reward, done, info = wumpus_env.step(WALK)
next_state, reward, done, info = wumpus_env.step(WALK)
wumpus_env.render()
print(next_state)
perceive_and_tell(kb,next_state, next_state['x'], next_state['y'],horn=True)
found = False

for i in range(4):
    for j in range(4):
        if pl_fc_entails(kb, Pit(i,j)):
            found = True
            print(f"Pit FOUND at ({i},{j})")
if found is False:
    print("Pit was not Found")

## the agent dosent need to make a full circle the pit to know where is 
next_state, reward, done, info = wumpus_env.step(WALK)
perceive_and_tell(kb,next_state, next_state['x'], next_state['y'],horn=True)
next_state, reward, done, info = wumpus_env.step(TURNRIGHT)
perceive_and_tell(kb,next_state, next_state['x'], next_state['y'],horn=True)
next_state, reward, done, info = wumpus_env.step(WALK)
perceive_and_tell(kb,next_state, next_state['x'], next_state['y'],horn=True)
next_state, reward, done, info = wumpus_env.step(WALK)
perceive_and_tell(kb,next_state, next_state['x'], next_state['y'],horn=True)
## its enoought if it goes up right and right couse it it feels BREZE on 0,2 not on 0,3 and again on 1,3 this should be enought to deduct that the pit is on 1,2
## but for some reason to be sure the agents needs to go one more time right
next_state, reward, done, info = wumpus_env.step(TURNRIGHT)
perceive_and_tell(kb,next_state, next_state['x'], next_state['y'],horn=True)
next_state, reward, done, info = wumpus_env.step(WALK)
perceive_and_tell(kb,next_state, next_state['x'], next_state['y'],horn=True)
next_state, reward, done, info = wumpus_env.step(WALK)
perceive_and_tell(kb,next_state, next_state['x'], next_state['y'],horn=True)
next_state, reward, done, info = wumpus_env.step(TURNRIGHT)
perceive_and_tell(kb,next_state, next_state['x'], next_state['y'],horn=True)
next_state, reward, done, info = wumpus_env.step(WALK)
perceive_and_tell(kb,next_state, next_state['x'], next_state['y'],horn=True)
next_state, reward, done, info = wumpus_env.step(WALK)
perceive_and_tell(kb,next_state, next_state['x'], next_state['y'],horn=True)
next_state, reward, done, info = wumpus_env.step(TURNRIGHT)
perceive_and_tell(kb,next_state, next_state['x'], next_state['y'],horn=True)
next_state, reward, done, info = wumpus_env.step(WALK)
perceive_and_tell(kb,next_state, next_state['x'], next_state['y'],horn=True)
wumpus_env.render()

found = False
for i in range(4):
    for j in range(4):
        if pl_fc_entails(kb, Pit(i,j)):
            found = True
            print(f"Pit FOUND at ({i},{j})")
if found is False: 
    print("Pit was not Found")