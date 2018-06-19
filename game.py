from datetime import datetime
from vector import vector
import csv



class Game():
    #
    # Base class for other game types
    #
    def __init__(self, barrels = None):
        self.games = []
        self.__barrels = []
        if barrels is None:
            self.__barrels.append(45)
        else:
            self.__barrels = barrels.copy()
        
    def load(self, filename):
        #
        # Implement this in subclasses
        #
        pass
    
    def play(self, numbers):
        #
        # Implement this in subclasses
        #
        pass
    
    @property
    def poolSize(self):
        return self.__barrels[0]
    
    @property
    def len(self):
        return len(self.games)


class Lotto(Game):
    def __init__(self):
        super().__init__([45])
        self.divisionWeights = vector([95000, 750, 100, 3, 2, 1])
        self.minPick = 6
        self.divisions = 6
    
    def load(self, filename, day = None):
        if day is None:
            day = ['SAT','MON','WED']
        with open(filename) as f:
            reader = csv.reader(f)
            next(reader)        # Discard the heading line
            
            for row in reader:
                if row[0] in day:  # + ['WED','MON']
                    g = {}
                    g['Drawdate'] = datetime.strptime(row[1],"%d/%m/%Y")
                    g['Numbers'] = set([int(i) for i in row[2:8]])
                    g['Sups'] = set([int(i) for i in row[8:10]])
                    self.games.append(g)
    
    def play(self, numbers):
        result=vector(self.divisions)
        for g in self.games:
            drawcount = 0
            supcount = 0
            drawcount=len(g['Numbers'].intersection(numbers))
            supcount=len(g['Sups'].intersection(numbers))
            if drawcount == 6:
                result[0]+=1
                continue
            if drawcount == 5:
                if supcount > 0:
                    result[1]+=1
                    continue
                else:
                    result[2]+=1
                    continue
            if drawcount == 4:
                result[3]+=1
                continue
            if drawcount == 3 and supcount > 0:
                result[4]+=1
                continue
            if drawcount > 0 and supcount == 2:
                result[5]+=1
        return result, sum(result*self.divisionWeights)

class OzLotto(Game):
    def __init__(self):
        super().__init__([45])
        self.divisionWeights = vector([680000, 1550, 200, 20, 3, 2, 1])
        self.minPick = 7
        self.divisions = 7
    
    def load(self, filename):
        with open(filename) as f:
            reader = csv.reader(f)
            next(reader)        # Discard the heading line
            
            for row in reader:
                g = {}
                g['Drawdate'] = datetime.strptime(row[0],"%d/%m/%Y")
                g['Numbers'] = set([int(i) for i in row[1:8]])
                g['Sups'] = set([int(i) for i in row[8:10]])
                self.games.append(g)
    
    def play(self, numbers):
        result=vector(self.divisions)
        for g in self.games:
            drawcount = 0
            supcount = 0
            drawcount=len(g['Numbers'].intersection(numbers))
            supcount=len(g['Sups'].intersection(numbers))
            if drawcount == 7:
                result[0]+=1
                continue
            if drawcount == 6:
                if supcount > 0:
                    result[1]+=1
                    continue
                else:
                    result[2]+=1
                    continue
            if drawcount == 5:
                if supcount > 0:
                    result[3]+=1
                    continue
                else:
                    result[4]+=1
                    continue
            if drawcount == 4:
                result[5]+=1
                continue
            if drawcount == 3 and supcount > 0:
                result[6]+=1
                continue
        return result, sum(result*self.divisionWeights)
