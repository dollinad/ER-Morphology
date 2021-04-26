"""
Filename: gui2d.py
Authors: C. Way, D. Dodani, D. Lekovic, S. Ghorpade
Description: File containing graphical user interface for highlighting of 2D images
"""

# TKinter imports
import tkinter as tk
from tkinter import *
from tkinter.filedialog import askopenfilename

import eigen

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler

import numpy as np

"""
ERGui
    - Graphical user interface for 2D highlighting of ER
"""
class ERGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.canvas = tk.Canvas(self)
        self.canvas.pack()
        self.wm_title("Endoplasmic Reticulum Morphology (2D)")
        
        # Most recent filepath
        self.currentPath = ""
        
        # Current slice index
        self.currentSlice = 0
        
        # Current method being used
        self.method = "thresholds"
        
        # Button for selecting a .TIF file
        self.selectBtnLabel = tk.StringVar()
        self.selectBtnLabel.set("Select ER .tif")
        self.selectBtn = tk.Button(self.canvas, textvariable=self.selectBtnLabel, width=45, command=lambda: self.openDialog(self.selectBtn))
        self.selectBtn.pack(side=tk.TOP, padx=6, pady=2)
        
        # Slider for selecting slice index
        self.sliceSlider = Scale(self.canvas, from_=0, to=4, length=250, orient=HORIZONTAL)
        self.sliceSlider.set(0)
        self.sliceSlider.bind("<ButtonRelease-1>", self.setSlices)
        
    
    """
    openDialog(self, widget)
        - Opens a file dialogue for user to select TIF
    """
    def openDialog(self, widget):
        filename = askopenfilename()
        self.initialize(filename)
    
    """
    initialize(self, path)
        - Creates the first highlighted image environment
        - Creates first sliders
        - Draws figure
    """
    def initialize(self, path):
        # 2D highlighting occurs
        fig = eigen.highlight_2D(path, self.currentSlice)
        
        # Properties are updated
        self.currentPath = path
        
        # A figure is created to draw matplotlib figures on the screen
        self.figure = FigureCanvasTkAgg(fig, self)
        self.figure.draw()
        self.figure.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        # Button text is changed
        self.selectBtnLabel.set("Select a different ER .tif")
        
        # Slice slider can only select a slice that exists
        self.sliceSlider = Scale(self.canvas, from_=0, to=30, length=250, orient=HORIZONTAL)
        self.sliceSlider.bind("<ButtonRelease-1>", self.setSlices)
        
        self.selectLabel = tk.Label(self.canvas, text="Select slice to view:")
        self.selectLabel.pack()
        self.sliceSlider.pack(side=tk.BOTTOM, padx=2, pady=4)
    
    """
    initialize(self, path)
        - Creates the first highlighted image environment
        - Creates first sliders
        - Draws figure
    """
    def execute(self, path):
        # 2D highlighting occurs
        
        fig = eigen.highlight_2D(path, self.currentSlice)
                
        # Properties are updated
        self.currentPath = path
        
        # Slice slider max is updated
        self.sliceSlider.configure(to=30)
        
        # A figure is created to draw matplotlib figures on the screen
        self.figure.get_tk_widget().destroy()
        self.figure = FigureCanvasTkAgg(fig, self)
        self.figure.draw()
        self.figure.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    
    """
    setSlices(self, val)
        - Reloads everything based on slide load being changed
    """
    def setSlices(self, val):
        # If the slide selected is different than the one we are currently on
        if self.sliceSlider.get() != self.currentSlice:
            # Everything is erased
            self.currentSlice = self.sliceSlider.get()
            self.execute(self.currentPath)

ERGui().mainloop()
