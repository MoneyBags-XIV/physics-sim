'''
========== PSA ==========
I am aware that this code is kind of a hairball.
It started out as just a quick way to test the physics
in main, and so it was never designed for scalability.
At some point, I hope to refactor everything, especially
fixing up the menu system and the nightmarish mess of 
globals. But that would take so much energy from me, 
so maybe later. 



========== Projects to work on ==========
play/pause icons
preserve selection through undo/redo
out of bounds garbage collector
framerate indicator


'''


from main import *
from save import *
from time import time
from random import shuffle
from tkinter import ttk, filedialog as fd, Toplevel
from pickle import dump, load

WIDTH = 1000
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

    if mode.get() != '(1) select' or mode.get() == '(5) line':
        for spring in springs:
            if selected == spring.id:
                canvas.itemconfigure(selected, fill='black')
                selected = None
        for shape in collision_shapes:
            if selected == shape.id:
                canvas.itemconfigure(selected, fill='black')
                selected = None

    mass_menu.pack_forget()
    spring_menu.pack_forget()
    line_menu.pack_forget()
    delete.pack_forget()

    if mode.get() != '(5) line':
        if grey_line:
            canvas.delete(grey_line)
            grey_line = None
        if last_click:
            last_click = None

    if mode.get() == '(2) mass':
        mass_menu.pack()
        pause_update = True
        mass_menu.winfo_children()[6].variable.set('0')
        mass_menu.winfo_children()[8].variable.set('0')
        pause_update = False
 
    elif mode.get() == '(3) spring':
        spring_menu.pack()
    
    elif mode.get() == '(5) line':
        line_menu.pack()
    
    elif mode.get() == '(1) select':
        delete.place(x=WIDTH-110, y=90)
        
        if not selected:
            return
        
        for spring in springs:
            if spring.id == selected and not spring.rod:
                spring_menu.pack()
                pause_update = True
                spring_menu.winfo_children()[1].set(spring.k)
                spring_menu.winfo_children()[3].set(spring.c)
                spring_menu.winfo_children()[7].set(spring.eq_len)
                pause_update = False
                return
        
        for shape in collision_shapes:
            if shape.id == selected:
                line_menu.pack()
                pause_update = True
                line_menu.winfo_children()[1].set(shape.friction)
                line_menu.winfo_children()[3].set(shape.energy_return)
                pause_update = False
        
        for mass in masses:
            if mass.id == selected:
                mass_menu.pack()
                pause_update = True
                mass_menu.winfo_children()[1].set(mass.mass)
                mass_menu.winfo_children()[2].variable.set(mass.static)
                mass_menu.winfo_children()[4].set(mass.energy_return)
                mass_menu.winfo_children()[6].variable.set(str(mass.x_vel))
                mass_menu.winfo_children()[8].variable.set(str(mass.y_vel))
                mass_menu.winfo_children()[10].set(mass.trace)
                pause_update = False


