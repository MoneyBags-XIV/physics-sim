from main import *

def update_lengths(event, spring):
    if event.char == 'a':
        spring.eq_len = 150
    elif event.char == 'd':
        spring.eq_len = 100

def main():
    timestep = 0.005

    root = tk.Tk()
    root.attributes('-type', 'dialog')              #This is for omarchy to not tile the window
    canvas = tk.Canvas(root, width=500, height=500)

    masses = [
        Point(canvas, 100, 200, 1),
        Point(canvas, 200, 200, 1),
        Point(canvas, 140, 250, 1),
        Point(canvas, 400, 200, 1),
        Point(canvas, 400, 300, 1)
    ]
    springs = [
        Spring(canvas, masses[0], masses[1], 100, 100, 75),
        Spring(canvas, masses[1], masses[2], 100, 100, 75),
        Spring(canvas, masses[0], masses[2], 100, 100, 75),
        Spring(canvas, masses[-2], masses[-1], 100, 100)
    ]

    canvas.grid()

    root.bind('<Key>', lambda event : update_lengths(event, springs[-1]))

    while True:

        for spring in springs:
            spring.apply_forces()
        for mass in masses:

            #============GRAVITY=============
            if mass.y + mass.radius < 500:
                mass.apply_force(0, 250*mass.mass)
            else:
                mass.y_vel *= -0.3
                mass.x_vel *= 0.3
                mass.y = 500 - mass.radius
            #================================

            mass.move(timestep)
        for spring in springs:
            spring.move()
        #     print(spring.length)
        # print("\n")

        canvas.update_idletasks()
        canvas.update()

        sleep(timestep)

        # input("")

if __name__ == "__main__":
    main()