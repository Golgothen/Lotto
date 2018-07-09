import multiprocessing, psutil, signal, os, pickle
from threading import Thread
#from vector import vector
#from datetime import datetime
from itertools import combinations
from message import Message
#import traceback, sys
from game import *
from connection import Connection
from mplogger import *
from time import sleep

QUEUE_SIZE_MULTIPLIER = 10

class PipeWatcher(Thread):

    def __init__(self, config, parent, pipe, name):
        super(PipeWatcher, self).__init__()

        self.__pipe = pipe
        self.__parent = parent
        self.__running = False
        self.name = name
        self.daemon = True
        self.config = config

    def run(self):
        logging.config.dictConfig(self.config)
        self.logger = logging.getLogger('pipewatcher')
        self.__running = True
        while self.__running:
            try:
                while self.__pipe.poll(None):  # Block indefinately waiting for a message
                    m = self.__pipe.recv()
                    self.logger.debug(m)
                    response = getattr(self.__parent, m.message)(m.params)
                    if response is not None:
                        self.send(response)
            except (KeyboardInterrupt, SystemExit):
                self.__running = False
                continue
            except BrokenPipeError:
                return
            except:
                self.logger.error('Exception caught in Pipe thread {}'.format(self.name), exc_info = True)#, stack_info = True)
                #traceback.print_exception(*sys.exc_info())
                continue

    # Public method to allow the parent to send messages to the pipe
    def send(self, m):
        self.__pipe.send(m)


class Workforce():
    def __init__(self, host, port, config):
        self.games = {}
        self.workers = []
        self.pipes = []
        self.con = Connection(config = config, host = host, port = port)
        self.connectionBusy = False
        self.stopQueue = False
        logging.config.dictConfig(config)
        self.logger = logging.getLogger('workforce')
        self.workQ = multiprocessing.Queue()
        success = False
        if os.path.isfile('cruncher.dat'):
            with open('cruncher.dat','rb') as f:
                self.games = pickle.load(f)
                while True:
                    try:
                        self.workQ.put(pickle.load(f))
                    except (EOFError):
                        success = True
                        break
        if success:
            os.remove('cruncher.dat')

        for i in range(self.crunchers):
            r, s = multiprocessing.Pipe()
            self.workers.append(Cruncher(i, self.workQ, s, config))
            self.workers[i].start()
            self.pipes.append(PipeWatcher(config, self, r, 'Hub{}'.format(i)))
            self.pipes[i].start()
            
    def RESULT(self, m):
        for p in self.pipes:
            if p.name != 'Hub{}'.format(m['PROC_ID']):
                p.send(Message('RESULT', **m))
        while self.connectionBusy:
            sleep(0.1)
        self.connectionBusy = True
        try:
            message = Message('RESULT', **m)
            self.con.send(message)
            self.con.close()
        except:
            with open('messages.dat','ab') as f:
                pickle.dump(message, f)
        self.connectionBusy = False

    def COMPLETE(self, m):
        while self.connectionBusy:
            sleep(0.1)
        self.logger.info('=========>>>{}'.format(m['BLOCK']))
        message = Message('COMPLETE', **m)
        self.connectionBusy = True
        try:
            self.con.send(message)
            self.con.close()
        except:
            self.logger.error('Exception in COMPLETE', exc_info = True)
            with open('messages.dat','ab') as f:
                pickle.dump(message, f)
            self.logger.info('=========^^^{}'.format(m['BLOCK']))
        self.connectionBusy = False
    
    def GETGAME(self, m):
        while self.connectionBusy:
            sleep(0.1)
        if m['GAMEID'] not in self.games:
            self.connectionBusy = True
            #self.con.connect(self.host, self.port)
            self.con.send(Message('GET_DATA', GAMEID = m['GAMEID']))
            self.games[m['GAMEID']] = self.con.recv().params['GAME']
            self.con.close()
            self.connectionBusy = False
            self.logger.debug('Loaded new game data for {}'.format(m['GAMEID']))
        else:
            self.logger.debug('Loaded game data from cache')
        self.pipes[m['PROC_ID']].send(Message('GAME_DATA', GAME = self.games[m['GAMEID']]))
    
    def halt(self):
        self.stopQueue = True
        for p in self.pipes:
            p.send(Message('HALT'))
        if self.workQ.qsize() > 0:
            with open('cruncher.dat', 'wb') as f:
                pickle.dump(self.games, f)
                while not self.workQ.empty():
                    pickle.dump(self.workQ.get(), f)
    
    def stop(self):
        for w in self.workers:
            w.join()
    
    def abort(self):
        for i in range(self.crunchers):
            self.workQ.put(None)
    
    @property
    def crunchers(self):
        return multiprocessing.cpu_count()
    
    @property
    def workQueueLimit(self):
        return self.crunchers * QUEUE_SIZE_MULTIPLIER
    
    @property
    def workAvailable(self):
        self.logger.info(self.workQ.qsize())
        if self.workQ.qsize() > 0:
            return True
        return False
    
    def fillQueue(self):
        if not self.stopQueue:
            success = False
            if self.workQ.qsize() < self.workQueueLimit:
                for i in range(self.workQueueLimit - self.workQ.qsize()):
                    try:
                        if self.connectionBusy:
                            sleep(0.1)
                        self.connectionBusy = True
                        self.con.send(Message('GET_BLOCK'))
                        try:
                            b = self.con.recv()
                        except:
                            continue
                        self.logger.info('<<<========={}'.format(b.params['BLOCK']))
                        self.workQ.put(b)
                        success = True
                        self.con.close()
                    except (ConnectionResetError, ConnectionRefusedError, TimeoutError, OSError):
                        raise
                    except(pickle.UnpicklingError, KeyError):
                        # Disregard corrupted messages
                        continue
                self.connectionBusy = False
                self.con.close()
                if success:
                    success = False
                    if os.path.isfile('messages.dat'):
                        with open('messages.dat','rb') as f:
                            while True:
                                try:
                                    if self.connectionBusy:
                                        sleep(0.1)
                                    self.connectionBusy = True
                                    self.con.send(pickle.load(f))
                                    self.con.close()
                                    self.connectionBusy = False
                                except (EOFError):
                                    success = True
                                    break
                        if success:
                            os.remove('messages.dat')
                            
                            
    
        

