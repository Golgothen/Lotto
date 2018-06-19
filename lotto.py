import csv, operator, os

import multiprocessing
from datetime import datetime
from itertools import combinations
from vector import vector
from sys import stdout
from cruncher import Workforce
from game import *

#from numba import jit

class Ball():
    def __init__(self, v):
        self.value = v
        self.drawnWith = vector(45)
        self.supWith = vector(45)
        self.lastDrawn = datetime(1900,1,1)
        self.streaks = vector(1)
        self.nonStreaks = vector(1)
        self.drawStreaks = vector(1)
        
    #@jit(nonpython=true)
    def draw(self, game):
        if self.value in game.numbers + game.sups:
            if self.nonStreaks[0] != 0:
                self.nonStreaks.insert(0,0)
            self.streaks[0] += 1
            if self.value in game.numbers:
                self.drawStreaks[0] += 1
            if game.drawDate > self.lastDrawn:
                self.lastDrawn = game.drawDate
            for a in game.numbers:
                self.drawnWith[a-1] += 1
            for a in game.sups:
                #self.drawnWith[a-1] += 1
                self.supWith[a-1] += 1
        else:
            if self.streaks[0] != 0:
                self.streaks.insert(0,0)
            if self.drawStreaks[0] != 0:
                self.drawStreaks.insert(0,0)
            self.nonStreaks[0] += 1
    
    @property
    def count(self):
        return self.drawnWith[self.value-1]
    
    @property
    def sup(self):
        return  self.supWith[self.value-1]
    
    @property
    def strikeRate(self):
        return (self.count + self.sup)/(sum(self.streaks)+sum(self.nonStreaks))*100
    
    def __str__(self):
        s =  'Ball {}:\n'.format(self.value)
        s += '  Drawn {} times, Supped {} times, {} in total, strike rate of {:3.3f}%, last drawn on {}\n'.format(self.count,self.sup, self.count + self.sup, self.strikeRate, self.lastDrawn)
        s += '  Current draw streak: {}, Longest draw streak: {}, Average draw streak: {:2.3f}\n'.format(self.drawStreaks[0],max(self.drawStreaks),self.drawStreaks.mean)
        s += '  Current pick streak: {}, Longest pick streak: {}, Average pick streak: {:2.3f}\n'.format(self.streaks[0],max(self.streaks),self.streaks.mean)
        s += '  Current miss streak: {}, Longest miss streak: {}, Average miss streak: {:2.3f}\n'.format(self.nonStreaks[0],max(self.nonStreaks),self.nonStreaks.mean)
        s += '  Top 10 most commonly drawn with - Ball(Count):\n    '
        t = self.drawnWith.sort(True)
        for i in range(1, 11):
            s += '{}({}), '.format(t[i][0]+1, t[i][1])
        s = s[:-2] + '\n'
        s += '  Top 10 most commonly supplemented with - Ball(Count):\n    '
        t = self.supWith.sort(True)
        for i in range(1, 11):
            s += '{}({}), '.format(t[i][0]+1, t[i][1])
        s = s[:-2] + '\n'
        return s

class Field():
    def __init__(self):
        self.balls = {}
        for a in range(1,46):
            self.balls[a] = Ball(a)
    
    def draw(self, game):
        for b in self.balls.values():
            b.draw(game)


                

class Procs():
    def __init__(self, id):
        self.id = id
        self.lastMessage = ''
        self.lastResult = {'Numbers' : vector(7), 'Divisions' : vector(6), 'Weight' : 0}
        self.bestResult = {'Numbers' : vector(7), 'Divisions' : vector(6), 'Weight' : 0}
        
