#list of imported modules
import tkinter
from tkinter import *
from math import cos, sin
from time import gmtime, sleep
import time
from datetime import datetime

# Horloge analogique
#defining of secondary functions
def drawcircle(Alpha,Beta,Rayon,Couleur,can): #draw a circle base on center coord radius and color
    x1,y1,x2,y2=Alpha-Rayon, Beta-Rayon, Alpha+Rayon, Beta+Rayon
    can.create_oval(x1,y1,x2,y2,fill=Couleur)

def drawPetAig(CoordA, CoordZ, Taille, Omega, can): #function to drawn the second hand of the clock
    Pi = 3.141592
    Omega = ((Omega/60)+1)*30
    can.create_line(CoordA + (Taille/3) * cos(Pi*(Omega/180)), CoordZ + (Taille/3) * sin(Pi*(Omega/180)), CoordA - (Taille/8) * cos(Pi*(Omega/180)), CoordZ - (Taille/8) * sin(Pi*(Omega/180)) )

def drawGrdAig(CoordA, CoordZ, Taille, Omega, can): #function to draw the minute hand, based on center coord and minutes.
    Pi = 3.141592
    Omega = (Omega-15)*6
    can.create_line(CoordA + (Taille/1.5) * cos(Pi*(Omega/180)), CoordZ + (Taille/1.5) * sin(Pi*(Omega/180)), CoordA - (Taille/6) * cos(Pi*(Omega/180)), CoordZ - (Taille/6) * sin(Pi*(Omega/180)))

def drawSecAig(CoordA, CoordZ, Taille, Omega, can): #function to draw the hour hand
    Pi = 3.141592
    Omega = (Omega-15) *6
    can.create_line(CoordA + (Taille/1.5) * cos(Pi*(Omega/180)), CoordZ + (Taille/1.5) * sin(Pi*(Omega/180)), CoordA - (Taille/6) * cos(Pi*(Omega/180)), CoordZ - (Taille/6) * sin(Pi*(Omega/180)), fill = "red")

def fondhorloge(CoordA, CoordZ, Taille, can1):  #function drawing the backgroud of the clock
    Pi = 3.141592
    drawcircle(CoordA, CoordZ, Taille + (Taille/10), "grey6",can1) #drawing the surrounding of the clock
    drawcircle(CoordA, CoordZ, Taille, "ivory3",can1)#backgroud
    drawcircle(CoordA, CoordZ, Taille/80, "grey6",can1)#central point/needle articulation
    can1.create_line(CoordA + (Taille - (Taille/15)), CoordZ, CoordA + (Taille - (Taille/5)), CoordZ) #drawing the N/S/E/W decorativ hour position
    can1.create_line(CoordA, CoordZ + (Taille - (Taille/15)), CoordA, CoordZ + (Taille - (Taille/5)))
    can1.create_line(CoordA - (Taille - (Taille/15)), CoordZ, CoordA - (Taille - (Taille/5)), CoordZ)
    can1.create_line(CoordA, CoordZ - (Taille - (Taille/15)), CoordA, CoordZ - (Taille - (Taille/5)))

    #here, this 4*2 line defined the position of the 8 intermediate line between the N/S/E/W decorativ line.
    can1.create_line(CoordA + (Taille/1.05) * cos(Pi*(30/180)), CoordZ + (Taille/1.05) * sin(Pi*(30/180)), CoordA + (Taille/1.20) * cos(Pi*(30/180)), CoordZ + (Taille/1.20) * sin(Pi*(30/180)))
    can1.create_line(CoordA + (Taille/1.05) * cos(Pi*(60/180)), CoordZ + (Taille/1.05) * sin(Pi*(60/180)), CoordA + (Taille/1.20) * cos(Pi*(60/180)), CoordZ + (Taille/1.20) * sin(Pi*(60/180)))

    can1.create_line(CoordA - (Taille/1.05) * cos(Pi*(30/180)), CoordZ - (Taille/1.05) * sin(Pi*(30/180)), CoordA - (Taille/1.20) * cos(Pi*(30/180)), CoordZ - (Taille/1.20) * sin(Pi*(30/180)))
    can1.create_line(CoordA - (Taille/1.05) * cos(Pi*(60/180)), CoordZ - (Taille/1.05) * sin(Pi*(60/180)), CoordA - (Taille/1.20) * cos(Pi*(60/180)), CoordZ - (Taille/1.20) * sin(Pi*(60/180)))

    can1.create_line(CoordA + (Taille/1.05) * cos(Pi*(30/180)), CoordZ - (Taille/1.05) * sin(Pi*(30/180)), CoordA + (Taille/1.20) * cos(Pi*(30/180)), CoordZ - (Taille/1.20) * sin(Pi*(30/180)))
    can1.create_line(CoordA + (Taille/1.05) * cos(Pi*(60/180)), CoordZ - (Taille/1.05) * sin(Pi*(60/180)), CoordA + (Taille/1.20) * cos(Pi*(60/180)), CoordZ - (Taille/1.20) * sin(Pi*(60/180)))

    can1.create_line(CoordA - (Taille/1.05) * cos(Pi*(30/180)), CoordZ + (Taille/1.05) * sin(Pi*(30/180)), CoordA - (Taille/1.20) * cos(Pi*(30/180)), CoordZ + (Taille/1.20) * sin(Pi*(30/180)))
    can1.create_line(CoordA - (Taille/1.05) * cos(Pi*(60/180)), CoordZ + (Taille/1.05) * sin(Pi*(60/180)), CoordA - (Taille/1.20) * cos(Pi*(60/180)), CoordZ + (Taille/1.20) * sin(Pi*(60/180)))


