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

def resolve(ci, cj):
    """Return the resolvent of two clauses ci and cj."""
    resolvents = []

    for li in ci:
        for lj in cj:
            if li == negate(lj):
                # Remove li and lj and merge the rest (set to remove duplicates)
                new_clause = list(set(ci + cj))
                new_clause.remove(li)
                new_clause.remove(lj)
                if new_clause not in resolvents:
                    resolvents.append(new_clause)

    return resolvents


def pl_resolution(kb, alpha):
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

def perceive_and_tell(kb,percept, x, y):
    # Assert current cell is safe (no pit/wumpus) since agent is alive
    Tell(kb, [f"~{Pit(x, y)}"])
    Tell(kb, [f"~{Wumpus(x, y)}"])
    
    # Add percept observations
    if percept['breeze']:
        Tell(kb, [Breeze(x, y)])
    else:
        Tell(kb, [f"~{Breeze(x, y)}"])

    if percept['stench']:
        Tell(kb, [Stench(x, y)])
    else:
        Tell(kb, [f"~{Stench(x, y)}"])

def is_safe(kb, x, y):
    no_pit = pl_resolution(kb, [f"~{Pit(x, y)}"])
    no_wumpus = pl_resolution(kb, [f"~{Wumpus(x, y)}"])
    return no_pit and no_wumpus

def print_kb(kb):
    print("Knowledge Base:")
    for clause in kb:
        print(" ∨ ".join(clause))

def populate():
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

    # Wumpus Rules same as Brteeze but with Stink

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




# Task 3.3 test
kb = populate()

x, y = 0, 0
percept = wumpus_env.reset()
print(percept)
perceive_and_tell(kb,percept, x, y)
print_kb(kb)
for i in range(4):
    for j in range(4):
        if pl_resolution(kb, [Wumpus(i,j)]):
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
        if pl_resolution(kb, [Wumpus(i,j)]):
            print(f"Wumpus FOUND at ({i},{j})")


#move to the left of the pint
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
        if pl_resolution(kb, [Pit(i,j)]):
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
        if pl_resolution(kb, [Pit(i,j)]):
            found = True
            print(f"Pit FOUND at ({i},{j})")
if found is False:
    print("Pit was not Found")



