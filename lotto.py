import argparse, sys, multiprocessing, os
#from itertools import combinations
from cruncher import Workforce
#from datetime import datetime
#from game import Lotto, OzLotto, PowerBall, USPowerBall, MegaMillions
#import pickle, os, multiprocessing
#from connection import Connection
#from message import Message
from mplogger import *
from time import sleep

        
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
    

    ap = argparse.ArgumentParser()
    ap.add_argument('--block', nargs = 1, type= int, default = [3], help = 'Size of the combination block.  Default is 3.  Larger blocks have exponentially more combinations')
    ap.add_argument('--server', nargs = 1, default = ['localhost'], help = 'Specify a block server to get work from (IP address or resolvable host name)')
    ap.add_argument('--port', nargs = 1, type = int, default = [2345], help = 'Specify a port to connect on (default = 2345)')
    
    args = ap.parse_args()
    
    workQ = multiprocessing.Queue()
    #resultQ = multiprocessing.Queue()
    host = args.server[0]
    port = args.port[0]


    startTime = datetime.now()
    wf = Workforce(host, port, config)
    while True:
        try:
            wf.fillQueue()
            try:
                sleep(1)
            except (KeyboardInterrupt, SystemExit):
                print('Waiting for crunchers to complete current work...')
                # Dump the queue to file
                wf.halt()
                wf.stop()
                break
        except (ConnectionRefusedError, OSError, TimeoutError, ConnectionResetError):
            # Host is up but no server found
            #logging.error('FillQueue raised exception:', exc_info = True)
            print('No server found on host {}:{}. Check settings and try again.'.format(host, port))
            if not wf.workAvailable:
                print('No work available. Exiting.')
                wf.abort()
                break
            else:
                try:
                    sleep(29)
                except (KeyboardInterrupt, SystemExit):
                    print('Waiting for crunchers to complete current work...')
                    # Dump the queue to file
                    wf.halt()
                    wf.stop()
                    break
        except (KeyboardInterrupt, SystemExit):
            print('Waiting for crunchers to complete current work...')
            # Dump the queue to file
            wf.halt()
            wf.stop()
            break

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
    
