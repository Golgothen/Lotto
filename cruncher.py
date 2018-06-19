import multiprocessing, psutil
from threading import Thread
from vector import vector
from datetime import datetime
from itertools import combinations

class Message():
    def __init__(self, type, id, message):
        self.type = type
        self.id = id
        self.message = message

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
                    #print('Pipe {} receiced {}'.format(self.name,m))
                    #response = getattr(self.__parent, m.message.lower())(m.params)
                    self.__parent.updateBest(m)
                    #if response is not None:
                    #    self.send(response)
            except (KeyboardInterrupt, SystemExit):
                self.__running = False
                continue
            except:
                continue

    # Public method to allow the parent to send messages to the pipe
    def send(self, msg):
        self.__pipe.send(msg)




class Workforce():
    def __init__(self, inQ, outQ, poolSize, blockSize, games, divisionWeights = None):

        self.workers = []
        self.pipes = []
        for i in range(multiprocessing.cpu_count()):
            r, s = multiprocessing.Pipe()
            self.pipes.append(PipeWatcher(self, r, 'Hub{}'.format(i)))
            self.workers.append(Cruncher(i, poolSize, blockSize, games, inQ, outQ, s, divisionWeights))
            self.pipes[i].start()
            self.workers[i].start()
            
    def updateBest(self, m):
        #print('Workforce received best weight {} from process {}'.format(m[1], m[0]))
        for i in range(len(self.pipes)):
            if i != m[0]:
                #print('sending {} on pipe {}'.format(m[1],self.pipes[i].name))
                self.pipes[i].send(m[1])
        

class Cruncher(multiprocessing.Process):
    def __init__(self, workerCount, poolSize, blockSize, games, jobQ, resultQ, p, divisionWeights = None):
        super(Cruncher,self).__init__()
        self.poolSize = poolSize
        self.blockSize = blockSize
        self.games = games
        self.jobQ = jobQ
        self.resultQ = resultQ
        self.bestWeight = 0
        self.workerCount = workerCount
        self.pipe = p
        self.weights = vector([95000, 750, 100, 3, 2, 1])
        if divisionWeights is not None:
            self.weights = vector(divisionWeights)
    
    def run(self):
        pw = PipeWatcher(self, self.pipe, 'Pipe{}'.format(self.workerCount))
        pw.start()
        p = psutil.Process()
        p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        print('Cruncher {} starting with divisional weights {}'.format(self.workerCount, self.weights))
        while True:
            c = 0
            t = datetime.now()
            prefix = self.jobQ.get()
            if prefix is None:
                return None
            #self.resultQ.put(Message('M', self.workerCount, 'Starting block {}'.format(prefix)))
            for i in combinations(range(max(list(prefix))+1,self.poolSize+1),self.blockSize):
                r = {}
                r['Numbers'] = set(prefix + i)
                #print(r['Numbers'])
                r['Divisions'] = vector(6)
                r['Process'] = self.workerCount
                for g in self.games:
                    d = g.play(r['Numbers'])
                    c += 1
                    if d is not None:
                         r['Divisions'][d-1] += 1
                r['Weight'] = sum(r['Divisions'] * self.weights)
                #print(r['Weight'])
                if r['Weight'] > self.bestWeight:
                    self.bestWeight = r['Weight']
                    self.pipe.send((self.workerCount,self.bestWeight))
                    self.resultQ.put(Message('R', self.workerCount,r))
                    #print(self.resultQ.qsize())
            e = datetime.now() - t
            s = e.seconds + (e.microseconds / 1000000)
            if s  > 0:
                self.resultQ.put(Message('M',self.workerCount, 'Completed {:10,.0f} combinations in {:8,.4f} seconds. {:7,.0f} combinations per second. Block {}'.format(c, s, c/s, prefix)))
    
    def updateBest(self, weight):
        #print('Process {} received weight of {}'.format(self.workerCount, weight))
        if weight > self.bestWeight:
            self.bestWeight = weight
            #print('Process {} updated best weight to {}'.format(self.workerCount, self.bestWeight))
