from tree_search import *
import math


class MazeDomain(SearchDomain):

    def __init__(self,rato,livres,paredes,goal):
        self.rato = rato
        self.livres = livres
        self.paredes = paredes
        self.goal = goal
        self.dict = None


    # lista de accoes possiveis num estado
    def actions(self, state):
        pos = state.rato
        
        self.dict = {'a' : (pos[0]-1,pos[1]),
                     'd' : (pos[0]+1,pos[1]),
                     's' : (pos[0],pos[1]-1),
                     'w' : (pos[0],pos[1]+1)}
        actions = []
        for p in self.dict:
            if self.dict[p] not in self.paredes and self.dict[p] in self.livres:
                actions.append(p)
        return actions

    # resultado de uma accao num estado, ou seja, o estado seguinte
    def result(self, state, action):
        return State(self.dict[action])

    # custo de uma accao num estado
    def cost(self, state, action):
        return 1

    # custo estimado de chegar de um estado a outro
    def heuristic(self, state=None):
        return math.sqrt(math.pow((state.rato[0]-self.goal[0]),2) + math.pow((state.rato[1]-self.goal[1]),2))

    # test if the given "goal" is satisfied in "state"
    def satisfies(self, state, goal):
        return state.rato == goal



# Classe que define um estado
# Posicao do robo - self.rato (x,y)
class State():
    def __init__(self, rato):
        self.rato = rato

    def __str__(self):
        return "state(" + str(self.rato) + ")"


