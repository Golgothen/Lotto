import multiprocessing, psutil
from threading import Thread
from vector import vector
from datetime import datetime
from itertools import combinations
from message import Message

class PipeWatcher(Thread):

    def __init__(self, parent, pipe, name):
        super(PipeWatcher, self).__init__()

        self.__pipe = pipe
        self.__parent = parent
        self.__running = False
        self.name = name
        self.daemon = True

    def run(self):
        self.__running = True
        #print('Pipe pid {}'.format(self.id))
        while self.__running:
            try:
                while self.__pipe.poll(None):  # Block indefinately waiting for a message
                    m = self.__pipe.recv()
                    #print('Pipe {} receiced {}'.format(self.name,m))
                    response = getattr(self.__parent, m.message)(m.params)
                    #self.__parent.updateBest(m)
                    if response is not None:
                        self.send(response)
            except (KeyboardInterrupt, SystemExit):
                self.__running = False
                continue
            except:
                continue

    # Public method to allow the parent to send messages to the pipe
    def send(self, m):
        #print('Pipe {} receiced {}'.format(self.name,m))
        self.__pipe.send(m)




class Workforce():
    def __init__(self, inQ, outQ, blockSize, game):

        self.workers = []
        self.pipes = []
        for i in range(self.workforceSize):
            r, s = multiprocessing.Pipe()
            self.pipes.append(PipeWatcher(self, r, 'Hub{}'.format(i)))
            self.workers.append(Cruncher(i, blockSize, game, inQ, outQ, s))
            self.pipes[i].start()
            self.workers[i].start()
            
    def UPDATEBEST(self, m):
        print('Workforce received best weight {} from process {}'.format(m['WEIGHT'], m['PROC_ID']))
        for p in self.pipes:
            #print(p.name)
            #if p.name != 'Hub{}'.format(m['PROC_ID']):
                #print('sending {} on pipe {}'.format(m, p.name))
            p.send(Message('UPDATEBEST', m))
    
    @property
    def workforceSize(self):
        return multiprocessing.cpu_count()

class Cruncher(multiprocessing.Process):
    def __init__(self, id, blockSize, game, jobQ, resultQ, p):
        super(Cruncher,self).__init__()
        self.blockSize = blockSize
        self.game = game
        self.jobQ = jobQ
        self.resultQ = resultQ
        self.bestWeight = 0
        self.id = id
        self.p = p
    
    def run(self):
        self.pipe = PipeWatcher(self, self.p, 'Pipe{}'.format(self.id))
        self.pipe.start()
        p = psutil.Process()
        p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        while True:
            c = 0
            t = datetime.now()
            prefix = self.jobQ.get()
            if prefix is None:
                return None
            #self.resultQ.put(Message('M', self.workerCount, 'Starting block {}'.format(prefix)))
            for i in combinations(range(max(list(prefix))+1,self.game.poolSize+1),self.blockSize):
                r = {}
                r['Numbers'] = set(prefix + i)
                #print(r['Numbers'])
                r['Divisions'], r['Weight'] = self.game.play(r['Numbers'])
                c+=self.game.len
                if r['Weight'] > self.bestWeight:
                    self.bestWeight = r['Weight']
                    self.pipe.send(Message('UPDATEBEST', PROC_ID = self.id, WEIGHT = self.bestWeight))
                    self.resultQ.put(Message('RESULT', PROC_ID = self.id, NUMBERS = r['Numbers'], DIVISIONS = r['Divisions'], WEIGHT = r['Weight']))
                    #print(self.resultQ.qsize())
            e = datetime.now() - t
            s = e.seconds + (e.microseconds / 1000000)
            if s  > 0:
                self.resultQ.put(Message('STATUS', PROC_ID = self.id, MESSAGE = 'Completed {:15,.0f} combinations in {:8,.2f} seconds. {:9,.0f} combinations per second. Block {}'.format(c, s, c/s, prefix)))
    
    def UPDATEBEST(self, m):
        print('Process {} received weight of {} from process'.format(self.id, m['WEIGHT'], m['PROC_ID']))
        if m['WEIGHT'] > self.bestWeight:
            self.bestWeight = weight
            print('Process {} updated best weight to {}'.format(self.id, self.bestWeight))
