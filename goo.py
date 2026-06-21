from main import *

WIDTH = 500
HEIGHT = 700
MAX_GOO_DIS = 120
GOO_K = 250
GOO_C = 200
GOO_MASS = 1

paused = False
grey_lines = []

root = tk.Tk()
root.attributes('-type', 'dialog')              #This is for omarchy to not tile the window
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT)
root.geometry(str(WIDTH)+'x'+str(HEIGHT))
canvas.grid()

masses = []
springs = []

def play_pressed():
    global paused
    paused = not paused

def reset_canvas():
    global masses
    global springs
    global paused
    global canvas

    canvas.delete('all')

    masses = [
        Point(canvas, 200, 600, GOO_MASS),
        Point(canvas, 300, 600, GOO_MASS),
        Point(canvas, 250, 515, GOO_MASS)
    ]
    springs = [
        Spring(canvas, masses[0], masses[1], GOO_K, GOO_C),
        Spring(canvas, masses[1], masses[2], GOO_K, GOO_C),
        Spring(canvas, masses[0], masses[2], GOO_K, GOO_C)
    ]

    paused = False

    canvas.update_idletasks()
    canvas.update()

def handle_click(event):
    global masses
    global springs
    global canvas

    x = event.x
    y = event.y

    in_range_masses = []

    for mass in masses:
        dis = sqrt((mass.x - x)**2 + (mass.y - y)**2)
        if dis < MAX_GOO_DIS:
            in_range_masses.append(mass)
    
    if len(in_range_masses) < 2 or len(in_range_masses) > 3:
        return
    
    masses.append(Point(canvas, x, y, GOO_MASS))

    for mass in in_range_masses:
        springs.append(Spring(canvas, masses[-1], mass, GOO_K, GOO_C))

def handle_motion(event):
    global masses
    global canvas
    global grey_lines

    for line in grey_lines:
        canvas.delete(line)
    
    grey_lines = []
    
    x = event.x
    y = event.y

    in_range_masses = []

    for mass in masses:
        dis = sqrt((mass.x - x)**2 + (mass.y - y)**2)
        if dis < MAX_GOO_DIS:
            in_range_masses.append(mass)

    if len(in_range_masses) < 2 or len(in_range_masses) > 3:
        return

    grey_lines = [canvas.create_line(x, y, mass.x, mass.y, fill="grey", dash=(10,10), width=2) for mass in in_range_masses]
    
    canvas.update_idletasks()
    canvas.update()

def main():
    timestep = 0.005

    play = tk.Button(canvas, text='Play/Pause', command=play_pressed, width=10, height=1)
    play.place(x=10, y=10)

    canvas.bind("<Button-1>", handle_click)
    canvas.bind("<Motion>", handle_motion)

    reset = tk.Button(canvas, text='Reset', command=reset_canvas, height=1, width=10)
    reset.place(x=WIDTH-110, y=10)

    reset_canvas()

    while True:
        
        try:
            root.state()
        except:
            break

        canvas.update_idletasks()
        canvas.update()

        if paused:
            continue

        for spring in springs:
            spring.apply_forces()
        for mass in masses:

            #============GRAVITY=============
            if mass.y + mass.radius < HEIGHT:
                mass.apply_force(0, 250*mass.mass)

            if mass.y + mass.radius > HEIGHT:    
                mass.y_vel = mass.x_vel = 0
                mass.y = HEIGHT - mass.radius
            if mass.x + mass.radius > WIDTH:
                mass.x_vel = mass.y_vel = 0
                mass.x = WIDTH - mass.radius
            elif mass.x - mass.radius < 0:
                mass.x_vel = mass.y_vel = 0
                mass.x = mass.radius
            #================================

            mass.move(timestep)
        for spring in springs:
            spring.move()

        sleep(timestep)

if __name__ == "__main__":
    main()