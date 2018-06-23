import multiprocessing, psutil, signal
from threading import Thread
#from vector import vector
from datetime import datetime
from itertools import combinations
from message import Message
import traceback, sys

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
        while self.__running:
            try:
                while self.__pipe.poll(None):  # Block indefinately waiting for a message
                    m = self.__pipe.recv()
                    response = getattr(self.__parent, m.message)(m.params)
                    if response is not None:
                        self.send(response)
            except (KeyboardInterrupt, SystemExit):
                self.__running = False
                continue
            except:
                print('*** Exception caught in Pipe thread {} ***'.format(self.name))
                traceback.print_exception(*sys.exc_info())
                continue

    # Public method to allow the parent to send messages to the pipe
    def send(self, m):
        self.__pipe.send(m)

class Workforce():
    def __init__(self, inQ, outQ, blockSize, game):

        self.workers = []
        self.pipes = []
        for i in range(multiprocessing.cpu_count()):
            r, s = multiprocessing.Pipe()
            self.workers.append(Cruncher(i, blockSize, game, inQ, outQ, s))
            self.workers[i].start()
            self.pipes.append(PipeWatcher(self, r, 'Hub{}'.format(i)))
            self.pipes[i].start()
            
    def UPDATEBEST(self, m):
        for p in self.pipes:
            if p.name != 'Hub{}'.format(m['PROC_ID']):
                p.send(Message('UPDATEBEST', WEIGHT = m['WEIGHT'], PROC_ID = m['PROC_ID']))
    
    def halt(self):
        print('Telling worker processes to HALT')
        for p in self.pipes:
            p.send(Message('HALT'))
    
    def stop(self):
        for w in self.workers:
            w.join()

class Cruncher(multiprocessing.Process):
    def __init__(self, proc_id, blockSize, game, jobQ, resultQ, p):
        super(Cruncher,self).__init__()
        self.blockSize = blockSize
        self.game = game
        self.jobQ = jobQ
        self.resultQ = resultQ
        self.bestWeight = 0
        self.id = proc_id
        self.p = p
        self.pipe = None
        self.__running = False
    
    def run(self):
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        self.pipe = PipeWatcher(self, self.p, 'Pipe{}'.format(self.id))
        self.pipe.start()
        p = psutil.Process()
        p.nice(psutil.IDLE_PRIORITY_CLASS)
        self.__running = True
        while self.__running:
            c = 0
            t = datetime.now()
            prefix = self.jobQ.get()
            if prefix is None:
                return None
            #self.resultQ.put(Message('M', self.workerCount, 'Starting block {}'.format(prefix)))
            for i in combinations(range(max(list(prefix))+1,self.game.poolSize+1),self.blockSize):
                numbers = set(prefix + i)
                r = self.game.play(numbers)
                r['Numbers'] = numbers
                c+=self.game.len
                if 'Divisions' in r:
                    if r['Weight'] > self.bestWeight:
                        self.bestWeight = r['Weight']
                        self.pipe.send(Message('UPDATEBEST', PROC_ID = self.id, WEIGHT = self.bestWeight))
                        self.resultQ.put(Message('RESULT', PROC_ID = self.id, NUMBERS = r['Numbers'], DIVISIONS = r['Divisions'], WEIGHT = r['Weight']))
                else:
                    #print(r)
                    for k, v in r.items():
                        if k == 'Numbers': continue
                        #print('k = {}, v = {}'.format(k, v))
                        if v['Weight'] > self.bestWeight:
                            self.bestWeight = v['Weight']
                            self.pipe.send(Message('UPDATEBEST', PROC_ID = self.id, WEIGHT = self.bestWeight))
                            self.resultQ.put(Message('RESULT', PROC_ID = self.id, NUMBERS = r['Numbers'], DIVISIONS = v['Divisions'], WEIGHT = v['Weight'], POWERBALL = k))
                            
                    #print(self.resultQ.qsize())
            e = datetime.now() - t
            s = e.seconds + (e.microseconds / 1000000)
            self.resultQ.put(Message('COMPLETED', PROC_ID = self.id, BLOCK = prefix, ELAPSED = s, COMBINATIONS = c))
    
    def UPDATEBEST(self, m):
        if m['WEIGHT'] > self.bestWeight:
            self.bestWeight = m['WEIGHT']
    
    def HALT(self, m):
        print('Process {} received HALT command.'.format(self.id))
        self.__running = False
