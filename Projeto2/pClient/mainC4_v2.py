
import sys
from croblink import *
import math
import xml.etree.ElementTree as ET
from tree_search import *
from mazeDomain import MazeDomain, State
import asyncio
import numpy as np
import matplotlib.pyplot as plt

CELLROWS=7
CELLCOLS=14

class MyRob(CRobLinkAngs):


    livres = set()
    visitadas = set()
    paredes = set()
    beacons = set()
    state = 'stop'
    initialPos = (0,0)
    mapArray = [[' ' for x in range(56)] for y in range(28)]
    #x linha, y coluna

    outsr = 0
    outsl = 0
    teta = 0

    xt = 0
    yt = 0

    previous_l = 0
    previous_r = 0

    currx = 0
    curry = 0

    diffx = []
    diffy = []

    allCalcx = []
    allCalcy = []

    allRx = []
    allRy = []

    lastTick = 0

    finishing = False
    fpx = 0
    fpy = 0

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


        state = self.state
        stopped_state = 'run'
        path = []
        f = True

        self.readSensors()

        #self.initialPos = (math.trunc(self.measures.x),math.trunc(self.measures.y))

        self.testing = (self.measures.x,self.measures.y)
        self.initialPos = (0,0)

        self.fpx = self.measures.x
        self.fpy = self.measures.y

        #self.allRx.append(self.fpx)
        #self.allRy.append(self.fpy)

        #print("Initial pos: " + str(self.initialPos))

        ##print("hello\n")
        while True:
            self.readSensors()
            #print("\n" + str(self.measures.time) + "\n")
            self.lastTick = self.measures.time
            if self.measures.endLed:
                #print(self.rob_name + " exiting")
                quit()

            if self.measures.time == 4990:
                """
                yvals = []
                #print(self.lastTick)

                yvals.append(0)
                self.diffx.append(0 - self.allRx[0])
                self.diffy.append(0 - self.allRy[0])

                
                for i in range(1,len(self.allRx)):
                    yvals.append(i)
                    self.diffx.append(self.allCalcx[i] - self.allRx[i])
                    self.diffy.append(self.allCalcy[i] - self.allRy[i])

                #print("amount of ticks: " + str(len(yvals)))
                #print("amount of diffx: " + str(len(self.diffx)))
                #print("amount of diffy: " + str(len(self.diffy)))
                
                plt.plot(self.diffx, yvals, label = "diff x")
                plt.plot(self.diffy, yvals, label = "diff y")

                # naming the x axis
                plt.xlabel('x - axis')
                # naming the y axis
                plt.ylabel('y - axis')
                # giving a title to my graph
                plt.title('Two lines on same graph!')
                
                # show a legend on the plot
                plt.legend()
                
                # function to show the plot
                plt.show()
                """

                self.drawMap()
                self.final_path()
            
            if f:
                #print("Inside F")

                if state == 'stop' and self.measures.start:
                    state = stopped_state

                if state != 'stop' and self.measures.stop:
                    stopped_state = state
                    state = 'stop'

                if state == 'run':
                    #print("ENTERING STATE RUN")
                    
                    if self.measures.ground==0:
                        self.setVisitingLed(True);
                    res = self.wander()
                    f = res[0]
                    if res[1]:
                        state = 'search_path'
                        self.driveMotors(0.0,0.0)
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
                    res = self.wander()
                    f = res[0]
                    if res[1]:
                        state = 'search_path'
                        self.driveMotors(0.0,0.0)

                elif state=='goTo':
                    #currPos = (math.trunc(self.measures.x),math.trunc(self.measures.y))
                    #currPos = (currPos[0]-math.trunc(self.initialPos[0]),currPos[1]-math.trunc(self.initialPos[1]))
                    
                    #print("ENTERING STATE goto")
                    
                    #currPos = (self.measures.x, self.measures.y)
                    #currPos = (round(currPos[0]-self.initialPos[0]),round(currPos[1]-self.initialPos[1]))

                    currPos = (round(self.currx), round(self.curry))
                    #currPos = (round(currPos[0]-self.initialPos[0]),round(currPos[1]-self.initialPos[1]))
                    
                    if len(path) > 1:
                        #print("still more path")
                        if self.measures.irSensor[0] > 1.1:
                            self.correctPos()
                            self.driveMotors(0,0)
                            self.calcPos(0,0)
                        else:
                            self.driveMotors(0,0)
                            self.calcPos(0,0)
                            #self.calcPos(self.previous_l,self.previous_r)
                        state = self.goTo(path[0],path[1])
                    elif currPos == path[0]:
                        #print("in position")
                        self.calcPos(self.previous_l,self.previous_r)
                        ##print("Done Walking!")
                        if self.finishing:
                            self.driveMotors(0,0)
                            
                            #print("All done, quitting.")
                                                        
                            self.finish()
                            """
                            yvals = []
                            #print(self.lastTick)

                            
                            for i in range(0,len(self.diffx)):
                                yvals.append(i)

                            #print("amount of ticks: " + str(len(yvals)))
                            #print("amount of diffx: " + str(len(self.diffx)))
                            #print("amount of diffy: " + str(len(self.diffy)))
                            
                            plt.plot(self.diffx, yvals, label = "diff x")
                            plt.plot(self.diffy, yvals, label = "diff y")

                            # naming the x axis
                            plt.xlabel('x - axis')
                            # naming the y axis
                            plt.ylabel('y - axis')
                            # giving a title to my graph
                            plt.title('Two lines on same graph!')
                            
                            # show a legend on the plot
                            plt.legend()
                            
                            # function to show the plot
                            plt.show()
                            """


                        else:
                            state='run'
                
                elif state=='rotLeft':
                    #print("ENTERING STATE ROT LEFT")
                    compass = self.measures.compass
                    ##print(compass)

                    #if compass > 170 or compass < -170:
                    if compass > 178 or compass < -178:
                        ##print("rotate done!\n")
                        state = 'walk'
                        path.pop(0)
                        self.walk()


                    else:
                        (l,r) = self.rotation(180)
                        self.driveMotors(l,r)
                        self.calcPos(l,r)

                        ##print("rotating!\n")

                elif state=='rotRight':
                    #print("ENTERING STATE ROT RIGHT")

                    compass = self.measures.compass

                    #if compass < 10 and compass > -10:
                    if compass < 2 and compass > -2:
                        state = 'walk'
                        path.pop(0)
                        self.walk()

                    else:
                        (l,r) = self.rotation(0)
                        self.driveMotors(l,r)
                        self.calcPos(l,r)


                elif state=='rotUp':
                    #print("ENTERING STATE ROT UP")

                    compass = self.measures.compass

                    #if compass < 100 and compass > 80:
                    if compass < 92 and compass > 88:
                        state = 'walk'
                        path.pop(0)
                        self.walk()

                    else:
                        (l,r) = self.rotation(90)
                        self.driveMotors(l,r)
                        self.calcPos(l,r)


                elif state=='rotDown':
                    #print("ENTERING STATE ROT DOWN")

                    compass = self.measures.compass

                    #if compass < -80 and compass > -100:
                    if compass < -88 and compass > -92:    
                        state = 'walk'
                        path.pop(0)
                        self.walk()

                    else:
                        (l,r) = self.rotation(-90)
                        self.driveMotors(l,r)
                        self.calcPos(l,r)

                elif state=='walk':
                    #print("ENTERING STATE WALK")

                    #print(self.initialPos)
                    #currPos = (self.measures.x, self.measures.y)
                    ##print(currPos)
                    #currPos = (round(currPos[0]-self.initialPos[0]),round(currPos[1]-self.initialPos[1]))
                    tempPos = self.currx, self.curry
                    
                    threshold = 0.2
                    path_threshold1 = (abs(path[0][0]) + threshold, abs(path[0][1]) + threshold)
                    path_threshold2 = (abs(path[0][0]) - threshold, abs(path[0][1]) - threshold)
                    #print(tempPos)
                    #print(path[0])
                    #print(path_threshold1)
                    #print(path_threshold2)
                    x1 = abs(tempPos[0])
                    y2 = abs(tempPos[1])

                    currPos = (round(self.currx), round(self.curry))
                    #print("position in walk is:")
                    #print(currPos)
                    if currPos != path[0]:
                        self.walk()
                    else:
                        compass = self.measures.compass
                        
                        if compass <= 45 and compass >= -45:
                            if x1 <= path_threshold1[0] and x1 >= path_threshold2[0]:
                                self.calcPos(self.previous_l,self.previous_r)
                                state='goTo'
                            else:
                                self.walk() 

                        elif compass <= 135 and compass > 45:
                            if y2 <= path_threshold1[1] and y2 >= path_threshold2[1]:
                                self.calcPos(self.previous_l,self.previous_r)
                                state='goTo'
                            else:
                                self.walk() 

                        elif compass < -135 or compass > 135:
                            if x1 <= path_threshold1[0] and x1 >= path_threshold2[0]:
                                self.calcPos(self.previous_l,self.previous_r)
                                state='goTo'
                            else:
                                self.walk() 

                        elif compass >= -135 and compass < -45:
                            if y2 <= path_threshold1[1] and y2 >= path_threshold2[1]:
                                self.calcPos(self.previous_l,self.previous_r)
                                state='goTo'
                            else:
                                self.walk() 
                                
                        else:
                            self.calcPos(self.previous_l,self.previous_r)
                            state='goTo'
                elif state=='search_path':

                    ##print("Visited cells: ")
                    ##print(self.visitadas)
                    ##print("\nParedes: ")
                    ##print(self.paredes)
                    #print("ENTERING STATE search_path")

                    pos = (0,0)
                    fullPath = [(0, 0)]
                    beac = []
                    temp = list(self.beacons)
                    for (i,j) in temp:
                        beac.append(i)

                    start = pos
                    if pos in beac:
                        beac.remove(pos)

                    ##print(beac)

                    for b in beac:

                        ##print("\nStart")
                        ##print(start)
                        
                        g = b#self.nearestBeacon(start, beac)

                        p = MazeDomain(start, self.visitadas, self.paredes, g, set())
                        s = State(start)
                        problema = SearchProblem(p,s,g)
                        tree = SearchTree(problema)

                        ##print("Finish")
                        ##print(g)

                        path = tree.search()
                        ##print("Solution: ")
                        ##print(path)
                        #beac.remove(g)

                        fullPath.extend(path[1:])
                        start = g

                    g = pos

                    p = MazeDomain(pos, self.visitadas, self.paredes, g, set())
                    s = State(start)
                    problema = SearchProblem(p,s,g)
                    tree = SearchTree(problema)
    
                    ##print("\nStart")
                    ##print(start)
                    ##print("Finish")
                    ##print(g)

                    path = tree.search()
                    ##print("Solution: ")
                    ##print(path)

                    fullPath.extend(path[1:])
                    
                    ##print("Full path: ")
                    ##print(fullPath)

                    state = 'goTo'

                    self.path_to_file(fullPath)
                    self.finish()

                    ##print("END")
                    f =True

            else:
                #print('Stop! \n Lets start A*\n')
                self.drawMap()

                ##print("Visited cells: ")
                ##print(self.visitadas)
                ##print("\nParedes: ")
                ##print(self.paredes)
                ##print("\nLivres: ")
                ##print(self.livres)
                
                #pos = (math.trunc(self.measures.x),math.trunc(self.measures.y))
                #pos = (pos[0]-math.trunc(self.initialPos[0]),pos[1]-math.trunc(self.initialPos[1]))

                pos = (round(self.currx), round(self.curry))

                g = self.searchFreeCell(pos)
                p = MazeDomain(pos, self.visitadas, self.paredes, g, self.livres)
                s = State(pos)
                problema = SearchProblem(p,s,g)
                tree = SearchTree(problema)

                ##print("\nStart")
                ##print(pos)
                ##print("Finish")
                ##print(g)

                path = tree.search()
                ##print("Solution: ")
                ##print(path)
                
                state = 'goTo'
                ##print("END")
                f =True

    
    # Função que procura uma celula livre nao visitada
    def searchFreeCell(self,pos):
        ##print("Searching for free cell")
        best = (10000,(0,0))

        self.livres.difference_update(self.visitadas)

        ##print("\nLivres: ")
        ##print(self.livres)

        for p in self.livres:
            dist = math.sqrt(math.pow((p[0]-pos[0]),2) + math.pow((p[1]-pos[1]),2))
            if dist < best[0]:
                best = (dist, p)
        ##print("Best: " + str(best))
        self.visitadas.add(best[1])
        
        if self.livres:
            self.livres.remove(best[1])
        else:
            self.finishing = True

            self.drawMap()
            self.final_path()
        
            #print("No more free cells, returning home.")

            return (0,0)

        return best[1]

    def nearestBeacon(self, pos, beac):
        ##print("Searching nearest Beacon!")

        best = (10000,(0,0))

        for p in beac:
            dist = math.sqrt(math.pow((p[0]-pos[0]),2) + math.pow((p[1]-pos[1]),2))
            if dist < best[0]:
                best = (dist, p)

        ##print("Best beacon: " + str(best))
        
        return best[1]



    def goTo(self,pos1,pos2):

        pos1Abs = (abs(pos1[0]),abs(pos1[1]))
        pos2Abs = (abs(pos2[0]),abs(pos2[1]))

        
        if pos1Abs[1] - pos2Abs[1] == 0: #mesma linha
            if pos1[0] < pos2[0]: # mov para a direita
                
                ##print("direita")
                return 'rotRight'
            else: #mov para a esquerda
                
                ##print("esquerda")
                return 'rotLeft'

        elif pos1Abs[0] - pos2Abs[0] == 0: #mesma coluna
            if pos1[1] > pos2[1]: # mov para baixo
                
                ##print("baixo")
                return 'rotDown'

            else: #mov para cima
                
                ##print("cima")
                return 'rotUp'
            

    def checkNearby(self,x,y,compass):

        center_id = 0
        left_id = 1
        right_id = 2
        back_id = 3
        
        #print("sensor measures")
        #print(self.measures.irSensor[center_id])
        #print(self.measures.irSensor[left_id])
        #print(self.measures.irSensor[right_id])

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
            ##print("\nFree cell in front of sensor left\n")
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
            ##print("\nFree cell in front of sensor right\n")
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
            ##print("\nFree cell in front of sensor back\n")
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
        l = 0.0
        r = 0.0
        

        
        if compass <= 45 and compass >= -45:
            angleGoal = 0
        elif compass <= 135 and compass > 45:
            angleGoal = 90
        elif compass < -135 or compass > 135:
            angleGoal = 180
        elif compass >= -135 and compass < -45:
            angleGoal = -90
        
        if angleGoal == 180:
            if (compass > -175 and compass <= 0) or (compass < 175 and compass > 0):
                (l,r) = self.rotation(180)
            else: 
                if self.measures.irSensor[left_id] > 2:
                    l = 0.15
                    r = 0.14
                    #self.driveMotors(0.15, 0.14)
                elif self.measures.irSensor[right_id] > 2:
                    l = 0.14
                    r = 0.15
                    #self.driveMotors(0.14,0.15)
                else:
                    l = r = 0.15
                    #self.driveMotors(0.15,0.15)
        else:
            if compass > angleGoal + 5 or compass < angleGoal - 5:
                (l,r) = self.rotation(angleGoal)
            else: 
                if self.measures.irSensor[left_id] > 2:
                    l = 0.15
                    r = 0.14
                    #self.driveMotors(0.15, 0.14)
                elif self.measures.irSensor[right_id] > 2:
                    l = 0.14
                    r = 0.15
                    #self.driveMotors(0.14,0.15)
                else:
                    l = 0.15
                    r = 0.15
                    #self.driveMotors(0.15,0.15)

        
        self.driveMotors(l,r)

        self.calcPos(l,r)

        




    def calcPos(self, l, r):

        outl = (l + self.outsl)/2 
        outr = (r + self.outsr)/2 
        """
        #print("OUTL: ")
        #print(outl)

        #print("OUTR: ")
        #print(outr)
        """

        self.outsl = outl
        self.outsr = outr


        lin = (outl + outr)/2
        ##print("lin")
        ##print(lin)
        previous_t = self.teta

        x = self.xt + lin * math.cos(math.radians(self.measures.compass))
        y = self.yt + lin * math.sin(math.radians(self.measures.compass))

        ##print("X-> ")
        ##print(x)
        ##print("Y-> ")
        ##print(y)

        self.xt = x
        self.yt = y

        rot = (outr - outl)

        t = previous_t + rot

        self.teta = t

        #print("##############################################################\n")

        x2 = self.measures.x
        y2 = self.measures.y
        

        #print("Motor strength: "+ str((l,r)))
        #print("New pos: " + str((x,y,t)))
        #print("Current pos: " + str((x2-round(self.fpx),y2-round(self.fpy),self.measures.compass)))
        #print("GPS pos: " + str((x2-self.testing[0],y2-self.testing[1],self.measures.compass)))

        #dfx = (x2-self.initialPos[0])
        #dfy = (y2-self.initialPos[1])

        # plot values
        #self.diffx.append(dfx)
        #self.diffy.append(dfy)

        #self.allCalcx.append(x)
        #self.allCalcy.append(y)

        #self.allRx.append(x2-self.fpx)
        #self.allRy.append(y2-self.fpy)

        #print("\n##############################################################")


        self.currx = x
        self.curry = y

        self.previous_l = l
        self.previous_r = r


    def correctPos(self):
        center_id = 0
        left_id = 1
        right_id = 2
        back_id = 3
        compass = self.measures.compass

        #print("Correcting in pos: " + str((self.currx, self.curry)))
        
        
        if self.measures.irSensor[center_id] > 1.1:

            temp_currx = round(self.currx)
            temp_curry = round(self.curry)

            if compass <= 30 and compass >= -30:
                if temp_currx % 2 == 0 : 
                    xw = temp_currx + 1
                
                #print("Wall is at: ")
                #print(xw)
                    correctedX = xw - 0.1 - 1/self.measures.irSensor[center_id] - 0.5
                    self.currx = correctedX
                    self.xt = correctedX

                #print("Corrected x: ")
                #print(correctedX)


                if self.measures.irSensor[left_id] > 1.1:
                    if temp_currx % 2 == 0 : 
                        yw = temp_curry + 1

                        correctedY = yw - 0.1 - 1/self.measures.irSensor[left_id] - 0.5
                        self.curry = correctedY
                        self.yt = correctedY
                    #yw = temp_curry + 1
                    

                    #print("(Left) Corrected y: ")
                    #print(correctedY)

                elif self.measures.irSensor[right_id] > 1.1:
                    if temp_currx % 2 == 0 : 
                        yw = temp_curry - 1

                        correctedY = yw + 0.1 + 1/self.measures.irSensor[right_id] + 0.5
                        self.curry = correctedY
                        self.yt = correctedY
                    #yw = temp_curry - 1
                    

                    #print("(Right) Corrected y: ")
                    #print(correctedY)


            elif compass <= 120 and compass >= 60:

                if temp_currx % 2 == 0 : 
                    yw = temp_curry + 1
                

                    correctedY = yw - 0.1 - 1/self.measures.irSensor[center_id] - 0.5
                    self.curry = correctedY
                    self.yt = correctedY

                if self.measures.irSensor[left_id] > 1.1:

                    if temp_currx % 2 == 0 : 
                        xw = temp_currx - 1
                    

                        correctedX = xw + 0.1 + 1/self.measures.irSensor[left_id] + 0.5
                        self.currx = correctedX
                        self.xt = correctedX
                    
                    #print("(Left) Corrected x: ")
                    #print(correctedX)
                elif self.measures.irSensor[right_id] > 1.1:

                    if temp_currx % 2 == 0 : 
                        xw = temp_currx + 1
                    
                        
                        correctedX = xw - 0.1 - 1/self.measures.irSensor[right_id] - 0.5
                        self.currx = correctedX
                        self.xt = correctedX

                    #print("(Right) Corrected x: ")
                    #print(correctedX)

                

                #print("Corrected y: ")
                #print(correctedY)

                
            elif compass <= -120 or compass >= 120:

                if temp_currx % 2 == 0 : 
                    xw = temp_currx - 1
                

                    correctedX = xw + 0.1 + 1/self.measures.irSensor[center_id] + 0.5
                    self.currx = correctedX
                    self.xt = correctedX

                #print("Corrected x: ")
                #print(correctedX)

                if self.measures.irSensor[left_id] > 1.1:

                    if temp_currx % 2 == 0 : 
                        yw = temp_curry - 1
                    

                        correctedY = yw + 0.1 + 1/self.measures.irSensor[left_id] + 0.5
                        self.curry = correctedY
                        self.yt = correctedY

                    #print("(Left) Corrected y: ")
                    #print(correctedY)

                elif self.measures.irSensor[right_id] > 1.1:

                    if temp_currx % 2 == 0 : 
                        yw = temp_curry + 1
                    

                        correctedY = yw - 0.1 - 1/self.measures.irSensor[right_id] - 0.5
                        self.curry = correctedY
                        self.yt = correctedY

                    #print("(Right) Corrected y: ")
                    #print(correctedY)
                    
            elif compass <= -60 and compass >= -120:
                if temp_currx % 2 == 0 : 
                    yw = temp_curry - 1
                

                    correctedY = yw + 0.1 + 1/self.measures.irSensor[center_id] + 0.5
                    self.curry = correctedY
                    self.yt = correctedY

                if self.measures.irSensor[left_id] > 1.1:

                    if temp_currx % 2 == 0 : 
                        xw = temp_currx + 1
                    

                        correctedX = xw - 0.1 - 1/self.measures.irSensor[left_id] - 0.5
                        self.currx = correctedX
                        self.xt = correctedX
                    
                    #print("(Left) Corrected x: ")
                    #print(correctedX)
                elif self.measures.irSensor[right_id] > 1.1:

                    if temp_currx % 2 == 0 : 
                        xw = temp_currx - 1
                    
                        
                        correctedX = xw + 0.1 + 1/self.measures.irSensor[right_id] + 0.5
                        self.currx = correctedX
                        self.xt = correctedX

                    #print("(Right) Corrected x: ")
                    #print(correctedX)

                #print("Corrected y: ")
                #print(correctedY)

        #xw = 1 + 2 * self.currx

        




    def wander(self):
        center_id = 0

        #print("In state wander")
        """
        x1 = self.measures.x
        y2 = self.measures.y
        
        #print(x1, y2)
        #print(self.initialPos)

        x = math.trunc(x1)
        y = math.trunc(y2)

        pos = (x,y)
        posM = (round(x1-self.initialPos[0]),round(y2-self.initialPos[1]))
        #(pos[0]-math.trunc(self.initialPos[0]),pos[1]-math.trunc(self.initialPos[1]))
        
        threshold = 0.8
        posM_threshold1 = (abs(posM[0]) + threshold, abs(posM[1]) + threshold)
        posM_threshold2 = (abs(posM[0]) - threshold, abs(posM[1]) - threshold)
        """

        x1 = self.currx
        y2 = self.curry
        
        #print(x1, y2)
        #print(self.initialPos)

        #print("wander x: " + str(x1) + "\nwander y: " + str(y2))

        x = round(x1)
        y = round(y2)

        pos = (x,y)
        posM = (round(x1-self.initialPos[0]),round(y2-self.initialPos[1]))
        #(pos[0]-math.trunc(self.initialPos[0]),pos[1]-math.trunc(self.initialPos[1]))
        
        threshold = 0.7
        posM_threshold1 = (abs(posM[0]) + threshold, abs(posM[1]) + threshold)
        posM_threshold2 = (abs(posM[0]) - threshold, abs(posM[1]) - threshold)

        ##print(posM_threshold)
        ##print(self.measures.x)
        ##print(self.measures.y)
        #print("ADDING TO VISITED:")
        #print(posM)
        #print("Finished adding")
        self.visitadas.add((round(posM[0]),round(posM[1])))
        ##print(self.livres)
        ##print(self.paredes)

        x1 = abs(posM[0])
        y2 = abs(posM[1])

        compass = self.measures.compass
        
        if posM[0] % 2 == 0 and posM[1] % 2 == 0:
            #print("checking threshold x")
            #print(x1)
            #print(posM_threshold1[0])
            #print(posM_threshold2[0])
            if x1 <= posM_threshold1[0] and x1 >= posM_threshold2[0]:
                #print("checking threshold y")
                #print(y2)
                #print(posM_threshold1[1])
                #print(posM_threshold2[1])
                if y2 <= posM_threshold1[1] and y2 >= posM_threshold2[1]:
                    
                    if self.measures.ground != -1:
                        ##print("adding beacon")
                        self.beacons.add((posM, self.measures.ground))

                        if int(self.nBeacons) == len(self.beacons):
                            ##print("\nParedes:" + str(self.paredes) + '\n')

                            #self.correctPos()


                            return (False, False)
                    #print("checking nearby")
                    self.checkNearby(round(posM[0]),round(posM[1]),compass)
                    
                    if self.measures.irSensor[center_id] <= 1.5:
                        self.walk()
                        return (True, False)
                    else:
                
                        self.driveMotors(0, 0)
                        self.calcPos(0,0)

                        self.correctPos()

                        #print("\nParedes:" + str(self.paredes) + '\n')

                        return (False, False)
                    
                else:
                    if self.measures.irSensor[center_id] > 1.5:
                        #self.checkNearby(posM[0],posM[1],compass)
                        ##print("\nParedes:" + str(self.paredes) + '\n')
                        #self.correctPos()

                        self.driveMotors(0,0)
                        self.calcPos(0,0)
                        self.correctPos()

                        return (False, False)
                    self.walk()
                    
                    return (True, False)
                

            else:
                if self.measures.irSensor[center_id] > 1.5:
                    #self.checkNearby(posM[0],posM[1],compass)

                    ##print("\nParedes:" + str(self.paredes) + '\n')
                    #self.correctPos()

                    self.driveMotors(0,0)
                    self.calcPos(0,0)
                    #self.correctPos()

                    return (False, False)
                self.walk()

                return (True, False)
            
        else:
            if self.measures.irSensor[center_id] > 1.6:
                #self.checkNearby(posM[0],pos[1],compass)

                ##print("\nParedes:" + str(self.paredes) + '\n')
                #self.correctPos()


                self.driveMotors(0,0)
                self.calcPos(0,0)
                #self.correctPos()

                return (False, False)
            self.walk()
            return (True, False)



    def rotation(self, angleGoal):
        compass = self.measures.compass
        l = r = 0.0
        motor_speed = 0.10

        if angleGoal == 180:
            diff = angleGoal - abs(compass)
        else:
            diff = angleGoal - compass
                
        if abs(diff) < 15:
            motor_speed = 0.01

        if angleGoal == 0:
            if compass > 0 and compass <= 180:
                #self.driveMotors(motor_speed,-motor_speed)
                l = motor_speed
                r = -motor_speed
            elif compass < 0 and compass >= -180:
                #self.driveMotors(-motor_speed,motor_speed)
                l = -motor_speed
                r = motor_speed
        elif angleGoal == 90:
            if (compass > 90 and compass <= 180) or (compass <= -90 and compass >=-180):
                #self.driveMotors(motor_speed,-motor_speed)
                l = motor_speed
                r = -motor_speed
            elif compass < 90 and compass > -90:
                #self.driveMotors(-motor_speed,motor_speed)
                l = -motor_speed
                r = motor_speed
        elif angleGoal == 180:
            if compass >= 0 and compass < 180:
                #self.driveMotors(-motor_speed,motor_speed)
                l = -motor_speed
                r = motor_speed
            elif compass < 0 and compass > -180:
                #self.driveMotors(motor_speed,-motor_speed)
                l = motor_speed
                r = -motor_speed
        elif angleGoal == -90:
            if (compass >= 90 and compass <= 180) or (compass < -90 and compass >=-180):
                #self.driveMotors(-motor_speed,motor_speed)
                l = -motor_speed
                r = motor_speed
            elif compass < 90 and compass > -90:
                #self.driveMotors(motor_speed,-motor_speed)
                l = motor_speed
                r = -motor_speed


        return (l,r)


    

    def path_to_file(self, path):
        #print("FINAL PATH TO FILE")
        flag = False

        tempfile = outfile + '.path'

        with open(tempfile, 'w') as f:
            for i in path:
                if i[0] % 2 == 0 and i[1] % 2 == 0:
                    ##print(i)
                    for s in self.beacons:
                        if s[0] == i and s[1] != 0:
                            f.write(str(i[0]) + " " + str(i[1])  + " #" + str(s[1])  + '\n')
                            flag = True
                    if not flag:
                        f.write(str(i[0]) + " " + str(i[1]) + '\n')
                    else:
                        flag = False
            f.close()
        
    def final_path(self):
        ##print("Visited cells: ")
        ##print(self.visitadas)
        ##print("\nParedes: ")
        ##print(self.paredes)
        #print("FINAL PATH")

        pos = (0,0)
        fullPath = [(0, 0)]
        beac = []
        temp = list(self.beacons)
        for (i,j) in temp:
            beac.append(i)

        start = pos
        if pos in beac:
            beac.remove(pos)

        ##print(beac)

        for b in beac:

            ##print("\nStart")
            ##print(start)

            g = b
            #self.nearestBeacon(start, beac)
            p = MazeDomain(start, self.visitadas, self.paredes, g, set())
            s = State(start)
            problema = SearchProblem(p,s,g)
            tree = SearchTree(problema)

            ##print("Finish")
            ##print(g)

            path = tree.search()
            ##print("Solution: ")
            ##print(path)
            #beac.remove(g)

            fullPath.extend(path[1:])
            start = g

        g = pos

        p = MazeDomain(pos, self.visitadas, self.paredes, g, set())
        s = State(start)
        problema = SearchProblem(p,s,g)
        tree = SearchTree(problema)

        ##print("\nStart")
        ##print(start)
        ##print("Finish")
        ##print(g)

        path = tree.search()
        ##print("Solution: ")
        ##print(path)

        fullPath.extend(path[1:])
        
        ##print("Full path: ")
        ##print(fullPath)

        state = 'goTo'

        self.path_to_file(fullPath)
        

        ##print("END")

    def drawMap(self):
        for i in self.livres:
            self.mapArray[13 - i[1]][27 + i[0]] = 'O'

        for i in self.visitadas:
            self.mapArray[13 - i[1]][27 + i[0]] = 'X'

        for i in self.beacons:
            self.mapArray[13 - i[0][1]][27 + i[0][0]] = str(i[1])
        
        for i in self.paredes:

            if i[1] % 2 == 0:
                if i[0] % 2 != 0:
                    self.mapArray[13 - i[1]][27 + i[0]] = '|'
            else:
                if i[0] % 2 == 0:
                    self.mapArray[13 - i[1]][27 + i[0]] = '-'

        self.mapArray[13][27] = '0'

        tempfile = outfile + '.map'
        with open(tempfile, 'w') as f:
            for i in range(27):
                for j in range(55):
                    f.write(self.mapArray[i][j])
                f.write('\n')


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


rob_name = "mainC4"
host = "localhost"
pos = 1
mapc = None
outfile = "challenge4"

for i in range(1, len(sys.argv),2):
    if (sys.argv[i] == "--host" or sys.argv[i] == "-h") and i != len(sys.argv) - 1:
        host = sys.argv[i + 1]
    elif (sys.argv[i] == "--pos" or sys.argv[i] == "-p") and i != len(sys.argv) - 1:
        pos = int(sys.argv[i + 1])
    elif (sys.argv[i] == "--robname" or sys.argv[i] == "-r") and i != len(sys.argv) - 1:
        rob_name = sys.argv[i + 1]
    elif (sys.argv[i] == "--outfile" or sys.argv[i] == "-f") and i != len(sys.argv) - 1:
        outfile = sys.argv[i + 1]
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
    
    try:
        rob.run()
    except Exception as e:
        
        rob.drawMap()
        rob.final_path()
