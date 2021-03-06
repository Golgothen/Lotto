from ball import Ball

class Field():
    def __init__(self):
        self.balls = {}
        for a in range(1,46):
            self.balls[a] = Ball(a)
    
    def draw(self, game):
        for g in game.games:
            for b in self.balls.values():
                b.draw(g)