class Results():
    def __init__(self, games, outfile = None):
        self.games = games
        self.block = 4
        self.pick = self.games.minPick
        self.divisionWeights = vector([95000, 750, 100, 3, 2, 1])
        if outfile is None:
            self.outfile = "Results"
        else:
            self.outfile = outfile
    
    def compute(self, picks = None, block = None):
        if picks is not None:
            if picks < self.games.minPick:
                self.pick = self.games.minPicks
            else:
                self.pick = picks
        if block is not None:
            self.block = block
        workQ = multiprocessing.Queue()
        resultQ = multiprocessing.Queue()
        

        for i in combinations(range(1,self.games.poolSize - self.block + 1),self.pick - self.block):
            workQ.put(i)
        for i in range(multiprocessing.cpu_count()):
            workQ.put(None)
        print('Added {:15,.0f} work blocks to the work que'.format(workQ.qsize()))

        wf = Workforce(workQ, resultQ, self.block, self.games)
        #procs = []
        #for i in range(multiprocessing.cpu_count()):
        #    procs.append(Procs(i))
            
        while not workQ.empty():
            m = resultQ.get()
            if m.type == 'M':
                #procs[m.id].lastMessage = m.message
                print('{}. {:9,.0f} blocks left'.format(m.message, workQ.qsize()))
            if m.type == 'R':
                #procs[m.id].lastResult = m.message
                #if procs[m.id].lastResult['Weight'] > procs[m.id].bestResult['Weight']:
                #    procs[m.id].bestResult = procs[m.id].lastResult.copy()
                #print('Numbers = {}, Divisions = {}, Weight = {}'.format(m.message['Numbers'], m.message['Divisions'], m.message['Weight']))
                with open('{} - {}.txt'.format(self.outfile, self.pick),'a') as f:
                    f.write('Numbers = {}, Divisions = {}, Weight = {}.\n'.format(m.message['Numbers'], m.message['Divisions'], m.message['Weight']))
            #updateScreen(procs,workQ.qsize())
                
        #for i in range(multiprocessing.cpu_count()):
        #    crunchers[i].join()

def prep():
    game = OzLotto()
    game.load("ozlotto.csv")
    #game.divisionWeights = vector([1,1,1,1,1,1])
    return game

def paintScreen(procs):
    os.system('cls')
    stdout.write('-- ID --:' + ('-' * 90) + '\n')
    for p in procs:
        stdout.write('  {:2.0f}  : Best - '.format(p.id))
        for n in p.bestResult['Numbers']:
            stdout.write('{:2.0f}, '.format(p.bestResult['Numbers'][n]))
        stdout.write(' : Divisions - ')
        for n in p.bestResult['Divisions']:
            stdout.write('{:3.0f}, '.format(p.bestResult['Divisions'][n]))
        stdout.write('/n')
        stdout.write('      : Last - '.format(p.id))
        for n in p.lastResult['Numbers']:
            stdout.write('{:2.0f}, '.format(p.lastResult['Numbers'][n]))
        stdout.write(' : Divisions - ')
        for n in p.lastResult['Divisions']:
            stdout.write('{:3.0f}, '.format(p.lastResult['Divisions'][n]))
        stdout.write('/n')
        stdout.write('      : Message - {}/n'.format(p.lastMessage))
        stdout.write('--------:' + ('-' * 90) + '\n')


def updateScreen(procs,qsize):
    
    for p in procs:
        
        s = ''
        for j in p.bestResult['Numbers']:
            s += '{:2.0f}, '.format(j)
        printxy(1+(p.id*4),16,s)

        s = ''
        for j in p.bestResult['Divisions']:
            s += '{:3.0f}, '.format(j)
        printxy(2+(p.id*4),31 + (len(p.bestResult['Numbers'])*4),s)

def printxy(x, y, text):
    stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (x, y, text))
    stdout.flush()

def go():
    g = prep()
    r = Results(g, "OzLotto")
    r.compute(7,4)

if __name__ == '__main__':
    go()
    

#    field = Field()
#    for a in range(len(games)-1, -1, -1):   # Itterate the list backward
#        field.draw(games[a])
#    
#    m = []
#    for b, v in field.balls.items():
#        m.append(v.drawnWith)
#    s = '  : '
#    for a in range(45):
#        s += '{:2.0f} '.format(a+1)
#    print(s)
#    for a in range(45):
#
#     s = '{:2.0f}  '.format(a+1)
#        for b in range(45):
#            if a==b:
#                s += '   '
#            else:
#                s += '{:2.0f} '.format(m[a][b])
#        print(s)
#    
#    for g in games:
#        d = g.play((1, 15, 11, 42, 31, 12, 36))
#        if d is not None:
#            print('Game {} paid dividend {}'.format(g.drawDate, d))
    
