from math import sqrt
import tkinter as tk
from time import sleep, time
import numpy as np

DENSITY = 0.1

class Point:
    def __init__(self, canvas, x, y, mass, energy_return=1, x_vel=0, y_vel=0, static=False, trace=0):
        self.x = x
        self.y = y
        self.mass = mass

        self.energy_return = energy_return
        self.static = static

        self.trace = trace
        self.trace_points = []

        self.x_vel = x_vel
        self.y_vel = y_vel

        self.x_force = self.y_force = 0

        self.radius = sqrt(mass) / DENSITY

        self.canvas = canvas
        self.id = self.canvas.create_oval(0,0,2*self.radius,2*self.radius,fill='red')
        self.canvas.move(self.id, self.x - self.radius, self.y - self.radius)
    
    def apply_force(self, x_comp, y_comp):
        self.x_force += x_comp
        self.y_force += y_comp
    
    def move(self, time):
        if self.static:
            self.x_vel = self.y_vel = 0
            self.x_force = self.y_force = 0
            return

        self.x_vel += (time * self.x_force)/self.mass
        self.y_vel += (time * self.y_force)/self.mass

        self.x += self.x_vel * time
        self.y += self.y_vel * time

        self.update_looks()

        self.x_force = 0
        self.y_force = 0

        # self.handle_traces()

    def handle_traces(self):

        length = self.trace

        if self.trace:
            self.trace_points.append(self.canvas.create_rectangle(self.x, self.y, self.x+1, self.y+1, fill="#%02x%02x%02x" % (0, 0, 0), width=0))
        while len(self.trace_points) > length:
            self.canvas.delete(self.trace_points[0])
            del self.trace_points[0]
        
        # for i, point in enumerate(self.trace_points):
            # brightness = round(255 * (length - i)/length)
            # self.canvas.itemconfigure(point, fill="#%02x%02x%02x" % (brightness, brightness, brightness))

    def handle_collisions(self, masses):
        for mass in masses:
            dist = sqrt((self.x - mass.x)**2 + (self.y - mass.y)**2)
            if dist > self.radius + mass.radius:
                continue

            if mass.x == self.x and mass.y == self.y:   # to handle masses in the same spot
                normal = [1,0]
            else:
                normal = [ans/(dist) for ans in [mass.x - self.x, mass.y - self.y]]
            tangent = [normal[1], -1*normal[0]]

            change_back = np.array([
                [tangent[0], normal[0]],
                [tangent[1], normal[1]]
            ])
            change_base = inverse(change_back)#np.linalg.inv(change_back)

            delta = dist - (self.radius + mass.radius)
            self_b = change_base @ (self.x, self.y)
            mass_b = change_base @ (mass.x, mass.y)

            if self.static and mass.static:
                return
            
            if self.static:
                mass_b[1] -= delta
            elif mass.static:
                self_b[1] += delta
            else:
                self_b[1] += delta/2
                mass_b[1] -= delta/2

            self.x, self.y = change_back @ self_b
            mass.x, mass.y = change_back @ mass_b

            self_b_vel = change_base @ (self.x_vel, self.y_vel)
            mass_b_vel = change_base @ (mass.x_vel, mass.y_vel)

            ua = self_b_vel[1]
            ub = mass_b_vel[1]
            ma = self.mass
            mb = mass.mass
            Cr = self.energy_return * mass.energy_return

            # formulas for velocities of inelastic collision taken from wikipedia
            if self.static:
                mass_b_vel[1] *= -1 * mass.energy_return * self.energy_return
            elif mass.static:
                self_b_vel[1] *= -1 * mass.energy_return * self.energy_return
            else:
                self_b_vel[1] = (Cr*mb*(ub-ua) + ma*ua + mb*ub)/(ma+mb)
                mass_b_vel[1] = (Cr*ma*(ua-ub) + ma*ua + mb*ub)/(ma+mb)

            self.x_vel, self.y_vel = change_back @ self_b_vel
            mass.x_vel, mass.y_vel = change_back @ mass_b_vel

            self_b_force = change_base @ (self.x_force, self.y_force)
            mass_b_force = change_base @ (mass.x_force, mass.y_force)

            # normal = self_b_force[1] - mass_b_force[1]
            # vel = self_b_vel[0] - mass_b_vel[0]
            # mu = 0.5
            # if not vel:
            #     return
            # f_tot = vel/abs(vel) * mu * normal

            # self_b_force[0] -= f_tot/2
            # mass_b_force[0] += f_tot/2

            # self.x_force, self.y_force = change_back @ self_b_force
            # mass.x_force, mass.y_force = change_back @ mass_b_force
        
    def handle_interparticle_forces(self, masses, force_multiplier):
        if not force_multiplier:
            return
        for mass in masses:
            dist = sqrt((self.x - mass.x)**2 + (self.y - mass.y)**2)
            if dist <= self.radius + mass.radius:    # gravity is not applied by overlapping bodies
                continue

            normal = [ans/(dist) for ans in [mass.x - self.x, mass.y - self.y]]
            tangent = [normal[1], -1*normal[0]]

            change_back = np.array([
                [tangent[0], normal[0]],
                [tangent[1], normal[1]]
            ])
            change_base = inverse(change_back)#np.linalg.inv(change_back)

            self_b_force = change_base @ (self.x_force, self.y_force)
            mass_b_force = change_base @ (mass.x_force, mass.y_force)

            f_tot =  (100000 * force_multiplier * self.mass * mass.mass)/(dist**2)

            self_b_force[1] += f_tot
            mass_b_force[1] -= f_tot

            self_b_vel = change_base @ (self.x_vel, self.y_vel)

            self.x_force, self.y_force = change_back @ self_b_force
            mass.x_force, mass.y_force = change_back @ mass_b_force


    def update_mass(self, mass):
        self.mass = mass
        self.radius = sqrt(mass) / DENSITY
        self.update_looks()
    
    def update_looks(self):
        self.canvas.coords(self.id, self.x-self.radius, self.y-self.radius, self.x+self.radius, self.y+self.radius)


