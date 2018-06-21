from game import *
from result import Results
import argparse


class Procs():
    def __init__(self, id):
        self.id = id
        self.lastMessage = ''
        self.lastResult = {'Numbers' : vector(7), 'Divisions' : vector(6), 'Weight' : 0}
        self.bestResult = {'Numbers' : vector(7), 'Divisions' : vector(6), 'Weight' : 0}
        
if __name__ == '__main__':
    
    ap = argparse.ArgumentParser()
    ap.add_argument('--game', nargs = 1, default = ['lotto'], help = ' REQUIRED: Games currently supported = Lotto, OzLotto, Powerball, USPowerball, MegaMillions. Default is Lotto')
    ap.add_argument('--file', nargs = 1, default = ['.csv'], help = ' REQUIRED: CSV File to load for game comparison. Default is <game>.csv')
    ap.add_argument('--day', nargs = '+', default = ['SAT'], help = 'Applies to Lotto games only.  Select which days to include out of MON, WED, SAT. Default is SAT only. Seperate arguments with commas.')
    ap.add_argument('--pick', nargs = 1, type= int, default = [0], help = 'Size of ticket to test. Default is the game minimum (6 for Lotto, 7 for OsLotto)')
    ap.add_argument('--block', nargs = 1, type= int, default = [4], help = 'Size of the combination block.  Default is 4 (minimum).  Larger blocks have exponentially more combinations')
    
    args = ap.parse_args()
    
    print(args)
    
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

    if args.file[0] == '.csv':
        args.file[0] = args.game[0] + args.file[0]
    
    game.load(args.file[0])
    #game.divisionWeights = vector([1,1,1,1,1,1])
    r = Results(game, args.game[0])
    if args.block[0] < 3:
        args.block[0] = 3
    r.compute(args.pick[0],args.block[0])
    
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
#    
#    for g in games:
#        d = g.play((1, 15, 11, 42, 31, 12, 36))
#        if d is not None:
#            print('Game {} paid dividend {}'.format(g.drawDate, d))
    
