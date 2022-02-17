class Ship():
    def __init__(self,field):
        self.size = len(field)
        self.field = field
        self.sunk = False

        self.hitlocs = []

    def hit(self,loc):
        self.hitlocs.append(loc)
        if len(self.hitlocs) == self.size:
            self.sunk = True
