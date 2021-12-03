
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
    initialPos = (0,0)
    mapArray = [[' ' for x in range(56)] for y in range(28)]
    #x linha, y coluna


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
        path = []
        f = True

        self.readSensors()

        self.initialPos = (math.trunc(self.measures.x),math.trunc(self.measures.y))

        print("hello\n")
        while True:
            self.readSensors()
            """
            if self.measures.endLed:
                print(self.rob_name + " exiting")
                quit()
            """
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
                    f = self.wander()

                elif state=='goTo':
                    currPos = (math.trunc(self.measures.x),math.trunc(self.measures.y))
                    currPos = (currPos[0]-self.initialPos[0],currPos[1]-self.initialPos[1])
                    
                    if len(path) > 1:
                        state = self.goTo(path[0],path[1])
                    elif currPos == path[0]:
                        state='run'
                        print("Done Walking!")
                    
                elif state=='rotLeft':
                    compass = self.measures.compass
                    #print(compass)

                    #if compass > 170 or compass < -170:
                    if compass > 178 or compass < -178:
                        #print("rotate done!\n")
                        state = 'walk'
                        path.pop(0)
                        self.walk()


                    else:
                        self.rotation(180)
                        #print("rotating!\n")

                elif state=='rotRight':
                    compass = self.measures.compass

                    #if compass < 10 and compass > -10:
                    if compass < 2 and compass > -2:
                        state = 'walk'
                        path.pop(0)
                        self.walk()

                    else:
                        self.rotation(0)

                elif state=='rotUp':
                    compass = self.measures.compass

                    #if compass < 100 and compass > 80:
                    if compass < 92 and compass > 88:
                        state = 'walk'
                        path.pop(0)
                        self.walk()

                    else:
                        self.rotation(90)

                elif state=='rotDown':
                    compass = self.measures.compass

                    #if compass < -80 and compass > -100:
                    if compass < -88 and compass > -92:    
                        state = 'walk'
                        path.pop(0)
                        self.walk()

                    else:
                        self.rotation(-90)

                elif state=='walk':
                    currPos = (math.trunc(self.measures.x),math.trunc(self.measures.y))
                    currPos = (currPos[0]-self.initialPos[0],currPos[1]-self.initialPos[1])

                    if currPos != path[0]:
                        self.walk()
                    else:
                        state='goTo'


            else:
                print('Stop! \n Lets start A*\n')

                print("Visited cells: ")
                print(self.visitadas)
                print("\nParedes: ")
                print(self.paredes)
                
                pos = (math.trunc(self.measures.x),math.trunc(self.measures.y))
                pos = (pos[0]-self.initialPos[0],pos[1]-self.initialPos[1])

                g = self.searchFreeCell(pos)
                p = MazeDomain(pos, self.visitadas, self.paredes, g, self.livres)
                s = State(pos)
                problema = SearchProblem(p,s,g)
                tree = SearchTree(problema)

                print("\nStart")
                print(pos)
                print("Finish")
                print(g)

                path = tree.search()
                print("Solution: ")
                print(path)
                
                state = 'goTo'
                print("END")
                f =True

    
    # Função que procura uma celula livre nao visitada
    def searchFreeCell(self,pos):
        print("Searching for free cell")
        best = (10000,(0,0))

        self.livres.difference_update(self.visitadas)

        print("\nLivres: ")
        print(self.livres)

        for p in self.livres:
            dist = math.sqrt(math.pow((p[0]-pos[0]),2) + math.pow((p[1]-pos[1]),2))
            if dist < best[0]:
                best = (dist, p)
        print("Best: " + str(best))
        self.visitadas.add(best[1])
        
        if self.livres:
            self.livres.remove(best[1])
        else:
            print("No more free cells, quitting.")
            quit()
        """
        if best[1] in self.paredes:
            self.paredes.remove(best[1])
        """


        return best[1]


    def goTo(self,pos1,pos2):

        pos1Abs = (abs(pos1[0]),abs(pos1[1]))
        pos2Abs = (abs(pos2[0]),abs(pos2[1]))

        
        if pos1Abs[1] - pos2Abs[1] == 0: #mesma linha
            if pos1[0] < pos2[0]: # mov para a direita
                
                print("direita")
                return 'rotRight'
            else: #mov para a esquerda
                
                print("esquerda")
                return 'rotLeft'

        elif pos1Abs[0] - pos2Abs[0] == 0: #mesma coluna
            if pos1[1] > pos2[1]: # mov para baixo
                
                print("baixo")
                return 'rotDown'

            else: #mov para cima
                
                print("cima")
                return 'rotUp'
                
        
        """
        currPos = (math.trunc(self.measures.x),math.trunc(self.measures.y))
        print(currPos)
        self.driveMotors(0.15,0.15)
        while currPos != pos2:
            self.driveMotors(0.15,0.15)
        """

    def checkNearby(self,x,y,compass):

        center_id = 0
        left_id = 1
        right_id = 2
        back_id = 3
        
        if self.measures.irSensor[center_id] > 1.1:
    
            if compass <= 30 and compass >= -30:
                pos = (x+1,y)
            elif compass <= 120 and compass >= 60:
                pos = (x,y+1)
            elif compass <= -120 or compass >= 120:
                pos = (x-1,y)
            elif compass <= -60 and compass >= -120:
                pos = (x,y-1)

            if pos not in self.livres:
                self.paredes.add(pos)

        if self.measures.irSensor[left_id] > 1.1:

            if compass <= 30 and compass >= -30:
                pos = (x,y+1)
            elif compass <= 120 and compass >= 60:
                pos = (x-1,y)
            elif compass <= -120 or compass >= 120:
                pos = (x,y-1)
            elif compass <= -60 and compass >= -120:
                pos = (x+1,y)

            if pos not in self.livres:
                self.paredes.add(pos)
        else:
            #print("\nFree cell in front of sensor left\n")
            if compass <= 30 and compass >= -30:
                pos = (x,y+1)
            elif compass <= 120 and compass >= 60:
                pos = (x-1,y)
            elif compass <= -120 or compass >= 120:
                pos = (x,y-1)
            elif compass <= -60 and compass >= -120:
                pos = (x+1,y)
            
            if pos in self.paredes:
                self.paredes.remove(pos)
            self.livres.add(pos)
            
        if self.measures.irSensor[right_id] > 1.1:
            
            if compass <= 30 and compass >= -30:
                pos = (x,y-1)
            elif compass <= 120 and compass >= 60:
                pos = (x+1,y)
            elif compass <= -120 or compass >= 120:
                pos = (x,y+1)
            elif compass <= -60 and compass >= -120:
                pos = (x-1,y)

            if pos not in self.livres:
                self.paredes.add(pos)

        else:
            #print("\nFree cell in front of sensor right\n")
            if compass <= 30 and compass >= -30:
                pos = (x,y-1)
            elif compass <= 120 and compass >= 60:
                pos = (x+1,y)
            elif compass <= -120 or compass >= 120:
                pos = (x,y+1)
            elif compass <= -60 and compass >= -120:
                pos = (x-1,y)
            
            if pos in self.paredes:
                self.paredes.remove(pos)
            self.livres.add(pos)
        
        if self.measures.irSensor[back_id] > 1.1:
            
            if compass <= 30 and compass >= -30:
                pos = (x-1,y)
            elif compass <= 120 and compass >= 60:
                pos = (x,y-1)
            elif compass <= -120 or compass >= 120:
                pos = (x+1,y)
            elif compass <= -60 and compass >= -120:
                pos = (x,y+1)
            
            if pos not in self.livres:
                self.paredes.add(pos)

        else:
            #print("\nFree cell in front of sensor back\n")
            if compass <= 30 and compass >= -30:
                pos = (x-1,y)
            elif compass <= 120 and compass >= 60:
                pos = (x,y-1)
            elif compass <= -120 or compass >= 120:
                pos = (x+1,y)
            elif compass <= -60 and compass >= -120:
                pos = (x,y+1)

            if pos in self.paredes:
                self.paredes.remove(pos)
            self.livres.add(pos)
    
    def walk(self):
        center_id = 0
        left_id = 1
        right_id = 2
        back_id = 3

        compass = self.measures.compass
        lin = 0.15
        rot = 0.0
        """
        diff = self.measures.irSensor[left_id] - self.measures.irSensor[right_id]

        if diff <= 0:
            rot = 0.01*(1/self.measures.irSensor[right_id])        
        else:
            rot = -0.01*(1/self.measures.irSensor[left_id])
        print(rot/2)
        self.driveMotors(lin + rot/2, lin - rot/2)
        """
        if compass <= 45 and compass >= -45:
            angleGoal = 0
        elif compass <= 135 and compass > 45:
            angleGoal = 90
        elif compass < -135 or compass > 135:
            angleGoal = 180
        elif compass >= -135 and compass < -45:
            angleGoal = -90
        
        if angleGoal == 180:
            if (compass > -178 and compass <= 0) or (compass < 178 and compass > 0):
                self.rotation(180)
            else: 
                self.driveMotors(0.15, 0.15)
        else:
            if compass > angleGoal + 2 or compass < angleGoal - 2:
                self.rotation(angleGoal)
            else: 
                self.driveMotors(0.15, 0.15)

        #if self.measures.irSensor[left_id] > 3:
        #    rot = 0.01*(1/self.measures.irSensor[left_id])
        #elif self.measures.irSensor[right_id] > 3:
        #    rot = -0.01*(1/self.measures.irSensor[right_id])

        #print(rot)
        #self.driveMotors(lin + rot/2, lin - rot/2)
    

            

    def wander(self):
        center_id = 0
        left_id = 1
        right_id = 2
        back_id = 3

        lin = 0;
        rot = 0;

        x1 = self.measures.x
        y2 = self.measures.y
        
        x = math.trunc(x1)
        y = math.trunc(y2)

        pos = (x,y)
        posM = (pos[0]-self.initialPos[0],pos[1]-self.initialPos[1])
        
        threshold = 1
        posM_threshold1 = (abs(x) + threshold, abs(y) + threshold)
        posM_threshold2 = (abs(x) - threshold, abs(y) - threshold)
        #print(posM_threshold)
        #print(self.measures.x)
        #print(self.measures.y)
        self.visitadas.add(posM)
        #print(self.livres)
        #print(self.paredes)


        compass = self.measures.compass

        for i in self.livres:
            #mapping_x = i[0] - self.initialPos[0]
            #mapping_y = i[1] - self.initialPos[1]
            self.mapArray[13 - i[1]][27 + i[0]] = 'O'

        for i in self.visitadas:
            #mapping_x = i[0] - self.initialPos[0]
            #mapping_y = i[1] - self.initialPos[1]
            self.mapArray[13 - i[1]][27 + i[0]] = 'X'
        
        for i in self.paredes:
            #mapping_x = i[0] - self.initialPos[0]
            #mapping_y = i[1] - self.initialPos[1]

            if i[1] % 2 == 0:
                if i[0] % 2 != 0:
                    #print(mapping_x, mapping_y)
                    self.mapArray[13 - i[1]][27 + i[0]] = '|'
            else:
                if i[0] % 2 == 0:
                    self.mapArray[13 - i[1]][27 + i[0]] = '-'

        self.mapArray[13][27] = 'I'

        with open('mapping.out', 'w') as f:
            for i in range(28):
                for j in range(56):
                    f.write(self.mapArray[i][j])
                f.write('\n')

        
        if posM[0] % 2 == 0 and posM[1] % 2 == 0:

            if x1 <= posM_threshold1[0] and x1 >= posM_threshold2[0]:
            
                if y2 <= posM_threshold1[1] and y2 >= posM_threshold2[1]:

                    self.checkNearby(posM[0],posM[1],compass)
                    
                    if self.measures.irSensor[center_id] <= 1.5:
                        self.walk()
                        return True
                    else:
                
                        self.driveMotors(0, 0)

                        print("\nParedes:" + str(self.paredes) + '\n')

                        return False
                    
                else:
                    self.walk()
                    if self.measures.irSensor[center_id] > 1.5:
                        #self.checkNearby(posM[0],posM[1],compass)
                        self.driveMotors(0,0)
                        return False

                    return True
                

            else:
                self.walk()
                if self.measures.irSensor[center_id] > 1.5:
                    #self.checkNearby(posM[0],posM[1],compass)
                    self.driveMotors(0,0)
                    return False

                return True
            
        else:
            if self.measures.irSensor[center_id] > 1.6:
                #self.checkNearby(posM[0],pos[1],compass)
                self.driveMotors(0,0)
                return False
            self.walk()
            return True

    def rotation(self, angleGoal):
        compass = self.measures.compass
        motor_speed = 0.10

        if angleGoal == 180:
            diff = angleGoal - abs(compass)
        else:
            diff = angleGoal - compass
                
        if abs(diff) < 15:
            motor_speed = 0.01

        if angleGoal == 0:
            if compass > 0 and compass <= 180:
                self.driveMotors(motor_speed,-motor_speed)
            elif compass < 0 and compass >= -180:
                self.driveMotors(-motor_speed,motor_speed)
        elif angleGoal == 90:
            if (compass > 90 and compass <= 180) or (compass <= -90 and compass >=-180):
                self.driveMotors(motor_speed,-motor_speed)
            elif compass < 90 and compass > -90:
                self.driveMotors(-motor_speed,motor_speed)
        elif angleGoal == 180:
            if compass >= 0 and compass < 180:
                self.driveMotors(-motor_speed,motor_speed)
            elif compass < 0 and compass > -180:
                self.driveMotors(motor_speed,-motor_speed)
        elif angleGoal == -90:
            if (compass >= 90 and compass <= 180) or (compass < -90 and compass >=-180):
                self.driveMotors(-motor_speed,motor_speed)
            elif compass < 90 and compass > -90:
                self.driveMotors(motor_speed,-motor_speed)
        






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