class Cruncher(multiprocessing.Process):
    def __init__(self, proc_id, jobQ, p, config):
        super(Cruncher,self).__init__()
        self.game = None
        self.jobQ = jobQ
        #self.resultQ = resultQ
        self.id = proc_id
        self.p = p
        self.pipe = None
        self.__running = False
        self.wait = multiprocessing.Event()
        self.config = config
        self.best = None
        self.most = None
        self.gameID = None
    
    def run(self):
        logging.config.dictConfig(self.config)
        self.logger = logging.getLogger('cruncher')
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        self.pipe = PipeWatcher(self.config, self, self.p, 'Pipe{}'.format(self.id))
        self.pipe.start()
        p = psutil.Process()
        p.nice(psutil.IDLE_PRIORITY_CLASS)
        self.__running = True
        while self.__running:
            c = 0
            t = datetime.now()
            block = self.jobQ.get()
            if block is None:
                return None
            prefix = block.params['BLOCK']
            self.pick = block.params['PICK']
            blockSize = self.pick - len(prefix)
            self.gameID = block.params['GAME']
            if self.gameID != type(self.game).__name__:
                self.pipe.send(Message('GETGAME', GAMEID = '{}{}'.format(self.gameID, self.pick), PROC_ID = self.id))
                self.wait.wait()
                self.wait.clear()
            self.best = block.params['BEST']
            self.most = block.params['MOST']
            self.logger.debug('Starting block {}'.format(prefix))
            for i in combinations(range(max(list(prefix))+1,self.game.poolSize+1),blockSize):
                numbers = set(prefix + i)
                r = self.game.play(numbers)
                c += self.game.len
                if r*self.game.divisionWeights > self.best:
                    self.best = r*self.game.divisionWeights
                    #self.pipe.send(Message('BROADCAST', PROC_ID = self.id, STAT_TYPE = 'BESTWEIGHT', VALUE = self.best, GAMEID = self.gameID, PICK = self.pick))
                    self.pipe.send(Message('RESULT', PROC_ID = self.id, RESULT_TYPE = 'BEST', RESULT = self.best, GAMEID = self.gameID, PICK = self.pick))
                if r > self.most:
                    self.most = r
                    #self.pipe.send(Message('BROADCAST', PROC_ID = self.id, STAT_TYPE = 'MOSTWON', VALUE = self.most, GAMEID = self.gameID, PICK = self.pick))
                    self.pipe.send(Message('RESULT', PROC_ID = self.id, RESULT_TYPE = 'MOST', RESULT = self.most, GAMEID = self.gameID, PICK = self.pick))
            e = datetime.now() - t
            s = e.seconds + (e.microseconds / 1000000)
            self.pipe.send(Message('COMPLETE', PROC_ID = self.id, GAMEID = self.gameID, PICK = self.pick, BLOCK = prefix, ELAPSED = s, COMBINATIONS = c))
        print('Cruncher {} finished.'.format(self.id))
        
    def RESULT(self, m):
        if m['GAMEID'] == self.gameID and m['PICK'] == self.pick:
            if m['RESULT_TYPE'] == 'BEST':
                if m['RESULT'] > self.best:
                    self.best = m['RESULT']
            if m['RESULT_TYPE'] == 'MOST':
                if m['RESULT'] > self.most:
                    self.most = m['RESULT']
    
    def HALT(self, m):
        self.__running = False
    
    def GAME_DATA(self, m):
        self.game = m['GAME']
        self.wait.set()
