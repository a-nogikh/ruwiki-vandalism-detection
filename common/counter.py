
class Counter:
    def __init__(self, step, total=None):
        self.step = step
        self.current = 0
        self.total = total

    def tick(self):
        self.current += 1
        if self.current % self.step == 0:
            self.print()

    def mass_tick(self, cnt):
        prev = self.current
        self.current += cnt
        if int(prev/self.step) != int(self.current /self.step):
            self.print()

    def print(self):
        total_part = "" if self.total is None else "/"+str(self.total)
        print(str(self.current) + total_part)
