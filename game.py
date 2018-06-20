from datetime import datetime
from vector import vector
import csv



class Game():
    #
    # Base class for other game types
    #
    def __init__(self, poolSize = None):
        self.games = []
        if poolSize is None:
            self.poolSize = 45
        else:
            self.poolSize = poolSize
        
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
    def len(self):
        return len(self.games)


class Lotto(Game):
    def __init__(self):
        super().__init__(45)
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
        super().__init__(45)
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

class Powerball(Game):
    def __init__(self):
        super().__init__(35)
        self.divisionWeights = vector([300000, 500, 20, 8, 2, 1])
        self.minPick = 7
        self.divisions = 6
    
    def load(self, filename):
        with open(filename) as f:
            reader = csv.reader(f)
            next(reader)        # Discard the heading line
            
            for row in reader:
                g = {}
                g['Drawdate'] = datetime.strptime(row[0],"%d/%m/%Y")
                g['Numbers'] = set([int(i) for i in row[1:8]])
                g['Powerball'] = int(row[8])
                self.games.append(g)
    
    def play(self, numbers):
        result = vector(self.divisions)
        for g in self.games:
            drawcount=len(g['Numbers'].intersection(numbers))
            if drawcount > 2:
                result[7-drawcount]+=1
        return result, sum(result*self.divisionWeights) 

class MegaMillions(Game):
    def __init__(self):
        super().__init__(70)
        self.divisionWeights = vector([250000, 2500, 50, 2, 1])
        self.minPick = 5
        self.divisions = 5
    
    def load(self, filename):
        with open(filename) as f:
            reader = csv.reader(f)
            next(reader)        # Discard the heading line
            
            for row in reader:
                g = {}
                g['Drawdate'] = datetime.strptime(row[0],"%b %d, %Y")
                g['Day'] = row[1]
                g['Numbers'] = set([int(i) for i in row[2:7]])
                g['Megaball'] = int(row[7])
                self.games.append(g)
    
    def play(self, numbers):
        result = vector(self.divisions)
        for g in self.games:
            drawcount=len(g['Numbers'].intersection(numbers))
            if drawcount > 0:
                result[5-drawcount]+=1
        return result, sum(result*self.divisionWeights) 

class USPowerBall(Game):
    def __init__(self):
        super().__init__(69)
        self.divisionWeights = vector([250000, 2500, 50, 2, 1])
        self.minPick = 5
        self.divisions = 5
    
    def load(self, filename):
        with open(filename) as f:
            reader = csv.reader(f)
            next(reader)        # Discard the heading line
            
            for row in reader:
                g = {}
                g['Drawdate'] = datetime.strptime(row[0], "%a, %b %d, %Y")
                g['Day'] = row[1]
                g['Numbers'] = set([int(i) for i in row[2:7]])
                g['Powerball'] = int(row[7])
                self.games.append(g)
    
    def play(self, numbers):
        result = vector(self.divisions)
        for g in self.games:
            drawcount=len(g['Numbers'].intersection(numbers))
            if drawcount > 0:
                result[5-drawcount]+=1
        return result, sum(result*self.divisionWeights) 
