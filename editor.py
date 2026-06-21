from main import *
from time import time
from random import shuffle

WIDTH = 1200
HEIGHT = 600

paused = True
selected = None

def play_pressed():
    global paused
    paused = not paused

def change_mode(canvas, mode, mass_menu, spring_menu, line_menu, delete):
    global selected
    global springs
    global collision_shapes
    global last_click
    global grey_line
    global pause_update

    if mode.get() != 'select' or mode.get() == 'line':
        for spring in springs:
            if selected == spring.id:
                canvas.itemconfigure(selected, fill='black')
                selected = None
        for shape in collision_shapes:
            if selected == shape.id:
                canvas.itemconfigure(selected, fill='black')
                selected = None

    mass_menu.place(x=-1000, y=-1000)
    spring_menu.place(x=-1000, y=-1000)
    line_menu.place(x=-1000, y=-1000)
    delete.place(x=-1000, y=-1000)

    if mode.get() != 'line':
        if grey_line:
            canvas.delete(grey_line)
            grey_line = None
        if last_click:
            last_click = None

    if mode.get() == 'mass':
        mass_menu.place(x=10, y=130)
        pause_update = True
        mass_menu.winfo_children()[6].variable.set('0')
        mass_menu.winfo_children()[8].variable.set('0')
        pause_update = False
 
    elif mode.get() == 'spring':
        spring_menu.place(x=10, y=130)
    
    elif mode.get() == 'line':
        line_menu.place(x=10, y=130)
    
    elif mode.get() == 'select':
        delete.place(x=WIDTH-110, y=90)
        
        if not selected:
            return
        
        for spring in springs:
            if spring.id == selected and not spring.rod:
                spring_menu.place(x=10, y=130)
                pause_update = True
                spring_menu.winfo_children()[1].set(spring.k)
                spring_menu.winfo_children()[3].set(spring.c)
                spring_menu.winfo_children()[7].set(spring.eq_len)
                pause_update = False
                return
        
        for shape in collision_shapes:
            if shape.id == selected:
                line_menu.place(x=10, y=130)
                pause_update = True
                line_menu.winfo_children()[1].set(shape.friction)
                line_menu.winfo_children()[3].set(shape.energy_return)
                pause_update = False
        
        for mass in masses:
            if mass.id == selected:
                mass_menu.place(x=10, y=130)
                pause_update = True
                mass_menu.winfo_children()[1].set(mass.mass)
                mass_menu.winfo_children()[2].variable.set(mass.static)
                mass_menu.winfo_children()[4].set(mass.energy_return)
                mass_menu.winfo_children()[6].variable.set(str(mass.x_vel))
                mass_menu.winfo_children()[8].variable.set(str(mass.y_vel))
                mass_menu.winfo_children()[10].set(mass.trace)
                pause_update = False