def handle_click(event, mode, mass_menu, spring_menu, line_menu, root):

    global selected
    global masses
    global springs
    global collision_shapes
    global last_click
    global pause_update
    global snap
    global snap_lines
    global top

    try:
        top.destroy()
    except:
        pass

    root.focus()

    canvas = event.widget
    x = canvas.canvasx(event.x)
    y = canvas.canvasy(event.y)
    
    if mode.get() == '(2) mass':
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
        # update_undo_hist()
        return

    if mode.get() == '(5) line':
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
        # update_undo_hist()
        return

    overlapping = canvas.find_overlapping(x-10, y-10, x+10, y+10)
    # overlapping = [x for x in overlapping if not x in snap_lines]

    selectables = [x.id for x in collision_shapes + masses + springs]
    overlapping = [x for x in overlapping if x in selectables]

    if selected in overlapping and len(overlapping) == 1:
        return
    
    overlapping = [x for x in overlapping if x != selected]

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
        mass_menu.pack_forget()
        spring_menu.pack_forget()
        line_menu.pack_forget()
        return
    
    if mode.get() != '(1) select':
        for spring in springs:
            if spring.id == overlapping[0]:
                return
        for shape in collision_shapes:
            if shape.id == overlapping[0]:
                return
    
    if not selected or mode.get() == '(1) select':

        if mode.get() == '(1) select':
            mass_menu.pack_forget()
            spring_menu.pack_forget()
            line_menu.pack_forget()

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

        if mode.get() != '(1) select':
            return

        for spring in springs:
            if spring.id == selected:
                if spring.rod:
                    return
                spring_menu.pack()
                return
        for shape in collision_shapes:
            if shape.id == selected:
                line_menu.pack()
                return
        mass_menu.pack()
        return

    if mode.get() != '(1) select':
        point_a = None
        point_b = None

        for mass in masses:
            if mass.id == selected:
                point_a = mass
            if mass.id == overlapping[0]:
                point_b = mass

        if point_a == point_b:
            return
        
        if mode.get() == '(4) rod':
            springs.append(Rod(canvas, point_a, point_b))
        
        else:
            k = spring_menu.winfo_children()[1].get()
            c = spring_menu.winfo_children()[3].get()
            use_eq = spring_menu.winfo_children()[5].variable.get()
            eq = spring_menu.winfo_children()[7].get() if use_eq else 0
            
            springs.append(Spring(canvas, point_a, point_b, k, c, eq))

        canvas.itemconfigure(selected, fill='red')
        selected = None
        # update_undo_hist()

        return


def handle_motion(event, canvas):
    global last_click
    global grey_line

    global mouse_pos
    mouse_pos = (event.x, event.y)

    canvas.delete(grey_line)
    grey_line = None

    if not last_click:
        return
    
    grey_line = canvas.create_line(event.x, event.y, last_click[0], last_click[1], fill='grey')


def handle_drag(event, canvas, mode, timestep):
    if mode != '(1) select':
        return

    global selected
    global masses
    global dragged

    for mass in masses:
        if mass.id == selected:
            dragged = mass
            handle_motion(event, canvas)
            # delta_x = event.x - mass.x
            # delta_y = event.y - mass.y
            # mass.x_vel = delta_x/timestep
            # mass.y_vel = delta_y/timestep
            # mass.x = event.x
            # mass.y = event.y
            # mass.update_looks()
            return

def handle_release(event):
    global dragged
    if dragged:
        dragged = None


def handle_key_press(event, mode, mass_menu, spring_menu, line_menu, delete, x_vel, y_vel, root):

    key = event.char

    global canvas

    if event.keysym == "Escape" or event.keysym == "Return":
        root.focus()

    elif key == 'z':
        handle_undo()

    elif key == 'y':
        handle_redo()
    
    elif key == ' ':
        play_pressed()

    elif key == 's':
        save_to_file()
    
    # if x_vel['state'] == 'disabled' or y_vel['state'] == 'disabled':
    if root.focus_get() == x_vel or root.focus_get() == y_vel:
        return

    if key in ['1', '2', '3', '4', '5']:
        if key == '1':
            mode.set("(1) select")
        elif key == '2':
            mode.set("(2) mass")
        elif key == '3':
            mode.set("(3) spring")
        elif key == '4':
            mode.set("(4) rod")
        elif key == '5':
            mode.set("(5) line")
        change_mode(canvas, mode, mass_menu, spring_menu, line_menu, delete)


def update_dragged_mass(pos, old_pos, mode, timestep):
    global dragged
    global springs
    global paused
    if mode != '(1) select' or not dragged:
        return
    
    delta_x = pos[0] - old_pos[0]
    delta_y = pos[1] - old_pos[1]
    dragged.x = pos[0]
    dragged.y = pos[1]
    if not paused:
        if delta_x == 0 and delta_y == 0:
            dragged.x_vel *= 0.9
            dragged.y_vel *= 0.9
        else:
            dragged.x_vel = delta_x/timestep
            dragged.y_vel = delta_y/timestep
        dragged.x_force = 0
        dragged.y_force = 0
    else:
        dragged.update_looks()
    for spring in springs:
        if dragged == spring.point_a or dragged == spring.point_b:
            spring.move()   # this method really should be named update_looks
    
    # update_undo_hist()

