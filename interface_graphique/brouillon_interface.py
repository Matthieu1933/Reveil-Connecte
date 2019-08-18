"""
Python in a Nutshell, 2nd Edition
By Alex Martelli
...............................................
Publisher: O'Reilly
Pub Date: July 2006
Print ISBN-10: 0-596-10046-9
Print ISBN-13: 978-0-59-610046-9
"""
import tkinter
import time
 
curtime = ''
clock = tkinter.Label( )
clock.pack( )
 
def tick( ):
    global curtime
    newtime = time.strftime('%H:%M:%S')
    if newtime != curtime:
        curtime = newtime
        clock.config(text=curtime)
    clock.after(200, tick)
tick( )
clock.mainloop( )