def handle_click(event, mode, mass_menu, spring_menu, line_menu):

    global selected
    global masses
    global springs
    global collision_shapes
    global last_click
    global pause_update
    global snap
    global snap_lines

    canvas = event.widget
    x = canvas.canvasx(event.x)
    y = canvas.canvasy(event.y)
    
    if mode.get() == 'mass':
        mass = mass_menu.winfo_children()[1].get()
        static = mass_menu.winfo_children()[2].variable.get()
        energy_return = float(mass_menu.winfo_children()[4].get())
        try:
            x_vel = float(mass_menu.winfo_children()[6].get())
        except:
            x_vel = 0
        try:
            y_vel = float(mass_menu.winfo_children()[8].get())
        except:
            y_vel = 0
        trail_length = mass_menu.winfo_children()[10].get()
        if not snap.get():
            masses.append(Point(canvas, x, y, mass, static=static, energy_return=energy_return, y_vel=y_vel, x_vel=x_vel, trace=trail_length))
        else:
            masses.append(Point(canvas, round(x/30)*30, round(y/30)*30, mass, static=static, energy_return=energy_return, y_vel=y_vel, x_vel=x_vel, trace=trail_length))
        canvas.update_idletasks()
        # canvas.update()
        return

    if mode.get() == 'line':
        if not last_click:
            if not snap.get():
                last_click = (x,y)
            else:
                last_click = (30*round(x/30), 30*round(y/30))
            return
        if (x,y) == last_click:
            return
        mu = float(line_menu.winfo_children()[1].get())
        energy = float(line_menu.winfo_children()[3].get())
        if not snap.get():
            collision_shapes.append(Static_Collision_Line(canvas, last_click, (x,y), mu, energy))
        else:
            collision_shapes.append(Static_Collision_Line(canvas, last_click, (30*round(x/30),30*round(y/30)), mu, energy))
        canvas.update_idletasks()
        # canvas.update()

        last_click = None
        return

    overlapping = canvas.find_overlapping(x-10, y-10, x+10, y+10)
    # overlapping = [x for x in overlapping if not x in snap_lines]

    selectables = [x.id for x in collision_shapes + masses + springs]
    overlapping = [x for x in overlapping if x in selectables and not x == selected]

    if not overlapping:
        fill = 'red'
        for spring in springs:
            if spring.id == selected:
                fill = 'black'
                break
        for shape in collision_shapes:
            if shape.id == selected:
                fill = 'black'
                break
        canvas.itemconfigure(selected, fill=fill)
        
        selected = None
        return
    
    if mode.get() != 'select':
        for spring in springs:
            if spring.id == overlapping[0]:
                return
        for shape in collision_shapes:
            if shape.id == overlapping[0]:
                return
    
    if not selected or mode.get() == 'select':

        if mode.get() == 'select':
            mass_menu.place(x=-1000, y=-1000)
            spring_menu.place(x=-1000, y=-1000)
            line_menu.place(x=-1000, y=-1000)

        fill = 'red'
        for spring in springs:
            if spring.id == selected:
                fill = 'black'
                break
        for shape in collision_shapes:
            if shape.id == selected:
                fill = 'black'
                break

        canvas.itemconfigure(selected, fill=fill)

        selected = overlapping[0]
        canvas.itemconfigure(selected, fill='green')

        for spring in springs:
            if selected == spring.id and not spring.rod:
                pause_update = True
                spring_menu.winfo_children()[1].set(spring.k)
                spring_menu.winfo_children()[3].set(spring.c)
                spring_menu.winfo_children()[7].set(spring.eq_len)
                pause_update = False
                break
        
        for shape in collision_shapes:
            if selected == shape.id:
                pause_update = True
                line_menu.winfo_children()[1].set(shape.friction)
                line_menu.winfo_children()[3].set(shape.energy_return)
                pause_update = False
                break
        
        for mass in masses:
            if selected == mass.id:
                pause_update = True
                mass_menu.winfo_children()[1].set(mass.mass)
                mass_menu.winfo_children()[2].variable.set(mass.static)
                mass_menu.winfo_children()[4].set(mass.energy_return)
                mass_menu.winfo_children()[6].variable.set(str(mass.x_vel))
                mass_menu.winfo_children()[8].variable.set(str(mass.y_vel))
                mass_menu.winfo_children()[10].set(mass.trace)
                pause_update = False
                break

        canvas.update_idletasks()
        # canvas.update()

        if mode.get() != 'select':
            return

        for spring in springs:
            if spring.id == selected:
                if spring.rod:
                    return
                spring_menu.place(x=10, y=130)
                return
        for shape in collision_shapes:
            if shape.id == selected:
                line_menu.place(x=10, y=130)
                return
        mass_menu.place(x=10, y=130)
        return

    if mode.get() != 'select':
        point_a = None
        point_b = None

        for mass in masses:
            if mass.id == selected:
                point_a = mass
            if mass.id == overlapping[0]:
                point_b = mass

        if point_a == point_b:
            return
        
        if mode.get() == 'rod':
            springs.append(Rod(canvas, point_a, point_b))
        
        else:
            k = spring_menu.winfo_children()[1].get()
            c = spring_menu.winfo_children()[3].get()
            use_eq = spring_menu.winfo_children()[5].variable.get()
            eq = spring_menu.winfo_children()[7].get() if use_eq else 0
            
            springs.append(Spring(canvas, point_a, point_b, k, c, eq))

        canvas.itemconfigure(selected, fill='red')
        selected = None

        return