def delete_selected(canvas, mode, mass_menu, spring_menu, line_menu):
    global selected
    global masses
    global springs
    global collision_shapes

    for i in range(4):
        if selected == collision_shapes[i].id:
            return

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
    if mode == '(1) select':
        mass_menu.pack_forget()
        spring_menu.pack_forget()
        line_menu.pack_forget()
    canvas.update_idletasks()
    # canvas.update()

    # update_undo_hist()


def update_selected(canvas, mode, mass_menu, spring_menu, line_menu):
    global pause_update
    
    if mode != '(1) select' or pause_update:
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
        # update_undo_hist()
        return
    
    elif is_shape:
        ans.friction = float(line_menu.winfo_children()[1].get())
        ans.energy_return = float(line_menu.winfo_children()[3].get())
        # update_undo_hist()
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
    # update_undo_hist()


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

    if mode == '(1) select':
        mass_menu.pack_forget()
        spring_menu.pack_forget()
        line_menu.pack_forget()

    canvas.delete('all')

    for shape in collision_shapes:
        shape.update_looks()
    
    update_grid()

    canvas.update_idletasks()
    # canvas.update()


def open_help_menu(root):

    global top

    top = Toplevel()
    top.geometry("400x" + str(HEIGHT-100))
    top.attributes('-type', 'dialog')
    top.title("Help")

    canvas = tk.Canvas(top, width=350, height=HEIGHT-120)
    canvas.place(x=25, y=10)

    scrollbar = tk.Scrollbar(top, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)

    frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=frame, anchor="nw")

    frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    title = ttk.Style()
    title.configure("Title.TLabel", font=("Helvetica", 20, "bold"))
    
    bold = ttk.Style()
    bold.configure("Bold.TLabel", font=("Helvetica", 12, "bold"))

    ttk.Label(frame, text="""Welcome to Physics Sim!""", style="Title.TLabel").pack()
    ttk.Label(frame, text="""
Physics Sim is a small project I have been working on to \
simulate simple physical interactions. \
These docs should help you get started. \
Please have fun messing around in this editor!

Check out the examples in the file dropdown \
to see what's possible. \
        """, wraplength=350).pack()

    ttk.Label(frame, text="\n\nMasses:", wraplength=350, style="Bold.TLabel").pack()
    ttk.Label(frame, text="""\
Everything in physics sim is based on masses. \
To place a mass, enter mass mode by selecting it in the \
left tray or by pressing 2 on the keyboard.

Masses have several properties which can be adjusted:

MASS -- This one is pretty self-explainatory. \
The size of mass is proportional to sqrt(mass), so the \
masses have a uniform 2d density.

STATIC -- When checked, this will prevent a mass from moving at all. \
Useful for anchoring springs or rods.

ENERGY RETURN -- This is a constant that controls how inelastic collisions involving this mass will be. \
Collision lines also have this property. In a collision, the product of the two energy return values \
is the ratio of energy that will be conserved.

X/Y VELOCITY -- The x and y velocity of the mass. Unitless.

LEAVE TRAIL -- The length of the trail that the mass will leave behind it. \
This has no effect on simulation, but can look really cool.
        """, wraplength=350).pack()

    ttk.Label(frame, text="\n\nSprings:", wraplength=350, style="Bold.TLabel").pack()
    ttk.Label(frame, text="""\
Springs connect between masses. To place springs, enter the spring menu by \
selecting it in the left tray of pressing 3, then select two masses.

You can adjust the following properties of a spring:

SPRING CONSTANT (K) -- This is the spring constant of the spring. The spring will apply forces based \
on this constant and its displacement from equilibrium.

DAMPING CONSTANT (C) -- Physics Sim uses non-ideal springs. This constant controls how much \
energy is lost in the motion of the spring. A value of 0 makes an ideal spring.

MANUAL EQUILIBRIUM LENGTH -- When checked, the springs equilibrium length can be set manually. \
When left unchecked, the spring will default to the distance between its two masses when it was created.
        """, wraplength=350).pack()
    
    ttk.Label(frame, text="\n\nRods:", wraplength=350, style="Bold.TLabel").pack()
    ttk.Label(frame, text="""\
Rods also connect masses to each other, but they are rigid. \
Place them by entering the rod menu by selecting it in the left \
tray or by pressing 4, then select two masses. 

Rods have no adjustable paramters, and will maintain their initial length. \
Under the hood, rods are springs with very high spring constants. \
This mean you may notice some displacement, especially under high forces.
        """, wraplength=350).pack()
    
    ttk.Label(frame, text="\n\nCollision Lines:", wraplength=350, style="Bold.TLabel").pack()
    ttk.Label(frame, text="""\
Collision lines are static lines that will collide with masses. \
To place them, enter the line menu by selecting it in the left tray or by \
pressing 5, then select two points on the screen. \
The walls of the area are also collision lines, and their properties \
can be adjusted.

Lines have two adjustable properties:

MU -- This is the coefficient of friction between this line and masses sliding on it.

ENERGY RETURN -- This is a constant that controls how inelastic collisions involving this line will be. \
Masses also have this property. In a collision, the product of the two energy return values \
is the ratio of energy that will be conserved.
        """, wraplength=350).pack()
    
    ttk.Label(frame, text="\n\nSelection Mode:", wraplength=350, style="Bold.TLabel").pack()
    ttk.Label(frame, text="""\
Enter selection mode by selecting it in the left tray or by pressing 1.

From this menu, you can select objects and adjust their properties or delete them. \
You can also click and drag to move masses around.
        """, wraplength=350).pack()
    
    ttk.Label(frame, text="\n\nOther Settings/Controls:", wraplength=350, style="Bold.TLabel").pack()
    ttk.Label(frame, text="""\
GRAVITY (DOWN) -- This controls the strength of gravity pulling masses downwards.

GRAVITY (BETWEEN BODIES) -- This controls the strength of gravity between masses, \
which can be used for orbital simulation and more.

SNAP TO GRID -- When checked, mass and line placement will be contrained to a grid.

WALLS -- Toggles whether the area is enclosed. 

PARTICLE COLLISIONS -- Toggles whether masses colide with eachother. Mass/line collisions are uneffected.

UNDO/REDO (Z/Y) -- Hitting z will undo, hitting y will redo.

SAVING/LOADING -- Simulations can be saved as a .phys file. Hit s to save, \
use the top bar to load.

PLAY/PAUSE (SPACE) -- Pressing the play/pause button or the space key will start or stop simulation. \
        """, wraplength=350).pack()


