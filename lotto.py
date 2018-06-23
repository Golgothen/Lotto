import argparse
from itertools import combinations
from cruncher import Workforce
from game import Lotto, OzLotto, PowerBall, USPowerBall, MegaMillions
import pickle, os, multiprocessing


        
if __name__ == '__main__':
    
    def processMessage(m):
        if m.message == 'STATUS':
            print('{}. {:9,.0f} blocks left'.format(m.params['MESSAGE'], workQ.qsize()))
        if m.message == 'RESULT':
            with open('{}-{}.txt'.format(args.game[0], args.pick[0]),'a') as f:
                if 'POWERBALL' in m.params:
                    f.write('Numbers = {} PB = {}, Divisions = {}, Weight = {}.\n'.format(m.params['NUMBERS'], m.params['POWERBALL'], m.params['DIVISIONS'], m.params['WEIGHT']))
                else:
                    f.write('Numbers = {}, Divisions = {}, Weight = {}.\n'.format(m.params['NUMBERS'], m.params['DIVISIONS'], m.params['WEIGHT']))

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

    ap = argparse.ArgumentParser()
    ap.add_argument('--game', nargs = 1, default = ['lotto'], help = ' REQUIRED: Games currently supported = Lotto, OzLotto, Powerball, USPowerball, MegaMillions. Default is Lotto')
    ap.add_argument('--file', nargs = 1, default = ['.csv'], help = ' REQUIRED: CSV File to load for game comparison. Default is <game>.csv')
    ap.add_argument('--day', nargs = '+', default = None, help = 'Applies to Lotto (MON, WED, SAT), MegaMillions (TUE, FRI) and US Powerball (THU, SUN). Select which days to include. Seperate arguments with commas.')
    ap.add_argument('--pick', nargs = 1, type= int, default = [0], help = 'Size of ticket to test. Default is the game minimum (6 for Lotto, 7 for OzLotto)')
    ap.add_argument('--block', nargs = 1, type= int, default = [3], help = 'Size of the combination block.  Default is 3.  Larger blocks have exponentially more combinations')
    ap.add_argument('--resume', nargs = 1, default = None, help = 'Specify an interrupted job to restart')
    args = ap.parse_args()
    
    print(args)
    
    workQ = multiprocessing.Queue()
    resultQ = multiprocessing.Queue()
    game = getGame()
    if args.resume is not None:
        print('Resuming...')
        f = open(args.resume[0], 'rb')
        game = getGame()
        args = pickle.load(f)
        while True:
            try:
                workQ.put(pickle.load(f))
            except (EOFError, pickle.UnpicklingError):
                break
        f.close()
        os.remove(args.resume[0])
    else:
        if args.file[0] == '.csv':
            args.file[0] = args.game[0] + args.file[0]
        game.load(args.file[0], args.day)
    
        if args.pick[0] < game.minPick:
            args.pick[0] = game.minPick
    
        if args.block[0] > game.minPick + 1:
            args.block[0] = game.minPick - 1
        for i in combinations(range(1, game.poolSize - args.block[0] + 1), args.pick[0] - args.block[0]):
            workQ.put(i)
        print('Added {:15,.0f} work blocks to the work queue'.format(workQ.qsize()))
        for i in range(multiprocessing.cpu_count()):
            workQ.put(None)
        
    
    wf = Workforce(workQ, resultQ, args.block[0], game)
    
    try:
        while not workQ.empty():
            processMessage(resultQ.get())
            
    except KeyboardInterrupt:
        # Dump the queue to file
        wf.halt()
        with open('{}.dat'.format(args.game[0]), 'wb') as f:
            pickle.dump(args, f)
            while not workQ.empty():
                pickle.dump(workQ.get(), f)
        wf.stop()
        while not resultQ.empty():
            processMessage(resultQ.get())
            
    
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
    
