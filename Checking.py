from tkinter import *
import os

root = Tk()
termf = Frame(root, height=400, width=500)

termf.pack(fill=BOTH, expand=YES)
wid = termf.winfo_id()
os.system(f'xterm -into %d -geometry {400}x{500} -sb &' % wid)

root.mainloop()