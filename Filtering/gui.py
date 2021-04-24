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
        self.wm_title("Endoplasmic Reticulum Morphology")
        self.currentPath = ""
        self.originalImages = []
        self.images = []
        self.slices = 3
        self.currentSlice = 0
        
        self.selectBtnLabel = tk.StringVar()
        self.selectBtnLabel.set("Select ER .tif")
        self.selectBtn = tk.Button(self.canvas, textvariable=self.selectBtnLabel, width=45, command=lambda: self.openDialog(self.selectBtn))
        self.selectBtn.pack(side=tk.TOP, padx=6, pady=2)
        
        self.sliceLoadSlider = Scale(self.canvas, from_=0, to=10, length=250, orient=HORIZONTAL)
        self.sliceLoadSlider.set(3)
        self.sliceLoadSlider.bind("<ButtonRelease-1>", self.setLoad)
        
        self.sliceSlider = Scale(self.canvas, from_=0, to=4, length=250, orient=HORIZONTAL)
        self.sliceSlider.set(0)
        self.sliceSlider.bind("<ButtonRelease-1>", self.setSlices)
        

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
    
    def initialize(self, path):
        originalImgs, imgs, fig = eigen.highlight_3D(path, self.slices, self.currentSlice)
        self.images = imgs
        self.originalImages = originalImgs
        self.currentPath = path
        
        self.figure = FigureCanvasTkAgg(fig, self)
        self.figure.draw()
        self.figure.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        self.selectBtnLabel.set("Select a different ER .tif")
        self.sliceSlider = Scale(self.canvas, from_=0, to=(len(self.images) - 1), length=250, orient=HORIZONTAL)
        self.sliceSlider.bind("<ButtonRelease-1>", self.setSlices)
        self.selectLoadLabel = tk.Label(self.canvas, text="Select # of slides to load (maximum - 10):")
        self.selectLoadLabel.pack()
        self.sliceLoadSlider.pack(padx=2, pady=4)
        self.selectLabel = tk.Label(self.canvas, text="Select slice to view:")
        self.selectLabel.pack()
        self.sliceSlider.pack(side=tk.BOTTOM, padx=2, pady=4)
        
    def execute(self, path):
        originalImgs, imgs, fig = eigen.highlight_3D(path, self.slices, self.currentSlice)
        self.images = imgs
        self.originalImages = originalImgs
        self.currentPath = path
        
        self.sliceSlider.configure(to=(len(self.images) - 1))
        
        self.figure = FigureCanvasTkAgg(fig, self)
        self.figure.draw()
        self.figure.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
    def setSlices(self, val):
        if self.sliceSlider.get() != self.currentSlice:
            self.figure.get_tk_widget().destroy()
            self.currentSlice = self.sliceSlider.get()
        
            if len(self.images) == 0:
                self.execute(self.currentPath)
        
            fig = eigen.getFig_3D(self.originalImages, self.images, self.currentSlice)
        
            self.figure = FigureCanvasTkAgg(fig, self)
            self.figure.draw()
            self.figure.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
            self.sliceSlider.pack(side=tk.BOTTOM, padx=2, pady=4)

ERGui().mainloop()