# Horloge digitale 
def tick(can):
    curtime = ''
    window_time = tkinter.Label(bg="white")
    window_date = tkinter.Label(bg="white")
    window_time.pack()
    window_date.pack()
# %d %m %y %H:%M:%S
    # today_time = datetime.today()
    now = datetime.now()
    mytime = now.strftime("%H:%M:%S")
    mydate = now.strftime("%a %b %Y")
    # newtime = datetime.strptime(today_time, '%b %d %H:%M:%S,%f')
    if mytime != curtime:
        curtime = mytime
        window_time.config(text=curtime, font=("Courier", 44))
        window_date.config(text=mydate, font=("Courier", 20))
    #window_time.after(200, tick)
    can.create_window(250, 390, window=window_time)
    can.create_window(250, 440, window=window_date)

def delete_canvas(can):
    can.delete("all")
    print('Hello')
    pass


#PRINCIPLE FUNCTION (here the problem starts)
def HORLOGE1(Gamma, Pi, Epsylon):# draw a clock with the center position x/x = gamma/pi and the radius = epsylon

    fondhorloge(Gamma, Pi, Epsylon, can1)# extracting time value
    patate = gmtime()
    heure = patate[3] + 1  # "+1" is changing time from english time to french time :P
    minute = patate[4]
    seconde = patate[5]

    print(heure, minute, seconde) # a simple test to watch what the programm is doing (run it, and you'll see, that this test is done tausend time per second, that why I think the problem is here.)
    drawPetAig(Gamma, Pi, Epsylon, heure, can1)
    drawGrdAig(Gamma, Pi, Epsylon, minute, can1)
    drawSecAig(Gamma, Pi, Epsylon, seconde, can1)

    #Test cadran digital
    tick(can1)
    #fen1.after(1000, HORLOGE1(250, 250, 200))
    fen1.after(1000, lambda: HORLOGE1(250, 180, 150))

#execution of the main function

fen1 = Tk()

can1 = Canvas(fen1, bg="white", height=500, width=500)
HORLOGE1(250, 180, 150)

box1 = Frame(fen1, bg="white")
button1 = tkinter.Button(box1, text ="Settings", font=("Courier", 20))
button1.pack(padx = 70, side = LEFT)
button2 = tkinter.Button(box1, text ="Suivant", font=("Courier", 20), action = delete_canvas(can1))
button2.pack(side = LEFT)

# can1.create_window(250, 390, window=box1)
can1.pack()

box1.pack(expand=True, fill="x", padx=5, pady=5, side = LEFT)


fen1.mainloop()
fen1.destroy()
