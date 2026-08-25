from main import *
from copy import copy

class Save:
    def __init__(self, masses, springs, lines, gravity, force, snap, walls, collisions):
        self.masses = [copy(mass) for mass in masses]
        self.springs = [copy(spring) for spring in springs]
        self.lines = [copy(line) for line in lines]
        # self.paused = paused
        self.gravity = gravity
        self.force = force
        self.snap = snap
        self.walls = walls
        self.collisions = collisions