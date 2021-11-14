
import sys
from croblink import *
import math
import xml.etree.ElementTree as ET
from tree_search import *
from mazeDomain import MazeDomain, State
import asyncio

CELLROWS=7
CELLCOLS=14

class MyRob(CRobLinkAngs):


    livres = set()
    visitadas = set()
    paredes = set()
    current_key = ""
    previous_pos = ""


    def __init__(self, rob_name, rob_id, angles, host):
        CRobLinkAngs.__init__(self, rob_name, rob_id, angles, host)

    # In this map the center of cell (i,j), (i in 0..6, j in 0..13) is mapped to labMap[i*2][j*2].
    # to know if there is a wall on top of cell(i,j) (i in 0..5), check if the value of labMap[i*2+1][j*2] is space or not
    def setMap(self, labMap):
        self.labMap = labMap

    def printMap(self):
        for l in reversed(self.labMap):
            print(''.join([str(l) for l in l]))

    def run(self):
        if self.status != 0:
            print("Connection refused or error")
            quit()

        state = 'stop'
        stopped_state = 'run'
        keys = []
        f = True


        while True:
            self.readSensors()

            if self.measures.endLed:
                print(self.rob_name + " exiting")
                quit()

            if f:

                if state == 'stop' and self.measures.start:
                    state = stopped_state

                if state != 'stop' and self.measures.stop:
                    stopped_state = state
                    state = 'stop'

                if state == 'run':
                    if self.measures.visitingLed==True:
                        state='wait'
                    if self.measures.ground==0:
                        self.setVisitingLed(True);
                    f = self.wander()
                elif state=='wait':
                    self.setReturningLed(True)
                    if self.measures.visitingLed==True:
                        self.setVisitingLed(False)
                    if self.measures.returningLed==True:
                        state='return'
                    self.driveMotors(0.0,0.0)
                elif state=='return':
                    if self.measures.visitingLed==True:
                        self.setVisitingLed(False)
                    if self.measures.returningLed==True:
                        self.setReturningLed(False)
                    f = self.wander(keys)
            else:
                print('Stop! \n Lets start A*\n')

                g = (843,405)
                pos = (math.trunc(self.measures.x),math.trunc(self.measures.y))
                p = MazeDomain(pos, self.visitadas, self.paredes, g)
                s = State(pos)
                problema = SearchProblem(p,s,g)
                tree = SearchTree(problema)
                res = tree.search()
                for i in res:
                    print(str(i))
                
                if not keys:
                    for j in range(1,len(res)):
                        print("path step by step")
                        print(res[j-1])
                        print(res[j])
                        keys.append(self.goTo(res[j-1],res[j]))
                
                print(keys)
                print("END")
                f =True


    # Função que traduz uma sequência de estados em inputs para o servidor
    def goTo(self,pos1,pos2):
        if pos1[1] - pos2[1] == 0: #mesma linha
            if pos1[0] < pos2[0]: # mov para a direita
                return "d"
            else: #mov para a esquerda
                return "a"
        if pos1[0] - pos2[0] == 0: #mesma coluna
            if pos1[1] < pos2[1]: # mov para baixo
                return "s"
            else: #mov para cima
                return "w"
        return ""

            

    def wander(self, keys=[]):
        center_id = 0
        left_id = 1
        right_id = 2
        back_id = 3

        lin = 0;
        rot = 0;

        x = math.trunc(self.measures.x)
        y = math.trunc (self.measures.y)
        
        pos = (x,y)

        self.visitadas.add(pos)
        #print(self.livres)
        #print(self.paredes)

        compass = self.measures.compass


        if self.measures.irSensor[center_id] <= 1.1 and not self.current_key:
            lin = 0.15

            if self.measures.irSensor[left_id] > 3:
                rot = 0.1*(1/self.measures.irSensor[left_id])
            elif self.measures.irSensor[right_id] > 3:
                rot = -0.1*(1/self.measures.irSensor[right_id])
                
        
            self.driveMotors(lin + rot/2, lin - rot/2)

        
            if self.measures.irSensor[left_id] > 1.1:

                if compass < 60 and compass > -60:
                    pos = (x,y+1)
                elif compass < 120 and compass > 60:
                    pos = (x-1,y)
                elif compass < -120 and compass > 120:
                    pos = (x,y-1)
                elif compass < -60 and compass > -120:
                    pos = (x+1,y)

                self.paredes.add(pos)
                
            if self.measures.irSensor[right_id] > 1.1:
                
                if compass < 60 and compass > -60:
                    pos = (x,y-1)
                elif compass < 120 and compass > 60:
                    pos = (x+1,y)
                elif compass < -120 and compass > 120:
                    pos = (x,y+1)
                elif compass < -60 and compass > -120:
                    pos = (x-1,y)

                self.paredes.add(pos)
            return True
        else:
            if keys or self.current_key:
                if not self.current_key:
                    self.current_key = keys.pop(0)

                if self.current_key == "d" and (compass > 4 or compass < 4): 
                    self.rotate(compass, 0)

                elif self.current_key == "a" and compass > -176 and compass < 176:
                    self.rotate(compass, 180)

                elif self.current_key == "s" and (compass > -86 or compass < -94):
                    self.rotate(compass, -90)

                elif self.current_key == "w" and (compass > 94 or compass < 86):
                    self.rotate(compass, 90)
                else:
                    #se já tiver avançado para a proxima casa -> passar para a proxima direçao
                    if self.previous_pos != pos:
                        self.current_key = ""
                    else:
                        self.previous_pos = pos
                        self.driveMotors(0.15, 0.15)

            return False

    #Supostamente a cada driveMotors no maximo (0.15,-0.15) ele roda 60º 
    # Ainda não tem em conta o erro
    def rotate(self, current_angle, goal_angle):
        abs_difference = abs(goal_angle-abs(current_angle))
        motor_strength = (abs_difference * 0.15)/60
        print(motor_strength)
        #tentar arranjar outra forma de verificar qual a rotação mais proxima
        if goal_angle > current_angle and current_angle > -90:
            self.driveMotors(-motor_strength, motor_strength)
            
        else: 
            self.driveMotors(motor_strength, -motor_strength)



        """
        elif self.measures.irSensor[left_id] > self.measures.irSensor[right_id]:
            rot = 0.15
            self.driveMotors(lin + rot, lin - rot)
        elif self.measures.irSensor[right_id] > self.measures.irSensor[left_id]:
            rot = -0.15
            self.driveMotors(lin + rot, lin - rot)
        """
    

                



