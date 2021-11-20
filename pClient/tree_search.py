from abc import ABC, abstractmethod
import asyncio
import sys
import heapq


# Dominios de pesquisa
# Permitem calcular
# as accoes possiveis em cada estado, etc
class SearchDomain(ABC):

    # construtor
    @abstractmethod
    def __init__(self):
        pass

    # lista de accoes possiveis num estado
    @abstractmethod
    def actions(self, state):
        pass

    # resultado de uma accao num estado, ou seja, o estado seguinte
    @abstractmethod
    def result(self, state, action):
        pass

    # custo de uma accao num estado
    @abstractmethod
    def cost(self, state, action):
        pass

    # custo estimado de chegar de um estado a outro
    @abstractmethod
    def heuristic(self, state=None):
        pass

    # test if the given "goal" is satisfied in "state"
    @abstractmethod
    def satisfies(self, state, goal):
        pass


# Problemas concretos a resolver
# dentro de um determinado domínio
class SearchProblem:
    def __init__(self, domain, initial, goal):
        self.domain = domain
        self.initial = initial
        self.goal = goal
    def goal_test(self, state):
        return self.domain.satisfies(state,self.goal, self.domain.extra_goals)

# Nós de uma árvore de pesquisa
class SearchNode:
    def __init__(self,state,parent): 
        self.state = state
        self.parent = parent
        self.astar = 0
        self.heuristic = 0
        self.cost = 0
        self.path = set()

    def __str__(self):
        return "no(" + str(self.state) + "," + str(self.parent) + ")"
    def __repr__(self):
        return str(self)
    def __lt__(self, ob1):
        return self.astar < ob1.astar

# Árvore de pesquisa
class SearchTree:

    # construtor
    def __init__(self,problem): 
        self.problem = problem
        self.root = SearchNode(problem.initial, None)
        self.open_nodes = [self.root]

    # obter o caminho (sequencia de estados) da raiz ate um no
    def get_path(self,node):
        if node.parent == None:
          return [node.state.rato]
        
        path = self.get_path(node.parent)
        path.append(node.state.rato)
        return(path)

    # procurar a solucao
    def search(self):
        heapq.heappush(self.open_nodes,self.root)

        while self.open_nodes != []:

            node = heapq.heappop(self.open_nodes)

            if node.parent != None:
                node.path = node.parent.path
                node.path.add(node.state)
            else:
                node.path.add(node.state)
            
            if self.problem.goal_test(node.state):
                self.solution = node
                return self.get_path(node)

            actions = self.problem.domain.actions(node.state)
            #print(actions)
            for a in actions:
                newstate = self.problem.domain.result(node.state,a)
                if newstate != None:
                    
                    if newstate not in node.path:
                        newnode = SearchNode(newstate,node)

                        newnode.heuristic = self.problem.domain.heuristic(newstate)

                        """
                        if(node.state.boxes != newnode.state.boxes):
                            newnode.heuristic = self.problem.domain.heuristic(newstate)
                        else:
                            newnode.heuristic = node.heuristic
                        """

                        newnode.cost = node.cost + 1
                        newnode.astar = newnode.heuristic + newnode.cost
                        
                        heapq.heappush(self.open_nodes,newnode)
                   
        return None