class Spring:
    def __init__(self, canvas, point_a, point_b, k, c, eq_len=0):
        self.k = k
        self.c = c
        self.point_a = point_a
        self.point_b = point_b
        self.length = self.old_length = distance(point_a, point_b)
        self.eq_len = eq_len if eq_len else self.length

        self.canvas = canvas

        self.rod = False

        self.create_display_self()
    
    def create_display_self(self):
        self.id = self.canvas.create_line(self.point_a.x, self.point_a.y, self.point_b.x, self.point_b.y, dash=(10,10), width=2)

    def apply_forces(self):

        self.length = distance(self.point_a,self.point_b)
        dx = self.length - self.old_length
        self. old_length = self.length

        f_tot = (self.k * (self.length - self.eq_len)) + (self.c * dx)

        x_len = self.point_a.x - self.point_b.x
        y_len = self.point_a.y - self.point_b.y

        sine = y_len/self.length
        cosine = x_len/self.length

        y_comp = f_tot * sine
        x_comp = f_tot * cosine

        # if dx > abs(self.length - self.eq_len) and self.rod:
        #     return

        self.point_a.apply_force(-1 * x_comp, -1 * y_comp)
        self.point_b.apply_force(x_comp, y_comp)
    
    def move(self):
        self.canvas.coords(self.id, self.point_a.x, self.point_a.y, self.point_b.x, self.point_b.y)


class Rod(Spring):
    def __init__(self, canvas, point_a, point_b):
        super().__init__(canvas, point_a, point_b, 20000, 5000)
        self.rod = True
    def create_display_self(self):
        self.id = self.canvas.create_line(self.point_a.x, self.point_a.y, self.point_b.x, self.point_b.y, width=2)


class Static_Collision_Polygon:
    def __init__(self, canvas, friction, energy_return, points, fill='black'):
        self.canvas = canvas
        self.friction = friction
        self.energy_return = energy_return
        self.points = points
        self.lines = []

        self.id = self.canvas.create_polygon(*sum(points, ()), fill=fill)

        for i in range(len(points)):
            if i == len(points)-1:
                self.lines.append(Static_Collision_Line(canvas, points[i], points[0], friction, energy_return, display=False))
                continue
            self.lines.append(Static_Collision_Line(canvas, points[i], points[i+1], friction, energy_return, display=False))

    def handle_collisions(self, masses):
        for line in self.lines:
            line.handle_collisions(masses)