class Map():
    def __init__(self, filename):
        tree = ET.parse(filename)
        root = tree.getroot()
        
        self.labMap = [[' '] * (CELLCOLS*2-1) for i in range(CELLROWS*2-1) ]
        i=1
        for child in root.iter('Row'):
           line=child.attrib['Pattern']
           row =int(child.attrib['Pos'])
           if row % 2 == 0:  # this line defines vertical lines
               for c in range(len(line)):
                   if (c+1) % 3 == 0:
                       if line[c] == '|':
                           self.labMap[row][(c+1)//3*2-1]='|'
                       else:
                           None
           else:  # this line defines horizontal lines
               for c in range(len(line)):
                   if c % 3 == 0:
                       if line[c] == '-':
                           self.labMap[row][c//3*2]='-'
                       else:
                           None
               
           i=i+1


rob_name = "pClient1"
host = "localhost"
pos = 1
mapc = None

for i in range(1, len(sys.argv),2):
    if (sys.argv[i] == "--host" or sys.argv[i] == "-h") and i != len(sys.argv) - 1:
        host = sys.argv[i + 1]
    elif (sys.argv[i] == "--pos" or sys.argv[i] == "-p") and i != len(sys.argv) - 1:
        pos = int(sys.argv[i + 1])
    elif (sys.argv[i] == "--robname" or sys.argv[i] == "-p") and i != len(sys.argv) - 1:
        rob_name = sys.argv[i + 1]
    elif (sys.argv[i] == "--map" or sys.argv[i] == "-m") and i != len(sys.argv) - 1:
        mapc = Map(sys.argv[i + 1])
    else:
        print("Unkown argument", sys.argv[i])
        quit()

if __name__ == '__main__':
    rob=MyRob(rob_name,pos,[0.0,90.0,-90.0,180.0],host)
    if mapc != None:
        rob.setMap(mapc.labMap)
        rob.printMap()
    
    rob.run()
