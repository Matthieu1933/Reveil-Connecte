import tkinter as tk
 
root = tk.Tk()
root.geometry("200x150")
 
label = tk.Label(root, text = "Hello World")
label.pack(padx = 5, pady = 5)
 
root.tk.call('tk', 'scaling', 2.0)
root.mainloop()