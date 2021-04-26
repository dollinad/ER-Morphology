"""
Filename: gui.py
Authors: C. Way, D. Dodani, D. Lekovic, S. Ghorpade
Description: File containing graphical user interface for highlighting of 3D images
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
    - Graphical user interface for 3D highlighting of ER
"""
class ERGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.canvas = tk.Canvas(self)
        self.canvas.pack()
        self.wm_title("Endoplasmic Reticulum Morphology")
        
        # Most recent filepath
        self.currentPath = ""
        
        # Original images
        self.originalImages = []
        
        # Modified images
        self.images = []
        
        # Slices to be loaded
        self.slices = 3
        
        # Current slice index
        self.currentSlice = 0

        
        self.method = "ratios"
        
        # Button for selecting a .TIF file
        self.selectBtnLabel = tk.StringVar()
        self.selectBtnLabel.set("Select ER .tif")
        self.selectBtn = tk.Button(self.canvas, textvariable=self.selectBtnLabel, width=45, command=lambda: self.openDialog(self.selectBtn))
        self.selectBtn.pack(side=tk.TOP, padx=6, pady=2)
        
        # Slider for selecting load amount
        self.sliceLoadSlider = Scale(self.canvas, from_=0, to=10, length=250, orient=HORIZONTAL)
        self.sliceLoadSlider.set(3)
        self.sliceLoadSlider.bind("<ButtonRelease-1>", self.setLoad)
        
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
        
        if len(self.images) == 0:
            self.initialize(filename)
        else:
            self.execute(filename)
    
    def setLoad(self, val):
        self.slices = self.sliceLoadSlider.get()
        self.figure.get_tk_widget().destroy()
        self.execute(self.currentPath)
    
    """
    initialize(self, path)
        - Creates the first highlighted image environment
        - Creates first sliders
        - Draws figure
    """
    def initialize(self, path):
        # 3D highlighting occurs
        originalImgs, imgs, fig = eigen.highlight_3D(path, self.method, self.slices, self.currentSlice)
        
        # Properties are updated
        self.images = imgs
        self.originalImages = originalImgs
        self.currentPath = path
        
        # A figure is created to draw matplotlib figures on the screen
        self.figure = FigureCanvasTkAgg(fig, self)
        self.figure.draw()
        self.figure.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        # Button text is changed
        self.selectBtnLabel.set("Select a different ER .tif")
        
        # Slice slider can only select a slice that exists
        self.sliceSlider = Scale(self.canvas, from_=0, to=(len(self.images) - 1), length=250, orient=HORIZONTAL)
        self.sliceSlider.bind("<ButtonRelease-1>", self.setSlices)
        
        self.selectLoadLabel = tk.Label(self.canvas, text="Select # of slides to load (maximum - 10):")
        self.selectLoadLabel.pack()
        self.sliceLoadSlider.pack(padx=2, pady=4)
        
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
        # 3D highlighting occurs
        originalImgs, imgs, fig = eigen.highlight_3D(path, self.method, self.slices, self.currentSlice)
        
        # Properties are updated
        self.images = imgs
        self.originalImages = originalImgs
        self.currentPath = path
        
        # Slice slider max is updated
        self.sliceSlider.configure(to=(len(self.images) - 1))
        
        # A figure is created to draw matplotlib figures on the screen
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
            self.figure.get_tk_widget().destroy()
            self.currentSlice = self.sliceSlider.get()
        
            if len(self.images) == 0:
                self.execute(self.currentPath)
            
            # New 3D highlighting occurs
            fig = eigen.getFig_3D(self.originalImages, self.images, self.currentSlice)
            
            # A figure is created to draw matplotlib figures on the screen
            self.figure = FigureCanvasTkAgg(fig, self)
            self.figure.draw()
            self.figure.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
            self.sliceSlider.pack(side=tk.BOTTOM, padx=2, pady=4)

ERGui().mainloop()
