from vector import vector
from datetime import datetime

class Ball():
    def __init__(self, v):
        self.value = v
        self.drawnWith = vector(45)
        self.supWith = vector(45)
        self.lastDrawn = datetime(1900,1,1)
        self.streaks = vector(1)
        self.nonStreaks = vector(1)
        self.drawStreaks = vector(1)
        
    #@jit(nonpython=true)
    def draw(self, game):
        if self.value in game['Numbers'] or self.value in game['Sups']:
            if self.nonStreaks[0] != 0:
                self.nonStreaks.insert(0,0)
            self.streaks[0] += 1
            if self.value in game['Numbers']:
                self.drawStreaks[0] += 1
            if game['Drawdate'] > self.lastDrawn:
                self.lastDrawn = game['Drawdate']
            for a in game['Numbers']:
                self.drawnWith[a-1] += 1
            for a in game['Sups']:
                #self.drawnWith[a-1] += 1
                self.supWith[a-1] += 1
        else:
            if self.streaks[0] != 0:
                self.streaks.insert(0,0)
            if self.drawStreaks[0] != 0:
                self.drawStreaks.insert(0,0)
            self.nonStreaks[0] += 1
    
    @property
    def count(self):
        return self.drawnWith[self.value-1]
    
    @property
    def sup(self):
        return  self.supWith[self.value-1]
    
    @property
    def strikeRate(self):
        return (self.count + self.sup)/(sum(self.streaks)+sum(self.nonStreaks))*100
    
    def __str__(self):
        s =  'Ball {}:\n'.format(self.value)
        s += '  Drawn {} times, Supped {} times, {} in total, strike rate of {:3.3f}%, last drawn on {}\n'.format(self.count,self.sup, self.count + self.sup, self.strikeRate, self.lastDrawn)
        s += '  Current draw streak: {}, Longest draw streak: {}, Average draw streak: {:2.3f}\n'.format(self.drawStreaks[0],max(self.drawStreaks),self.drawStreaks.mean)
        s += '  Current pick streak: {}, Longest pick streak: {}, Average pick streak: {:2.3f}\n'.format(self.streaks[0],max(self.streaks),self.streaks.mean)
        s += '  Current miss streak: {}, Longest miss streak: {}, Average miss streak: {:2.3f}\n'.format(self.nonStreaks[0],max(self.nonStreaks),self.nonStreaks.mean)
        s += '  Top 10 most commonly drawn with - Ball(Count):\n    '
        t = self.drawnWith.sort(True)
        for i in range(1, 11):
            s += '{}({}), '.format(t[i][0]+1, t[i][1])
        s = s[:-2] + '\n'
        s += '  Top 10 most commonly supplemented with - Ball(Count):\n    '
        t = self.supWith.sort(True)
        for i in range(1, 11):
            s += '{}({}), '.format(t[i][0]+1, t[i][1])
        s = s[:-2] + '\n'
        return s
