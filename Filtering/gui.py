import tkinter as tk
from tkinter import *
from tkinter.filedialog import askopenfilename
import eigen

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)

from matplotlib.backend_bases import key_press_handler

import numpy as np

class ERGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.canvas = tk.Canvas(self)
        self.canvas.pack()
        self.wm_title("Endoplasmic Reticulum Shape")
        self.currentPath = ""
        
        self.selectBtnLabel = tk.StringVar()
        self.selectBtnLabel.set("Select ER .tif")
        self.selectBtn = tk.Button(self.canvas, textvariable=self.selectBtnLabel, width=45, command=lambda: self.openDialog(self.selectBtn))
        self.selectBtn.pack(side=tk.TOP, padx=6, pady=2)
        
        self.pageSlider = Scale(self.canvas, from_=0, to=50, length=500, orient=HORIZONTAL)
        self.pageSlider.set(5)
        self.pageSlider.bind("<ButtonRelease-1>", self.changePage)
        

    def openDialog(self, widget):
        filename = askopenfilename()
        self.execute(filename)
    
    def execute(self, path, page=0):
        fig = eigen.highlight(path, page)
        self.currentPath = path
        
        self.figure = FigureCanvasTkAgg(fig, self)
        self.figure.draw()
        self.figure.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.selectBtnLabel.set("Select a different ER .tif")
        self.pageSlider.pack(side=tk.BOTTOM, padx=2, pady=2)
        
    def changePage(self, val):
        self.figure.get_tk_widget().destroy()
        self.execute(self.currentPath, self.pageSlider.get())
        

ERGui().mainloop()