class Static_Collision_Line:
    def __init__(self, canvas, coord_a, coord_b, friction, energy_return, display=True):
        self.canvas = canvas
        self.coord_a = coord_a
        self.coord_b = coord_b
        self.friction = friction
        self.energy_return = energy_return

        if coord_a[0] == coord_b[0] and coord_a[1] < coord_b[1]:
            self.coord_a, self.coord_b = coord_b, coord_a
        elif coord_a[1] == coord_b[1] and coord_a[0] > coord_b[0]:
            self.coord_a, self.coord_b = coord_b, coord_a

        self.id = self.canvas.create_line(*coord_a, *coord_b, width=2, capstyle=tk.ROUND) if display else None

        self.set_end_orth_lines()
    
    def update_looks(self):
        self.id = self.canvas.create_line(*self.coord_a, *self.coord_b, width=2, capstyle=tk.ROUND)


    def set_end_orth_lines(self):
        # self.length = sqrt((self.coord_a[0] - self.coord_b[0])**2 + (self.coord_a[1] - self.coord_b[1])**2)

        if self.coord_a[0] == self.coord_b[0]:  # handles vertical surfaces
            self.change_base_matrix = self.change_back_matrix = np.array([
                [0,1],
                [1,0]
            ])

            self.func = lambda x : np.inf if x > self.coord_a[0] else -1 * np.inf
            self.line1_func = lambda x : self.coord_a[1]
            self.line2_func = lambda x : self.coord_b[1]
            return

        if self.coord_a[1] == self.coord_b[1]:  # handles flat surfaces
            self.change_base_matrix = self.change_back_matrix = np.array([
                [1,0],
                [0,-1]  # the sign here is to handle quirks with directionality
            ])

            self.func = lambda x : self.coord_a[1]
            self.line1_func = lambda x : np.inf if x > self.coord_a[0] else -1 * np.inf
            self.line2_func = lambda x : np.inf if x > self.coord_b[0] else -1 * np.inf
            return

        m = self.m = (self.coord_b[1] - self.coord_a[1])/(self.coord_b[0] - self.coord_a[0])
        ortho_m = (-1)/m

        self.tangent = [x/sqrt(1 + m**2) for x in [1, m]]
        self.normal = [self.tangent[1], -self.tangent[0]]

        self.change_back_matrix = np.array([
            [self.tangent[0], self.normal[0]],
            [self.tangent[1], self.normal[1]]
        ])
        self.change_base_matrix = inverse(self.change_back_matrix)#np.linalg.inv(self.change_back_matrix)

        self.func = lambda x : m*(x-self.coord_a[0]) + self.coord_a[1]
        
        if self.coord_a[1] > self.coord_b[1]:
            self.line1_func = lambda x : ortho_m*(x-self.coord_a[0]) + self.coord_a[1]
            self.line2_func = lambda x : ortho_m*(x-self.coord_b[0]) + self.coord_b[1]
        else:
            self.line1_func = lambda x : ortho_m*(x-self.coord_b[0]) + self.coord_b[1]
            self.line2_func = lambda x : ortho_m*(x-self.coord_a[0]) + self.coord_a[1]
    
    def change_base(self, vector):
        return self.change_base_matrix @ vector
    def change_back(self, vector):
        return self.change_back_matrix @ vector

    def handle_collisions(self, masses):
        line_collidables = []
        for mass in masses:
            if mass.y > self.line1_func(mass.x) or mass.y < self.line2_func(mass.x):
                continue

            line_collidables.append(mass)

            x1, y1 = self.coord_a
            x2, y2 = self.coord_b
            x0 = mass.x
            y0 = mass.y

            # formula for distance between point and line taken from Wikipedia
            dist = abs(((y2-y1)*x0)-((x2-x1)*y0) + x2*y1 - y2*x1)/sqrt((y2-y1)**2 + (x2-x1)**2)
            
            if dist < mass.radius:

                delta = mass.radius - dist
                b = self.change_base((mass.x, mass.y))

                if mass.y > self.func(mass.x):
                    b[1] -= delta
                else:
                    b[1] += delta
                mass.x, mass.y = self.change_back(b)

                b_vel = self.change_base((mass.x_vel, mass.y_vel))
                b_vel[1] *= -1*self.energy_return*mass.energy_return
                mass.x_vel, mass.y_vel = self.change_back(b_vel)

                if b_vel[0] == 0:
                    continue

                b_force = self.change_base((mass.x_force, mass.y_force))
                friction = b_force[1] * self.friction * b_vel[0]/abs(b_vel[0])
                b_force[0] += friction
                mass.x_force, mass.y_force = self.change_back(b_force)
        
        end_collidables = [mass for mass in masses if not mass in line_collidables]
        
        for point in [self.coord_a, self.coord_b]:
            x = point[0]
            y = point[1]

            for mass in end_collidables:
                dist = sqrt((mass.x-x)**2 + (mass.y-y)**2)
                if dist > mass.radius:
                    continue

                delta = dist - mass.radius

                collision_norm = [a/dist for a in [mass.x-x, mass.y-y]]
                collision_tan = [-collision_norm[1], collision_norm[0]]

                change_back = np.array([
                    [collision_tan[0], collision_norm[0]],
                    [collision_tan[1], collision_norm[1]]
                ])
                change_base = inverse(change_back)#np.linalg.inv(change_back)

                b = change_base @ (mass.x, mass.y)
                b[1] -= delta
                mass.x, mass.y = change_back @ b

                # currently a collision with the end of a rod or corner of a 
                # polygon does not result in losses to friction, only energy return
                b_vel = change_base @ (mass.x_vel, mass.y_vel)
                # b_vel[0] *= self.friction
                b_vel[1] *= -1*self.energy_return*mass.energy_return
                mass.x_vel, mass.y_vel = change_back @ b_vel


def distance(point_a, point_b):
    x_dis = point_a.x - point_b.x
    y_dis = point_a.y - point_b.y
    return sqrt(x_dis**2 + y_dis**2)

def inverse(matrix):
    a = matrix[0][0]
    b = matrix[0][1]
    c = matrix[1][0]
    d = matrix[1][1]

    det = 1/(a*d - b*c)

    inverse = [
        [det*d, det*-b],
        [det*-c, det*a]
    ]

    return np.array(inverse)