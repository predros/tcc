import numpy as np
import tkinter as tk
from tkinter import Canvas
import math

def distance(x1, y1, x2, y2):
	return np.sqrt((x2-x1)*(x2-x1)+(y2-y1)*(y2-y1))

def distPointLine(xP, yP, x1, y1, x2, y2):
	if x1 == x2:
		return np.absolute(xP-x1)
	else:
		a = (y2-y1)/(x2-x1)
		c = y1 - a*x1
		return np.absolute((a*xP -yP + c)/np.sqrt(a*a+1))

def canvascoords(x, y, scale):
	offsetx = 300
	offsety = 300
	canvasx = (x+offsetx)*scale
	canvasy = (-y+offsety)*scale
	return [canvasx, canvasy]

def truecoords(canvasx, canvasy, scale):
	offsetx = 300
	offsety = 300
	x = canvasx/scale - offsetx
	y = -canvasy/scale + offsety
	return [x, y]

def shapeFunction(L, x, d1, d2, d3, d4, d5, d6):
	N1 = 1 - x/L
	N2 = 1 - 3*((x/L)**2) + 2*((x/L)**3)
	N3 = x - 2*(x**2)/L + (x**3)/(L**2)
	N4 = x/L
	N5 = 3*((x/L)**2) - 2*((x/L)**3)
	N6 = -(x**2)/L + (x**3)/(L**2)
	u = np.dot([N1, N4], [d1, d4])
	w = np.dot([N2, N3, N5, N6], [d2, d3, d5, d6])
	return [u, w]
