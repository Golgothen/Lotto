from result import Results
import argparse
        
if __name__ == '__main__':
    
    ap = argparse.ArgumentParser()
    ap.add_argument('--game', nargs = 1, default = ['lotto'], help = ' REQUIRED: Games currently supported = Lotto, OzLotto, Powerball, USPowerball, MegaMillions. Default is Lotto')
    ap.add_argument('--file', nargs = 1, default = ['.csv'], help = ' REQUIRED: CSV File to load for game comparison. Default is <game>.csv')
    ap.add_argument('--day', nargs = '+', default = ['SAT'], help = 'Applies to Lotto games only.  Select which days to include out of MON, WED, SAT. Default is SAT only. Seperate arguments with commas.')
    ap.add_argument('--pick', nargs = 1, type= int, default = [0], help = 'Size of ticket to test. Default is the game minimum (6 for Lotto, 7 for OsLotto)')
    ap.add_argument('--block', nargs = 1, type= int, default = [4], help = 'Size of the combination block.  Default is 4 (minimum).  Larger blocks have exponentially more combinations')
    ap.add_argument('--resume', action = "store_true", help = 'Resume an interrupted job')
    args = ap.parse_args()
    
    print(args)
    
    r = Results(args)
    r.compute()
    
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
    
