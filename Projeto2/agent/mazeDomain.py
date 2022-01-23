from tree_search import *
import math


class MazeDomain(SearchDomain):

    def __init__(self,rato,livres,paredes,goal,extra_goals):
        self.rato = rato
        self.livres = livres
        self.paredes = paredes
        self.goal = goal
        self.extra_goals = extra_goals
        self.dict = None


    # lista de accoes possiveis num estado
    def actions(self, state):
        pos = state.rato
        
        self.dict = {'a' : (pos[0]-1,pos[1]),
                     'd' : (pos[0]+1,pos[1]),
                     's' : (pos[0],pos[1]-1),
                     'w' : (pos[0],pos[1]+1)}
        actions = set()
        for p in self.dict:
            if self.dict[p] not in self.paredes and self.dict[p] in self.livres:
                actions.add(p)
        return actions

    # resultado de uma accao num estado, ou seja, o estado seguinte
    def result(self, state, action):
        return State(self.dict[action])

    def result2(self, state, action):

        set1 = set(state.beacons)
        set2 = set(self.goal)

        if self.dict[action] in set2 and set2.issubset(set1) and self.dict[action] == self.goal[0]:
            return State(self.dict[action], state.beacons.append[self.dict[action]])

        if self.dict[action] in set2 and self.dict[action] not in set1:
            print("moshi moshi")
            print(self.dict[action])
            print(state.beacons)
            print(self.goal)
            state.beacons.append(self.dict[action])
            b = state.beacons
            print(b)
            return State(self.dict[action], b)
        else:
            """
            print("--------------------------")
            print(self.dict[action])
            print(state.beacons)
            print("--------------------------")
            """
            return State(self.dict[action], state.beacons)

    # custo de uma accao num estado
    def cost(self, state, action):
        return 1

    # custo estimado de chegar de um estado a outro
    def heuristic(self, state=None):
        return math.sqrt(math.pow((state.rato[0]-self.goal[0]),2) + math.pow((state.rato[1]-self.goal[1]),2))

    # custo estimado de chegar de um estado a outro
    def heuristic2(self, state=None):
        h = 0
        for i in self.goal:
            h = h + math.sqrt(math.pow((state.rato[0]-i[0]),2) + math.pow((state.rato[1]-i[1]),2))
        return h
        

    # test if the given "goal" is satisfied in "state"
    def satisfies(self, state, goal, extra_goals):
        if state.rato == goal or state.rato in extra_goals:
            return True

    # test if the given "goal" is satisfied in "state"
    def satisfies2(self, state, goals):
        if len(state.beacons) != len(goals):
            return False
        else:
            print(state.beacons)
            return state.beacons[0] == goals[0] and state.beacons[len(state.beacons)-1] == goals[len(goals)-1] and goals[1] in state.beacons

# Classe que define um estado
# Posicao do robo - self.rato (x,y)
class State():
    def __init__(self, rato, beacons = []):
        self.rato = rato
        self.beacons = beacons

    def __str__(self):
        return "state(" + str(self.rato) + ")"


