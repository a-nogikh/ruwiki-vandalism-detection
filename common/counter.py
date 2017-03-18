
class Counter:
    def __init__(self, step):
        self.step = step
        self.current = 0

    def tick(self):
        self.current += 1
        if self.current % self.step == 0:
            self.print()

    def print(self):
        print(self.current)