def handle_motion(event, canvas):
    global last_click
    global grey_line

    canvas.delete(grey_line)
    grey_line = None

    if not last_click:
        return
    
    grey_line = canvas.create_line(event.x, event.y, last_click[0], last_click[1], fill='grey')


def delete_selected(canvas, mode, mass_menu, spring_menu, line_menu):
    global selected
    global masses
    global springs
    global collision_shapes

    for mass in masses:
        if mass.id == selected:
            for pix in mass.trace_points:
                canvas.delete(pix)
    masses = [mass for mass in masses if mass.id != selected]
    springs = [spring for spring in springs if spring.id != selected]
    collision_shapes = [shape for shape in collision_shapes if shape.id != selected]
    canvas.delete(selected)
    
    spring_ids = []
    for spring in springs:
        if spring.point_a.id == selected or spring.point_b.id == selected:
            spring_ids.append(spring.id)
    springs = [spring for spring in springs if spring.point_a.id != selected and spring.point_b.id != selected]
    canvas.delete(*spring_ids)

    selected = None
    if mode == 'select':
        mass_menu.place(x=-1000, y=-1000)
        spring_menu.place(x=-1000, y=-1000)
        line_menu.place(x=-1000, y=-1000)
    canvas.update_idletasks()
    # canvas.update()


def update_selected(canvas, mode, mass_menu, spring_menu, line_menu):
    global pause_update
    
    if mode != 'select' or pause_update:
        return

    global selected
    global springs
    global masses
    global collision_shapes

    ans = None
    is_spring = False
    is_shape = False

    for mass in masses:
        if mass.id == selected:
            ans = mass
            break
    
    if not ans:
        for spring in springs:
            if spring.id == selected:
                ans = spring
                is_spring = True
                break
    
    if not ans:
        for shape in collision_shapes:
            if shape.id == selected:
                ans = shape
                is_shape = True
                break
    
    if is_spring:
        ans.k = spring_menu.winfo_children()[1].get()
        ans.c = spring_menu.winfo_children()[3].get()
        use_eq = spring_menu.winfo_children()[5].variable.get()
        if use_eq:
            ans.eq_len = spring_menu.winfo_children()[7].get()
        return
    
    elif is_shape:
        ans.friction = float(line_menu.winfo_children()[1].get())
        ans.energy_return = float(line_menu.winfo_children()[3].get())
        return
    
    ans.update_mass(mass_menu.winfo_children()[1].get())
    ans.static = mass_menu.winfo_children()[2].variable.get()
    ans.energy_return = float(mass_menu.winfo_children()[4].get())
    global paused
    if paused:
        try:
            ans.x_vel = float(mass_menu.winfo_children()[6].get())
        except:
            pass
        try:
            ans.y_vel = float(mass_menu.winfo_children()[8].get())
        except:
            pass

    ans.trace = mass_menu.winfo_children()[10].get()

    canvas.update_idletasks()
    # canvas.update()


def reset_canvas(canvas, mode, mass_menu, spring_menu, line_menu):
    global masses
    global springs
    global collision_shapes
    global selected
    global paused
    global walls

    masses = []
    springs = []
    collision_shapes = list(walls)
    selected = None
    paused = True

    if mode == 'select':
        mass_menu.place(x=-1000, y=-1000)
        spring_menu.place(x=-1000, y=-1000)
        line_menu.place(x=-1000, y=-1000)

    canvas.delete('all')

    for shape in collision_shapes:
        shape.update_looks()
    
    update_grid(canvas)

    canvas.update_idletasks()
    # canvas.update()


