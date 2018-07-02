import argparse
from itertools import combinations
from cruncher import Workforce
from datetime import datetime
from game import Lotto, OzLotto, PowerBall, USPowerBall, MegaMillions
import pickle, os, multiprocessing
from connection import Connection
from message import Message
from mplogger import *

        
if __name__ == '__main__':

    totalComs = 0
    
    loggingQueue = multiprocessing.Queue()
    listener = LogListener(loggingQueue)
    listener.start()
    
    logging.config.dictConfig(sender_config)
    
    config = sender_config
    config['handlers']['queue']['queue'] = loggingQueue

    logging.config.dictConfig(sender_config)
    logger = logging.getLogger('application')
    
    
    def getGame():            
        if args.game[0].lower() == 'lotto':
            game = Lotto()
        if args.game[0].lower() == 'ozlotto':
            game = OzLotto()
        if args.game[0].lower() == 'powerball':
            game = PowerBall()
        if args.game[0].lower() == 'uspowerball':
            game = USPowerBall()
        if args.game[0].lower() == 'megamillions':
            game = MegaMillions()
        return game

    def processResult(m):
        #print(m)
        with open('{}-{}_{}.txt'.format(m.params['GAMEID'], m.params['PICK'], m.params['RESULT_TYPE']),'a') as f:
            #if 'POWERBALL' in m.params:
            #    f.write('Numbers = {} PB = {}, Divisions = {}, Weight = {}.\n'.format(m.params['NUMBERS'], m.params['POWERBALL'], m.params['DIVISIONS'], m.params['WEIGHT']))
            #else:
            f.write('Numbers = {}, Divisions = {}.\n'.format(m.params['RESULT'].numbers, m.params['RESULT'].divisions))
        #if m.params['RESULT_TYPE'] == 'ALL' and args.all:
        #    with open('{}-{}_all.txt'.format(args.game[0], args.pick[0]),'a') as f:
        #        if 'POWERBALL' in m.params:
        #            f.write('Numbers = {} PB = {}, Divisions = {}.\n'.format(m.params['NUMBERS'], m.params['POWERBALL'], m.params['DIVISIONS']))
        #        else:
        #            f.write('Numbers = {}, Divisions = {}.\n'.format(m.params['NUMBERS'], m.params['DIVISIONS']))

    ap = argparse.ArgumentParser()
    ap.add_argument('--block', nargs = 1, type= int, default = [3], help = 'Size of the combination block.  Default is 3.  Larger blocks have exponentially more combinations')
    ap.add_argument('--server', nargs = 1, default = ['localhost'], help = 'Specify a block server to get work from (IP address or resolvable host name)')
    ap.add_argument('--port', nargs = 1, type = int, default = [2345], help = 'Specify a port to connect on (default = 2345)')
    #ap.add_argument('--all', action = "store_true", default = False, help = 'Record all results')
    
    args = ap.parse_args()
    
    print(args)
    
    workQ = multiprocessing.Queue()
    resultQ = multiprocessing.Queue()
    host = args.server[0]
    port = args.port[0]


    startTime = datetime.now()
    wf = Workforce(workQ, resultQ, host, port, config)
    c = Connection(config)
    c.connect(host, port)
    for i in range(wf.crunchers):
        c.send(Message('GET_BLOCK'))
        workQ.put(c.recv())
    c.close()
    elapsed = 0
    try:
        while True:
            #logger.debug('Work que has {} items'.format(workQ.qsize()))
            if workQ.qsize() < wf.crunchers:
                logger.debug('Adding {} items to work que'.format(wf.crunchers-workQ.qsize()))
                c.connect(host, port)
                for i in range(wf.crunchers-workQ.qsize()):
                    c.send(Message('GET_BLOCK'))
                    workQ.put(c.recv())
                c.close()
            m = resultQ.get()
            if m.message == 'COMPLETED':
                totalElapsed = datetime.now() - startTime
                elapsed = (totalElapsed.microseconds / 1000000) + totalElapsed.seconds
                totalComs += m.params['COMBINATIONS']
                if m.params['ELAPSED'] > 0:
                    print('Completed block {} ({:11,.0f} combinations) in {:7,.1f} seconds ({:9,.0f} coms/sec). {:12,.0f} blocks left.  Overall rate {:11,.0f} coms/sec'.format(m.params['BLOCK'], m.params['COMBINATIONS'], m.params['ELAPSED'], (m.params['COMBINATIONS'] / m.params['ELAPSED']), workQ.qsize(), totalComs / elapsed))
                else:
                    print('Completed block {} ({:11,.0f} combinations) in {:7,.1f} seconds ({:9,.0f} coms/sec). {:12,.0f} blocks left.  Overall rate {:11,.0f} coms/sec'.format(m.params['BLOCK'], m.params['COMBINATIONS'], m.params['ELAPSED'], (0), workQ.qsize(), totalComs / elapsed))
            if m.message == 'RESULT':
                processResult(m)
                
    except KeyboardInterrupt:
        # Dump the queue to file
        wf.halt()
        with open('cruncher.dat', 'wb') as f:
            while not workQ.empty():
                pickle.dump(workQ.get(), f)
        wf.stop()
        while not resultQ.empty():
            m = resultQ.get()
            if m.message == 'COMPLETED':
                totalElapsed = datetime.now() - startTime
                elapsed = (totalElapsed.microseconds / 1000000) + totalElapsed.seconds
                totalComs += m.params['COMBINATIONS']
                if m.params['ELAPSED'] > 0:
                    print('Completed block {} ({:11,.0f} combinations) in {:7,.1f} seconds ({:9,.0f} coms/sec). {:12,.0f} blocks left.  Overall rate {:11,.0f} coms/sec'.format(m.params['BLOCK'], m.params['COMBINATIONS'], m.params['ELAPSED'], (m.params['COMBINATIONS'] / m.params['ELAPSED']), workQ.qsize(), totalComs / elapsed))
                else:
                    print('Completed block {} ({:11,.0f} combinations) in {:7,.1f} seconds ({:9,.0f} coms/sec). {:12,.0f} blocks left.  Overall rate {:11,.0f} coms/sec'.format(m.params['BLOCK'], m.params['COMBINATIONS'], m.params['ELAPSED'], (0), workQ.qsize(), totalComs / elapsed))
            if m.message == 'RESULT':
                processResult(m)
    
    print('{:30,.0f} combinations tested in {:15,.0f} seconds.'.format(totalComs, elapsed))
    listener.stop()
    
def calc():
    from field import Field
    g = Lotto()
    g.load("lotto.csv",['SAT'])
    field = Field()
    field.draw(g)
    m = []
    for b, v in field.balls.items():
        m.append(v.drawnWith)
    s = '  : '
    for a in range(45):
        s += '{:2.0f} '.format(a+1)
    print(s)
    for a in range(45):
        s = '{:2.0f}  '.format(a+1)
        for b in range(45):
            if a==b:
                s += '   '
            else:
                s += '{:2.0f} '.format(m[a][b])
        print(s)
    
    for i in range(1,46):
        print(field.balls[i])
    
