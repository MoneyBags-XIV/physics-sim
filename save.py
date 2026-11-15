from main import *
from copy import copy

class Save:
    def __init__(self, masses, springs, lines, gravity, force, snap, walls, collisions):
        self.masses = masses #[copy(mass) for mass in masses]
        self.springs = springs #[copy(spring) for spring in springs]
        self.lines = lines #[copy(line) for line in lines]

        self.desync()

        # self.paused = paused
        self.gravity = gravity
        self.force = force
        self.snap = snap
        self.walls = walls
        self.collisions = collisions
    
    def desync(self):

        for spring in self.springs:
            for i in range(len(self.masses)):
                if self.masses[i] == spring.point_a:
                    spring.point_a_index = i
                elif self.masses[i] == spring.point_b:
                    spring.point_b_index = i

        self.masses = [copy(mass) for mass in self.masses]
        self.springs = [copy(spring) for spring in self.springs]
        self.lines = [copy(line) for line in self.lines]

        for spring in self.springs:
            spring.point_a = self.masses[spring.point_a_index]
            spring.point_b = self.masses[spring.point_b_index]

    def refresh_canvas(self, canvas):
        canvas.delete("all")
        for mass in self.masses:
            mass.create_display_self(canvas)
        for spring in self.springs:
            spring.create_display_self(canvas)
        for line in self.lines:
            line.create_display_self(canvas)
    
    def is_equal(self, other):

        if len(self.masses) != len(other.masses): return False
        for x, y in zip(self.masses, other.masses):
            if not x.is_equal(y):
                return False
        
        if len(self.springs) != len(other.springs): return False
        for x, y in zip(self.springs, other.springs):
            if not x.is_equal(y):
                return False
        
        if len(self.lines) != len(other.lines): return False
        for x, y in zip(self.lines, other.lines):
            if not x.is_equal(y):
                return False

        if self.gravity != other.gravity: return False
        if self.force != other.force: return False
        if self.snap != other.snap: return False
        if self.walls != other.walls: return False
        if self.collisions != other.collisions: return False

        return True