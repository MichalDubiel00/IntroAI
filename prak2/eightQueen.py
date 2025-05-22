import random

#[0,2,3,4,5,6,7,7] index represnts col value represents row
class ChessBoard:
    def __init__(self, initial_state=None):
        self.size = 8
        if initial_state is None:
            self.initial_state = [random.randint(0, 7) for _ in range(self.size)]
        else:
            self.initial_state = initial_state

    def heuristic(self, state):
        conflicts = 0
        for i in range(self.size):
            for j in range(i+1, self.size):
                if state[i] == state[j]:
                    conflicts += 1
                elif abs(state[i] - state[j]) == abs(i - j):
                    conflicts += 1
        return conflicts

    def print_board(self, state):
        for row in range(self.size - 1, -1, -1):
            row_str = str(row + 1)
            for col in range(self.size):
                if state[col] == row:
                    row_str += "|Q|"
                elif (row + col) % 2 == 0:
                    row_str += "|□|"
                else :
                    row_str += "|■|"
            print(row_str)
        print("  a  b  c  d  e  f  g  h")

class GeneticSolver:
    def __init__(self, population_size, mutation_rate, board):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.board = board
        self.population = self.generate_initial_population("inv_row")

    def generate_initial_population(self, selection="inv_row"):
        population = []
        if selection == "inv_row":
            for _ in range(self.population_size):
                individual = list(range(8))
                random.shuffle(individual)
                population.append(individual)
        else:
            for _ in range(self.population_size):
                individual = [random.randint(0, 7) for _ in range(8)]
                population.append(individual)
        return population

    def fitness(self, ind):
        return 28 - self.board.heuristic(ind)
    #pmx_crossover is better for 8 queens but this was used in lecture and is easier to write ¯\_(ツ)_/¯
    def reproduce(self,x, y):
        n = len(x)
        c = random.randint(1, n-1)
        return x[:c] + y[c:]
    #fine i wrote it (bit of help from chatgpt :))
    def pmx_crossover(self, parent_a, parent_b):
     size = len(parent_a)
     cx1 = random.randint(0, size - 2)
     cx2 = random.randint(cx1 + 1, size - 1)
     child = [-1] * size
     #copy middle part from parent_a
     child[cx1:cx2+1] = parent_a[cx1:cx2+1]
     # Map from parent_b 
     # compare middle parent b and child
     # map diffient values
     # replace positions found in middle with map
     for i in range(cx1, cx2 + 1):
         if parent_b[i] not in child[cx1:cx2+1]:
             val = parent_b[i]
             while True:
                 pos = parent_a.index(val)
                 if pos < cx1 or pos > cx2:
                     child[pos] = parent_b[i]
                     break
                 else:
                     val = parent_b[pos]
     for i in range(size):
         if child[i] == -1:
             if parent_b[i] not in child:
                 child[i] = parent_b[i]
             else:
                 for elem in parent_b:
                     if elem not in child:
                         child[i] = elem
                         break
     return child
    def mutate(self, individual):
        if random.random() < self.mutation_rate:
            col1, col2 = random.sample(range(8), 2)
            individual[col1], individual[col2] = individual[col2], individual[col1]
        return individual

    def select_parent(self, population):
        fitnesses = [self.fitness(ind) for ind in population]
        total_fitness = sum(fitnesses)
        probabilities = [f / total_fitness for f in fitnesses]
        return random.choices(population, weights=probabilities, k=1)[0]

    def solve(self, max_generations=1000,cross = "pmx"):
        best = max(self.population, key=self.fitness)
        for gen in range(max_generations):
            new_population = [best.copy()]
            while len(new_population) < self.population_size:
                parent_a = self.select_parent(self.population)
                parent_b = self.select_parent(self.population)
                if cross == "pmx" :
                    child = self.pmx_crossover(parent_a, parent_b)
                else :
                    child = self.reproduce(parent_a, parent_b)
                child = self.mutate(child)
                new_population.append(child)
            self.population = new_population
            current_best = max(self.population, key=self.fitness)
            if self.fitness(current_best) > self.fitness(best):
                best = current_best.copy()
            print(f"Gen {gen}: Best Fitness: {self.fitness(best)}")
            if self.fitness(best) == 28:
                break
        return best

# Example Usage:
board = ChessBoard([3,2,1,4,3,2,1,2])
print("Initial State Conflicts:", board.heuristic(board.initial_state))
board.print_board(board.initial_state)

solver = GeneticSolver(population_size=100, mutation_rate=0.1, board=board)
solution = solver.solve(max_generations=100,cross="pmx")
print("Solution Conflicts:", board.heuristic(solution))
board.print_board(solution)