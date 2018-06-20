from vector import vector
from multiprocessing import Queue
from itertools import combinations
from cruncher import Workforce

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
                self.pick = self.games.minPick
            else:
                self.pick = picks
        else:
            self.pick = self.games.minPicks
            
        if block is not None:
            self.block = block
        workQ = Queue()
        resultQ = Queue()

        for i in combinations(range(1,self.games.poolSize - self.block + 1),self.pick - self.block):
            workQ.put(i)

        wf = Workforce(workQ, resultQ, self.block, self.games)

        for i in range(wf.workforceSize):
            workQ.put(None)
        
        print('Added {:15,.0f} work blocks to the work que'.format(workQ.qsize()))

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
                with open('{}-{}.txt'.format(self.outfile, self.pick),'a') as f:
                    f.write('Numbers = {}, Divisions = {}, Weight = {}.\n'.format(m.message['Numbers'], m.message['Divisions'], m.message['Weight']))
            #updateScreen(procs,workQ.qsize())
                
        #for i in range(multiprocessing.cpu_count()):
        #    crunchers[i].join()