def update_grid():
    global snap
    global snap_lines
    global canvas
    if not snap.get():
        for line in snap_lines:
            canvas.delete(line)
        return
    for i in range((WIDTH//30) + 1):
        snap_lines.append(canvas.create_line(i*30, 0, i*30, HEIGHT, fill='grey'))
    for i in range((HEIGHT//30) + 1):
        snap_lines.append(canvas.create_line(0, i*30, WIDTH, i*30, fill='grey'))


def update_undo_hist(event):
    global undo_history
    global undo_index

    a = write_to_save()

    if not a.is_equal(undo_history[undo_index]):
        undo_history = undo_history if undo_index == -1 else undo_history[:undo_index+1]
        undo_history.append(a)
        undo_index = -1

    if len(undo_history) > 20:
        del undo_history[0]


def handle_undo():
    global undo_history
    global undo_index

    # if len(undo_history) < 2:
    #     return

    undo_index -= 1
    
    try:
        a = undo_history[undo_index]
    except:
        undo_index += 1
        return
    
    read_from_save(a)


def handle_redo():
    
    global undo_history
    global undo_index

    if undo_index == -1:
        return

    undo_index += 1
    read_from_save(undo_history[undo_index])


def write_to_save():
    global masses
    global springs
    global collision_shapes
    # global paused
    global gravity_var
    global force_var
    global snap
    global walls_var
    global collision_var

    return Save(masses, springs, collision_shapes, gravity_var.get(), force_var.get(), snap.get(), walls_var.get(), collision_var.get())

def read_from_save(save):
    global masses
    global springs
    global collision_shapes
    global gravity_var
    global force_var
    global snap
    global walls_var
    global collision_var

    global canvas

    global selected
    selected = None

    global undo_history
    global undo_index
    # undo_history = []
    # undo_index = -1

    # print(len(save.masses))
    # print(len(masses))

    save.refresh_canvas(canvas)

    masses, springs, collision_shapes = save.masses, save.springs, save.lines
    # masses = [copy(mass) for mass in save.masses]
    # springs = [copy(spring) for spring in save.springs]
    # collision_shapes = [copy(line) for line in save.lines]

    save.desync()

    gravity_var.set(save.gravity)
    snap.set(save.snap)
    walls_var.set(save.walls)
    force_var.set(save.force)
    collision_var.set(save.collisions)

    update_grid()

    update_undo_hist(None)


def save_to_file():
    file = fd.asksaveasfile(initialdir="saves", filetypes=[("Physics Sim Files", "*.phys"), ("All Files", "*.*")], defaultextension=".phys", mode='wb')
    if not file:
        return

    save_state = write_to_save()
    save_state.clear_canvas_refs()

    dump(save_state, file)

    file.close()

def load_from_file():
    file = fd.askopenfile(initialdir="saves", filetypes=[("Physics Sim Files", "*.phys"), ("All Files", "*.*")], mode='rb')
    ans = load(file)
    file.close()
    read_from_save(ans)

def open_example(name):
    with open("examples/" + name, 'rb') as file:
        ans = load(file)
    read_from_save(ans)

def main():

    timestep = 0.005

    root = tk.Tk()
    root.attributes('-type', 'dialog')              #This is for omarchy to not tile the window

    global canvas
    canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT)#, background='white')
    root.geometry(str(WIDTH + 200)+'x'+str(HEIGHT))

    canvas.place(x=200, y=0)

    tray = tk.Frame(root)#, highlightbackground='black', highlightthickness=1)#, width=200, height=HEIGHT)
    tray.place(x=0, y=0)

    menu_bar = tk.Menu(root)

    file = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="File", menu=file)
    file.add_command(label='Save', command=save_to_file)
    file.add_command(label='Load', command=load_from_file)

    # file.entryconfig(0, state=tk.DISABLED)

    file.add_separator()

    demos = tk.Menu(file, tearoff=0)
    file.add_cascade(label='Examples', menu=demos)
    demos.add_command(label='Simple Orbit', command=lambda *args : open_example("simple_orbit.phys"))
    demos.add_command(label='3 Body Orbit', command=lambda *args : open_example("3_body_orbit.phys"))
    demos.add_command(label='Simple Pendulum', command=lambda *args : open_example("pendulum.phys"))
    demos.add_command(label='Double Pendulum', command=lambda *args : open_example("double_pendulum.phys"))
    demos.add_command(label='Newton\'s Cradle', command=lambda *args : open_example("newtons_cradle.phys"))
    demos.add_command(label='Simple Springs.phys', command=lambda *args : open_example("simple_springs.phys"))
    demos.add_command(label='Gas Simulation', command=lambda *args : open_example("gas.phys"))
    demos.add_command(label='Liquid Simulation', command=lambda *args : open_example("liquid.phys"))
    demos.add_command(label='Marble Track', command=lambda *args : open_example("marbles.phys"))
    demos.add_command(label='Friction Demo', command=lambda *args : open_example("friction_spring.phys"))
    demos.add_command(label='Cannon', command=lambda *args : open_example("cannon.phys"))

    edit = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label='Edit', menu=edit)
    edit.add_command(label='Undo', command=handle_undo)
    edit.add_command(label='Redo', command=handle_redo)

    view = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label='View', menu=view)
    view.add_command()

    menu_bar.add_command(label="Help", command = lambda *args : open_help_menu(root))

    root.config(menu = menu_bar)

    play = tk.Button(canvas, text='Play/Pause', command=play_pressed, width=10, height=1)
    play.place(x=WIDTH-110, y=10)

    ttk.Separator(tray, orient=tk.HORIZONTAL).pack(fill=tk.X)

    modes = ['(1) select', '(2) mass', '(3) spring', '(4) rod', '(5) line']
    mode_value = tk.StringVar(canvas, value='(2) mass')
    mode_value.trace_add('write', lambda *args : change_mode(canvas, mode_value, mass_menu, spring_menu, line_menu, delete))
    # mode = tk.OptionMenu(canvas, mode_value, *modes)
    # mode.place(x=10, y=50)
    mode_frame = tk.Frame(tray)#canvas)#, highlightbackground='black', highlightthickness=1)
    mode_frame.pack()
    # mode_frame.place(x=10,y=10)

    for option in modes:
        ans = tk.Radiobutton(mode_frame, text=option, variable=mode_value, value=option)
        ans.pack()
    
    ttk.Separator(tray, orient=tk.HORIZONTAL).pack(fill=tk.X)

    gravity_frame = tk.Frame(tray)#, highlightbackground='black', highlightthickness=1)
    # gravity_frame.place(x=215, y=10)
    gravity_frame.pack()#side=tk.TOP)

    ttk.Separator(tray, orient=tk.HORIZONTAL).pack(fill=tk.X)

    gravity_label = tk.Label(gravity_frame, text='Gravity\n(down):')
    global gravity_var
    gravity_var = tk.IntVar(value=1)
    gravity = tk.Scale(gravity_frame, from_=0, to=5, orient=tk.HORIZONTAL, variable=gravity_var)
    gravity_label.grid(row=0, column=0)
    gravity.grid(row=0, column=1)
    # gravity_label.place(x=140, y=20)
    # gravity.place(x=250, y=10)

    force_label = tk.Label(gravity_frame, text='Gravity\n(between\nbodies):')
    global force_var
    force_var = tk.IntVar(value=0)
    force = tk.Scale(gravity_frame, from_=-10, to=10, orient=tk.HORIZONTAL, variable=force_var)
    force_label.grid(row=1, column=0)
    force.grid(row=1, column=1)
    # force_label.place(x=140, y=50)
    # force.place(x=250, y=50)

    KE = tk.Label(canvas, text='Total KE: 0')
    KE.place(x=WIDTH-120, y=HEIGHT-30)

    options = tk.Frame(tray)#, highlightbackground='black', highlightthickness=1)
    # options.place(x=80, y=10)
    options.pack()#side=tk.TOP)

    ttk.Separator(tray, orient=tk.HORIZONTAL).pack(fill=tk.X)

    global snap
    global snap_lines
    snap = tk.IntVar(value=0)
    snap_lines = []
    grid = tk.Checkbutton(options, text='Snap to grid', variable=snap, command=lambda *args : update_grid())
    grid.pack()
    # grid.place(x=100, y=90)

    global walls_var
    walls_var = tk.IntVar(value=1)
    use_walls = tk.Checkbutton(options, text='Walls', variable=walls_var)
    use_walls.pack()
    # use_walls.place(x=100, y=120)

    global collision_var
    collision_var = tk.IntVar(value=1)
    collision = tk.Checkbutton(options, text='Particle Collisions', variable=collision_var)
    collision.pack()
    # collision.place(x=100, y=150)

    canvas.bind("<Button-1>", lambda event : handle_click(event, mode_value, mass_menu, spring_menu, line_menu, root))
    canvas.bind("<Motion>", lambda event : handle_motion(event, canvas))
    canvas.bind("<B1-Motion>", lambda event : handle_drag(event, canvas, mode_value.get(), timestep))
    canvas.bind("<ButtonRelease-1>", handle_release)
    
    root.bind("<ButtonRelease-1>", update_undo_hist)


    #=====================MASS MENU=========================
    mass_menu = tk.Frame(tray)#, highlightbackground='black', highlightthickness=1)
    mass_menu.pack()

    mass_label = tk.Label(mass_menu, text="Mass:")
    mass_label.pack()
    mass_var = tk.IntVar(value=2)
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


    # mass_menu.pack_forget()


    #=====================SPRING MENU=========================
    spring_menu = tk.Frame(tray)#, highlightbackground='black', highlightthickness=1)
    spring_menu.pack()

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

    spring_menu.pack_forget()


    #=====================COLLISION LINE MENU=========================
    line_menu = tk.Frame(tray)#, highlightbackground='black', highlightthickness=1)
    line_menu.pack()

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

    line_menu.pack_forget()

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


    root.bind("<Key>", lambda event : handle_key_press(event, mode_value, mass_menu, spring_menu, line_menu, delete, x_vel, y_vel, root))

    reset = tk.Button(canvas, text='Clear', command=lambda *args : reset_canvas(canvas, mode_value.get(), mass_menu, spring_menu, line_menu), height=1, width=10)
    reset.place(x=WIDTH-110, y=50)

    delete = tk.Button(canvas, text='Delete', command=lambda *args : delete_selected(canvas, mode_value.get(), mass_menu, spring_menu, line_menu), height=1, width=10)
    delete.pack_forget()
    # delete.place(x=WIDTH-110, y=50)

    global undo_history
    global undo_index
    undo_index = -1

    global masses
    global springs
    global collision_shapes
    global walls

    global last_click
    global grey_line
    last_click = None
    grey_line = None

    global selected
    global dragged

    dragged = None

    global pause_update
    pause_update = False    # this is to fix an issue with the syncing of values with the ui

    global mouse_pos
    global old_mouse_pos
    mouse_pos = old_mouse_pos = (0,0)

    springs = []
    masses = []
    collision_shapes = []

    walls = (
        Static_Collision_Line(canvas, (1,1), (WIDTH,1), 0.3, 0.7),
        Static_Collision_Line(canvas, (1,1), (1,HEIGHT-1), 0.3, 0.7),
        Static_Collision_Line(canvas, (WIDTH,1), (WIDTH,HEIGHT-1), 0.3, 0.7),
        Static_Collision_Line(canvas, (1,HEIGHT-1), (WIDTH,HEIGHT-1), 0.3, 0.7)
    )
    collision_shapes += walls

    start = time()

    undo_history = [write_to_save()]


    while True:
        
        try:
            root.state()
        except:
            break

        # canvas.update_idletasks()
        canvas.update()

        update_dragged_mass(mouse_pos, old_mouse_pos, mode_value.get(), timestep)
        old_mouse_pos = mouse_pos

        for mass in masses:
            mass.handle_traces()

        if paused:
            sleep(timestep)
            continue
            
        energy = sum([x.mass*sqrt(x.x_vel**2 + x.y_vel**2) for x in masses])
        KE.configure(text = 'Total KE: ' + str(round(energy, 2)))

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
            for shape in collision_shapes[4:]: #[x for x in collision_shapes if not x in walls]:
                shape.handle_collisions(masses)
        
        for i, mass in enumerate(masses):
            mass.handle_interparticle_forces(masses[i+1:], force_var.get())

        if collision_var.get():
            for i, mass in enumerate(masses):
                mass.handle_collisions(masses[i+1:])
        
        if selected and mode_value.get() == '(1) select':
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
            if mass != dragged:
                mass.move(timestep)
            else:
                mass.update_looks()
        for spring in springs:
            spring.move()

        end = time()
        if timestep > end - start:
            sleep(timestep - (end - start))
        start = time()

if __name__ == "__main__":
    main()