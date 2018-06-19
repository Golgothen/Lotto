from datetime import datetime
#import numpy as np

class Game():
    def __init__(self, data):
        self.day = data[0]
        self.drawDate = datetime.strptime(data[1],"%d/%m/%Y")
        self.numbers = set([int(i) for i in data[2:8]])
        self.sups = set([int(i) for i in data[8:10]])
    
    #@jit(nonpython=true)
    def play(self, numbers):
        drawcount = 0
        supcount = 0
        if len(self.numbers) == 6 and len(self.sups) == 2 and len(numbers) > 5:
            drawcount=len(self.numbers.intersection(numbers))
            supcount=len(self.sups.intersection(numbers))
            #for n in numbers:
            #    if n in self.numbers:
            #        drawcount += 1
            #    if n in self.sups:
            #        supcount += 1
            #print((drawcount,supcount))
            if drawcount == 6:
                return 1
            if drawcount == 5:
                if supcount > 0:
                    return 2
                return 3
            if drawcount == 4:
                return 4
            if drawcount == 3 and supcount > 0:
                return 5
            if drawcount > 0 and supcount == 2:
                return 6
            return None
