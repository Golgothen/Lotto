#import csv, operator, os

#import multiprocessing
#from datetime import datetime
#from itertools import combinations
#from vector import vector
#from sys import stdout
#from cruncher import Workforce
from game import *
from result import Results

#from numba import jit


class Procs():
    def __init__(self, id):
        self.id = id
        self.lastMessage = ''
        self.lastResult = {'Numbers' : vector(7), 'Divisions' : vector(6), 'Weight' : 0}
        self.bestResult = {'Numbers' : vector(7), 'Divisions' : vector(6), 'Weight' : 0}
        
if __name__ == '__main__':
    game = OzLotto()
    game.load("ozlotto.csv")
    #game.divisionWeights = vector([1,1,1,1,1,1])
    r = Results(game, "OzLotto")
    r.compute(7,4)
    





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
    
