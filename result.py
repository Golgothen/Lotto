from vector import vector
from multiprocessing import Queue
from itertools import combinations
from cruncher import Workforce
from game import *
import pickle, os

class Results():
    def __init__(self, args):
        self.workQ = Queue()
        self.resultQ = Queue()
        self.resume = False
        if args.resume:
            self.resume = True
            print('Resuming...')
            f = open('WorkQueue.pkl', 'rb')
            args = pickle.load(f)
            while True:
                try:
                    self.workQ.put(pickle.load(f))
                except (EOFError, pickle.UnpicklingError):
                    break
            f.close()
            os.remove('WorkQueue.pkl')
        if args.game[0].lower() == 'lotto':
            self.game = Lotto()
        if args.game[0].lower() == 'ozlotto':
            self.game = OzLotto()
        if args.game[0].lower() == 'powerball':
            self.game = PowerBall()
        if args.game[0].lower() == 'uspowerball':
            self.game = USPowerBall()
        if args.game[0].lower() == 'megamillions':
            self.game = MegaMillions()
        
        if args.file[0] == '.csv':
            args.file[0] = args.game[0] + args.file[0]
        self.game.load(args.file[0])

        if args.block[0] < 3:
            args.block[0] = 3
        
        if args.block[0] > self.game.minPick + 1:
            args.block[0] = self.game.minPick - 1
        self.block = args.block[0]

        if args.pick[0] < self.game.minPick:
            args.pick[0] = self.game.minPick
        self.pick = args.pick[0]
        
        #self.divisionWeights = vector([95000, 750, 100, 3, 2, 1])
        self.outfile = "Results"
        self.args = args
    
    def compute(self):
        if not self.resume:
            for i in combinations(range(1,self.game.poolSize - self.block + 1),self.pick - self.block):
                self.workQ.put(i)
            print('Added {:15,.0f} work blocks to the work que'.format(self.workQ.qsize()))

        wf = Workforce(self.workQ, self.resultQ, self.block, self.game)

        for i in range(wf.workforceSize):
            self.workQ.put(None)
        
        try:
            while not self.workQ.empty():
                self.processMessage(self.resultQ.get())
                
        except (KeyboardInterrupt, SystemExit):
            # Dump the queue to file
            wf.halt()
            with open("WorkQueue.pkl", 'wb') as f:
                pickle.dump(self.args, f)
                while not self.workQ.empty():
                    pickle.dump(self.workQ.get(), f)
            wf.stop()
            while not self.resultQ.empty():
                self.processMessage(self.resultQ.get())
                
            #updateScreen(procs,workQ.qsize())
                
        #for i in range(multiprocessing.cpu_count()):
        #    crunchers[i].join()
    def processMessage(self, m):
        if m.message == 'STATUS':
            #procs[m.id].lastMessage = m.message
            print('{}. {:9,.0f} blocks left'.format(m.params['MESSAGE'], self.workQ.qsize()))
        if m.message == 'RESULT':
            #procs[m.id].lastResult = m.message
            #if procs[m.id].lastResult['Weight'] > procs[m.id].bestResult['Weight']:
            #    procs[m.id].bestResult = procs[m.id].lastResult.copy()
            #print('Numbers = {}, Divisions = {}, Weight = {}'.format(m.message['Numbers'], m.message['Divisions'], m.message['Weight']))
            with open('{}-{}.txt'.format(self.outfile, self.pick),'a') as f:
                f.write('Numbers = {}, Divisions = {}, Weight = {}.\n'.format(m.params['NUMBERS'], m.params['DIVISIONS'], m.params['WEIGHT']))