def update_grid(canvas):
    global snap
    global snap_lines
    if not snap.get():
        for line in snap_lines:
            canvas.delete(line)
        return
    for i in range((WIDTH//30) + 1):
        snap_lines.append(canvas.create_line(i*30, 0, i*30, HEIGHT, fill='grey'))
    for i in range((HEIGHT//30) + 1):
        snap_lines.append(canvas.create_line(0, i*30, WIDTH, i*30, fill='grey'))


def main():
    timestep = 0.005

    root = tk.Tk()
    root.attributes('-type', 'dialog')              #This is for omarchy to not tile the window
    canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT)#, background='white')
    root.geometry(str(WIDTH)+'x'+str(HEIGHT))

    canvas.grid()

    play = tk.Button(canvas, text='Play/Pause', command=play_pressed, width=10, height=1)
    play.place(x=WIDTH-110, y=10)

    modes = ['select', 'mass', 'spring', 'rod', 'line']
    mode_value = tk.StringVar(canvas, value='mass')
    mode_value.trace_add('write', lambda *args : change_mode(canvas, mode_value, mass_menu, spring_menu, line_menu, delete))
    # mode = tk.OptionMenu(canvas, mode_value, *modes)
    # mode.place(x=10, y=50)
    mode_frame = tk.Frame(canvas, highlightbackground='black', highlightthickness=1)
    mode_frame.place(x=10,y=10)

    for option in modes:
        ans = tk.Radiobutton(mode_frame, text=option, variable=mode_value, value=option)
        ans.pack()

    gravity_frame = tk.Frame(canvas, highlightbackground='black', highlightthickness=1)
    gravity_frame.place(x=215, y=10)

    gravity_label = tk.Label(gravity_frame, text='Gravity (down):')
    gravity_var = tk.IntVar(value=1)
    gravity = tk.Scale(gravity_frame, from_=0, to=5, orient=tk.HORIZONTAL, variable=gravity_var)
    gravity_label.grid(row=0, column=0)
    gravity.grid(row=0, column=1)
    # gravity_label.place(x=140, y=20)
    # gravity.place(x=250, y=10)

    force_label = tk.Label(gravity_frame, text='Gravity\n(between bodies):')
    force_var = tk.IntVar(value=0)
    force = tk.Scale(gravity_frame, from_=-10, to=10, orient=tk.HORIZONTAL, variable=force_var)
    force_label.grid(row=1, column=0)
    force.grid(row=1, column=1)
    # force_label.place(x=140, y=50)
    # force.place(x=250, y=50)

    KE = tk.Label(canvas, text='Total KE: 0')
    KE.place(x=WIDTH-120, y=HEIGHT-30)

    options = tk.Frame(canvas, highlightbackground='black', highlightthickness=1)
    options.place(x=80, y=10)

    global snap
    global snap_lines
    snap = tk.IntVar(value=0)
    snap_lines = []
    grid = tk.Checkbutton(options, text='Snap to grid', variable=snap, command=lambda *args : update_grid(canvas))
    grid.pack()
    # grid.place(x=100, y=90)

    walls_var = tk.IntVar(value=1)
    use_walls = tk.Checkbutton(options, text='Walls', variable=walls_var)
    use_walls.pack()
    # use_walls.place(x=100, y=120)

    collision_var = tk.IntVar(value=1)
    collision = tk.Checkbutton(options, text='Particle Collisions', variable=collision_var)
    collision.pack()
    # collision.place(x=100, y=150)

    canvas.bind("<Button-1>", lambda event : handle_click(event, mode_value, mass_menu, spring_menu, line_menu))
    canvas.bind("<Motion>", lambda event : handle_motion(event, canvas))


    #=====================MASS MENU=========================
    mass_menu = tk.Frame(canvas, highlightbackground='black', highlightthickness=1)
    mass_menu.place(x=10, y=130)

    mass_label = tk.Label(mass_menu, text="Mass:")
    mass_label.pack()
    mass_var = tk.IntVar(value=3)
    mass = tk.Scale(mass_menu, from_=1, to=20, orient=tk.HORIZONTAL, variable=mass_var)
    mass.pack()

    static_var = tk.IntVar(value=0)
    static = tk.Checkbutton(mass_menu, text='Static', variable=static_var)
    static.variable = static_var
    static.pack()

    energy_return_label = tk.Label(mass_menu, text="Energy Return:")
    energy_return_label.pack()
    energy_return_var = tk.StringVar(value='0.7')
    energy_return = tk.Scale(mass_menu, from_=0, to=1, orient=tk.HORIZONTAL, variable=energy_return_var, resolution=0.1)
    energy_return.pack()

    x_vel_label = tk.Label(mass_menu, text='x velocity')
    x_vel_label.pack()
    x_vel_var = tk.StringVar(value='0')
    x_vel = tk.Entry(mass_menu, textvariable=x_vel_var)
    x_vel.variable = x_vel_var
    x_vel.pack()

    y_vel_label = tk.Label(mass_menu, text='y velocity')
    y_vel_label.pack()
    y_vel_var = tk.StringVar(value='0')
    y_vel = tk.Entry(mass_menu, textvariable=y_vel_var)
    y_vel.variable = y_vel_var
    y_vel.pack()

    trail_label = tk.Label(mass_menu, text='Leave trail:')
    trail_label.pack()
    trail_var = tk.IntVar(value=0)
    trail = tk.Scale(mass_menu, from_=0, to=1000, orient=tk.HORIZONTAL, variable=trail_var)
    trail.pack()


    # mass_menu.place(x=-1000, y=-1000)


    #=====================SPRING MENU=========================
    spring_menu = tk.Frame(canvas, highlightbackground='black', highlightthickness=1)
    spring_menu.place(x=10, y=130)

    spring_constant_label = tk.Label(spring_menu, text="Spring Constant:")
    spring_constant_label.pack()
    k_var = tk.IntVar()
    k = tk.Scale(spring_menu, from_=0, to=500, orient=tk.HORIZONTAL, variable=k_var)
    k.set(100)
    k.pack()

    damper_constant_label = tk.Label(spring_menu, text="Damper Constant:")
    damper_constant_label.pack()
    c_var = tk.IntVar()
    c = tk.Scale(spring_menu, from_=0, to=500, orient=tk.HORIZONTAL, variable=c_var)
    c.set(100)
    c.pack()

    use_eq_label = tk.Label(spring_menu, text='Manual Equilibrium\nLength:')
    use_eq_label.pack()
    use_eq_var = tk.IntVar()
    use_eq = tk.Checkbutton(spring_menu, variable=use_eq_var)
    use_eq.variable = use_eq_var
    use_eq.pack()

    equilibrium_length_label = tk.Label(spring_menu, text="Equilibrium Length:")
    equilibrium_length_label.pack()
    eq_var = tk.IntVar()
    eq = tk.Scale(spring_menu, from_=20, to=300, orient=tk.HORIZONTAL, variable=eq_var)
    eq.pack()

    spring_menu.place(x=-1000, y=-1000)


    #=====================COLLISION LINE MENU=========================
    line_menu = tk.Frame(canvas, highlightbackground='black', highlightthickness=1)
    line_menu.place(x=10, y=130)

    mu_label = tk.Label(line_menu, text="Mu:")
    mu_label.pack()
    mu_var = tk.StringVar()
    mu = tk.Scale(line_menu, from_=0, to=1, orient=tk.HORIZONTAL, variable=mu_var, resolution=0.1)
    mu.set(0.3)
    mu.pack()

    energy_label = tk.Label(line_menu, text="Energy Return:")
    energy_label.pack()
    energy_var = tk.StringVar()
    energy = tk.Scale(line_menu, from_=0, to=1, orient=tk.HORIZONTAL, variable=energy_var, resolution=0.1)
    energy.set(0.9)
    energy.pack()

    line_menu.place(x=-1000, y=-1000)

    update_func = lambda *args : update_selected(canvas, mode_value.get(), mass_menu, spring_menu, line_menu)
    mass_var.trace_add('write', update_func)
    static_var.trace_add('write', update_func)
    energy_return_var.trace_add('write', update_func)
    x_vel_var.trace_add('write', update_func)
    y_vel_var.trace_add('write', update_func)
    trail_var.trace_add('write', update_func)
    k_var.trace_add('write', update_func)
    c_var.trace_add('write', update_func)
    use_eq_var.trace_add('write', update_func)
    eq_var.trace_add('write', update_func)
    mu_var.trace_add('write', update_func)
    energy_var.trace_add('write', update_func)


    reset = tk.Button(canvas, text='Clear', command=lambda *args : reset_canvas(canvas, mode_value.get(), mass_menu, spring_menu, line_menu), height=1, width=10)
    reset.place(x=WIDTH-110, y=50)

    delete = tk.Button(canvas, text='Delete', command=lambda *args : delete_selected(canvas, mode_value.get(), mass_menu, spring_menu, line_menu), height=1, width=10)
    delete.place(x=-1000, y=-1000)
    # delete.place(x=WIDTH-110, y=50)


    global masses
    global springs
    global collision_shapes
    global walls

    global last_click
    global grey_line
    last_click = None
    grey_line = None

    global selected

    global pause_update
    pause_update = False    # this is to fix an issue with the syncing of values with the ui


    springs = []
    masses = []
    collision_shapes = []

    walls = (
        Static_Collision_Line(canvas, (0,0), (WIDTH,0), 0.3, 0.7),
        Static_Collision_Line(canvas, (0,0), (0,HEIGHT), 0.3, 0.7),
        Static_Collision_Line(canvas, (WIDTH,0), (WIDTH,HEIGHT), 0.3, 0.7),
        Static_Collision_Line(canvas, (0,HEIGHT), (WIDTH,HEIGHT), 0.3, 0.7)
    )
    collision_shapes += walls

    start = time()

    while True:

        energy = sum([x.mass*sqrt(x.x_vel**2 + x.y_vel**2) for x in masses])
        KE.configure(text = 'Total KE: ' + str(round(energy, 2)))
        
        try:
            root.state()
        except:
            break

        # canvas.update_idletasks()
        canvas.update()

        if paused:
            continue

        for spring in springs:
            spring.apply_forces()
        for mass in masses:
            # if gravity_var.get():
                # if mass.y + mass.radius < HEIGHT:
            mass.apply_force(0, gravity_var.get() * 600 * mass.mass)
        
        if walls_var.get():
            for shape in collision_shapes:
                shape.handle_collisions(masses)
        else:
            for shape in [x for x in collision_shapes if not x in walls]:
                shape.handle_collisions(masses)
        
        for i, mass in enumerate(masses):
            mass.handle_interparticle_forces(masses[i+1:], force_var.get())

        if collision_var.get():
            for i, mass in enumerate(masses):
                mass.handle_collisions(masses[i+1:])
        
        if selected and mode_value.get() == 'select':
            for mass in masses:
                if mass.id == selected:
                    pause_update = True
                    x_vel_var.set(str(mass.x_vel))
                    y_vel_var.set(str(mass.y_vel))
                    pause_update = False
            for spring in springs:
                if spring.id == selected and not use_eq_var.get():
                    pause_update = True
                    eq.set(spring.length)
                    pause_update = False
        
        for mass in masses:
            mass.move(timestep)
        for spring in springs:
            spring.move()

        end = time()
        if timestep > end - start:
            sleep(timestep - (end - start))
        start = time()

if __name__ == "__main__":
    main()