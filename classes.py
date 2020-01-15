import numpy as np
import tkinter as tk
from canvasfunctions import *
from tkinter import Canvas, Scrollbar, Frame, messagebox


class Node():
	def __init__(self, x, y):
		self.coords = [x, y]
		self.restr = [0, 0, 0]
		self.springs = [0, 0, 0]
		self.pdispl = [0, 0, 0]


	def setcoords(self, x, y):
		self.coords[0] = x
		self.coords[1] = y


	def setrestr(self, Rx, Ry, Rz, Kx, Ky, Kz, PDx, PDy, PDz):
		self.restr[0] = Rx
		self.restr[1] = Ry
		self.restr[2] = Rz
		self.springs[0] = Kx
		self.springs[1] = Ky
		self.springs[2] = Kz
		self.pdispl[0] = PDx
		self.pdispl[1] = PDy
		self.pdispl[2] = PDz



class Member():
	def __init__(self, start, end, material, section):
		self.nodes = [start, end]
		self.matname = material
		self.secname = section

	def setnodes(self, start, end):
		self.nodes[0] = start
		self.nodes[1] = end

	def setmaterial(self, material):
		self.matname = material

	def setsection(self, section):
		self.secname = section


class Material():
	def __init__(self, name, E, alpha):
		self.name = name
		self.E = E
		self.alpha = alpha

	def setprop(self, E, alpha):
		self.E = E
		self.alpha = alpha


class Section():
	def __init__(self, name, I, A, h, yg):
		self.name = name
		self.I = I
		self.A = A
		self.yg = yg
		self.ysup = h - yg
		self.h = h

	def setprop(self, I, A, h, yg):
		self.I = I
		self.A = A
		self.h = h
		self.yg = yg
		self.ysup = h - yg


class LoadCase():
	def __init__(self, name, NODES, MEMBERS):
		self.name = name
		self.Px = np.zeros(NODES)
		self.Py = np.zeros(NODES)
		self.Mz = np.zeros(NODES)
		self.qx = np.zeros(MEMBERS)
		self.qy = np.zeros(MEMBERS)
		self.Tsup = np.zeros(MEMBERS)
		self.Tinf = np.zeros(MEMBERS)
		self.prestr = np.zeros(MEMBERS)
		self.curv = np.zeros(MEMBERS)
	
	def newNode(self):
		self.Px = np.append(self.Px, 0)
		self.Py = np.append(self.Py, 0)
		self.Mz = np.append(self.Mz, 0)
	
	def delNode(self, i):
		np.delete(self.Px, i)
		np.delete(self.Py, i)
		np.delete(self.Mz, i)

	def newMember(self):
		self.qx = np.append(self.qx, 0)
		self.qy = np.append(self.qx, 0)
		self.Tsup = np.append(self.Tsup, 0)
		self.Tinf = np.append(self.Tinf, 0)
		self.prestr = np.append(self.prestr, 0)
		self.curv = np.append(self.curv, 0)

	def delMember(self, i):
		np.delete(self.qx, i)
		np.delete(self.qy, i)
		np.delete(self.Tsup, i)
		np.delete(self.Tinf, i)
		np.delete(self.prestr, i)
		np.delete(self.curv, i)

	def nodalForces(self, i, Px, Py, Mz):
		self.Px[i] = Px
		self.Py[i] = Py
		self.Mz[i] = Mz

	def memberLoads(self, i, qx, qy):
		self.qx[i] = qx
		self.qy[i] = qy

	def thermalLoads(self, Member, Tsup, Tinf):
		i = MEMBERS.index(Member)
		self.Tsup[i] = Tsup
		self.Tinf[i] = Tinf

	def prestrains(self, Member, prestr, curv):
		i = MEMBERS.index(Member)
		self.prestr[i] = prestr
		self.curv[i] = curv


class LoadCombination(): # Not yet implemented
	def __init__(self, LoadCases, factors, name):
		self.name = name
		self.Px = np.zeros(NODES)
		self.Py = np.zeros(NODES)
		self.Mz = np.zeros(NODES)
		self.qx = np.zeros(MEMBERS)
		self.qy = np.zeros(MEMBERS)
		self.Tsup = np.zeros(MEMBERS)
		self.Tinf = np.zeros(MEMBERS)
		self.prestr = np.zeros(MEMBERS)
		self.curv = np.zeros(MEMBERS)
		for case in Loadcases:
			i = Loadcases.index(case)
			self.Px += np.dot(case.Px, factors[i])
			self.Py += np.dot(case.Py, factors[i])
			self.Mz += np.dot(case.Py, factors[i])
			self.qx += np.dot(case.qx, factors[i])
			self.qy += np.dot(case.qy, factors[i])
			self.Tsup += np.dot(case.Tsup, factors[i])
			self.Tinf += np.dot(case.Tinf, factors[i])
			self.prestr += np.dot(case.prestr, factors[i])
			self.curv += np.dot(case.curv, factors[i])


class Tooltip():
    """
    create a tooltip for a given widget
    """
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     #miliseconds
        self.wraplength = 180   #pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 30
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left',
                       background="#ffffff", relief='solid', borderwidth=1,
                       wraplength = self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()


class MainCanvas():
	def __init__(self, master, width, height):
		# Parameters
		self.scale = 1.0
		self.item_tags = [None, -1]
		self.ClickType = 'select'
		self.memberCurrentNode = 'start'
		self.memberNodes = [-1, -1]
		self.currentMaterial = ''
		self.currentSection = ''
		self.restrictions = [0, 0, 0]
		self.pDisplacements = [0, 0, 0]
		self.springConstants = [0, 0, 0]
		self.nodalForces = [0, 0, 0]
		self.memberLoads = [0, 0]


		# Images
		self.img_nodecanvas = tk.PhotoImage(file="./img/canvas/img_nodecanvas.gif")
		self.img_nodeselected = tk.PhotoImage(file='./img/canvas/img_nodeselected.gif')
		
		self.img_rx = tk.PhotoImage(file='./img/canvas/img_rx.gif')
		self.img_ry = tk.PhotoImage(file='./img/canvas/img_ry.gif')
		self.img_rz = tk.PhotoImage(file='./img/canvas/img_rz.gif')
		self.img_rxy = tk.PhotoImage(file='./img/canvas/img_rxy.gif')
		self.img_rxz = tk.PhotoImage(file='./img/canvas/img_rxz.gif')
		self.img_ryz = tk.PhotoImage(file='./img/canvas/img_ryz.gif')
		self.img_rxyz = tk.PhotoImage(file='./img/canvas/img_rxyz.gif')

		self.img_kx = tk.PhotoImage(file='./img/canvas/img_kx.gif')
		self.img_ky = tk.PhotoImage(file='./img/canvas/img_ky.gif')

		# Container lists
		self.nodesList = []
		self.membersList = []
		self.materialsList = []
		self.sectionsList = []
		self.loadCasesList = []

		# Canvas definition
		self.frame=Frame(master,width=width,height=height)
		self.canvas=Canvas(self.frame,bg='white',width=width,height=height,scrollregion=(-10*width,-10*height,10*width,10*height))
		self.hbar=Scrollbar(self.frame,orient=tk.HORIZONTAL)
		self.hbar.config(command=self.canvas.xview)
		self.vbar=Scrollbar(self.frame,orient=tk.VERTICAL)
		self.vbar.config(command=self.canvas.yview)
		self.canvas.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)
		self.canvas.pack(fill=tk.BOTH, expand=True)

		# Key binding
		self.canvas.bind("<Key-Delete>", self.pressdel)
		self.canvas.bind("<ButtonPress-1>", self.onclick)		
		self.canvas.bind("<ButtonPress-3>", self.pan_start)
		self.canvas.bind("<B3-Motion>", self.pan_move)
		self.canvas.bind('<MouseWheel>', self.zoom)
		self.canvas.focus_set()

	def redraw(self):
		'''
		Redraws the whole canvas
		'''
		self.canvas.delete('all')
		for i in range(len(self.nodesList)):
			p = canvascoords(self.nodesList[i].coords[0], self.nodesList[i].coords[1], self.scale)
			x = p[0]
			y = p[1]
			if self.item_tags[0] == 'Node' and self.item_tags[1] == str(i):
				self.canvas.create_image(x, y, image=self.img_nodeselected, tags = ('Node', i))
			else:
				self.canvas.create_image(x, y, image=self.img_nodecanvas, tags = ('Node', i))

			# Support conditions
			rx = self.nodesList[i].restr[0]
			ry = self.nodesList[i].restr[1]
			rz = self.nodesList[i].restr[2]
			if rx == 1:
				if ry == 1:
					if rz == 1:
						self.canvas.create_image(x, y, image=self.img_rxyz, anchor=tk.N, tags = ('Node', i))
					else:
						self.canvas.create_image(x, y, image=self.img_rxy, anchor=tk.N, tags = ('Node', i))
				elif rz == 1:
					self.canvas.create_image(x, y, image=self.img_rxz, anchor=tk.E, tags = ('Node', i))
				else:
					self.canvas.create_image(x, y, image=self.img_rx, anchor=tk.E, tags = ('Node', i))
			else:
				if ry == 1:
					if rz == 1:
						self.canvas.create_image(x, y, image=self.img_ryz, anchor=tk.N, tags = ('Node', i))
					else:
						self.canvas.create_image(x, y, image=self.img_ry, anchor=tk.N, tags = ('Node', i))
				elif rz == 1:
					self.canvas.create_image(x, y, image=self.img_rz, anchor=tk.CENTE, tags = ('Node', i))
			
			# Springs
			kx = self.nodesList[i].springs[0]
			ky = self.nodesList[i].springs[1]
			kz = self.nodesList[i].springs[2]

			if kx != 0:
				string = 'KX = ' + str(kx)
				self.canvas.create_image(x, y, image=self.img_kx, anchor=tk.E, tags = ('Node', i))
				self.canvas.create_text(x-20*self.scale, y-15*self.scale, text=string)
			if ky != 0:
				string = 'KY = ' + str(ky)
				self.canvas.create_image(x, y, image=self.img_ky, anchor=tk.N)
				self.canvas.create_text(x-15*self.scale, y+20*self.scale, text=string, justify=tk.RIGHT, tags = ('Node', i))

			# Nodal forces
			Px = self.loadCasesList[0].Px[i]
			Py = self.loadCasesList[0].Py[i]
			Mz = self.loadCasesList[0].Mz[i]
			string = ''
			if Px > 0:
				string = 'PX = ' + str(Px)
				self.canvas.create_line(x, y, x+15*self.scale, y, arrow=tk.LAST)
				self.canvas.create_text(x+7.5*self.scale, y-3*self.scale, text=string)
			elif Px < 0:
				string = 'PX = ' + str(-Px)
				self.canvas.create_line(x-15*self.scale, y, x, y, arrow=tk.LAST)
				self.canvas.create_text(x-7.5*self.scale, y-3*self.scale, text=string)
			if Py > 0:
				string = 'PY = ' + str(Py)
				self.canvas.create_line(x, y, x, y-15*self.scale, arrow=tk.LAST)
				self.canvas.create_text(x-5*self.scale, y-18*self.scale, text=string)
			elif Py < 0:
				string = 'PY = ' + str(-Py)
				self.canvas.create_line(x, y-15*self.scale, x, y, arrow=tk.LAST)
				self.canvas.create_text(x-5*self.scale, y-18*self.scale, text=string)
			if Mz != 0:
				string = string + 'MZ = ' + str(Mz)
				self.canvas.create_text(x, y-15*self.scale, text=string)

		for i in range(len(self.membersList)):
			start = int(self.membersList[i].nodes[0])
			end = int(self.membersList[i].nodes[1])
			p1 = canvascoords(self.nodesList[start].coords[0], self.nodesList[start].coords[1], self.scale)
			x1 = p1[0]
			y1 = p1[1]
			p2 = canvascoords(self.nodesList[end].coords[0], self.nodesList[end].coords[1], self.scale)
			x2 = p2[0]
			y2 = p2[1]
			if x2 == x1: theta = np.pi/2
			else: theta = np.arctan((y2-y1)/(x2-x1))
			x = (x1+x2)/2
			y = (y1+y2)/2
			if self.item_tags[0] == 'Member' and self.item_tags[1] == str(i):
				self.canvas.create_line(x1, y1, x2, y2, width=2, fill='green4', tags = ('Member', i))
			else:
				self.canvas.create_line(x1, y1, x2, y2, width=2, fill='gray25', tags = ('Member', i))
			qx = self.loadCasesList[0].qx[i]
			qy = self.loadCasesList[0].qy[i]
			string = ''
			if qx != 0:
				string = string + 'qx = ' + str(qx) + ' '
			if qy != 0:
				string = string + 'qy = ' + str(qy)
			self.canvas.create_text(x, y-15, text=string, angle=-np.degrees(theta))
		return

	def onclick(self, event):
		'''
		Defines what happens after LMB clicks on the canvas.
		'''
		self.canvas.focus_set()
		mx = self.canvas.canvasx(event.x)
		my = self.canvas.canvasy(event.y)
		itemtags = []
		if self.ClickType == 'results':
			return

		if not self.canvas.find_all():
			itemtags = ['Empty', -1]
		else:
			item = self.canvas.find_closest(mx, my)
			item_type = self.canvas.type(item)
			itemtags = self.canvas.gettags(item)
			c = self.canvas.coords(item)
		
		if itemtags[0] == 'Empty' or len(itemtags)==0:
			itemtags = ['Empty', -1]
			if self.ClickType == 'node':
				self.newnode(mx, my)
				self.redraw()
				return

			elif self.ClickType == 'member':
				if self.memberCurrentNode == 'start':
					self.newnode(mx, my)
					self.memberNodes[0] = len(self.nodesList)-1
					self.memberCurrentNode = 'end'
					self.redraw()
					return
				elif self.memberCurrentNode == 'end':
					self.newnode(mx, my)
					self.memberNodes[1] = len(self.nodesList)-1
					self.newmember(self.memberNodes[0], self.memberNodes[1], self.currentMaterial, self.currentSection)
					self.memberNodes = [-1, -1]
					self.membercurrentnode = 'start'		
					self.redraw()
					return

		elif itemtags[0] == 'Node':
			d = distance(mx, my, c[0], c[1])
			
			if self.ClickType == 'select':
				if d <= 5: self.item_tags = itemtags
				else: self.item_tags = [None, -1]
				self.redraw()
				return

			elif self.ClickType == 'node':
				self.newnode(mx, my)
				self.redraw()
				return
			
			elif self.ClickType == 'member':
				if self.memberCurrentNode == 'start':
					if d < 8:
						self.memberNodes[0] = itemtags[1]
						self.memberCurrentNode = 'end'
						return
					else:
						self.newnode(mx, my)
						self.memberNodes[0] = len(self.nodesList)-1
						self.memberCurrentNode = 'end'
						self.redraw()
						return
				elif self.memberCurrentNode == 'end':
					if d < 8:
						self.memberNodes[1] = itemtags[1]
						self.memberCurrentNode = 'start'
						self.newmember(self.memberNodes[0], self.memberNodes[1], self.currentMaterial, self.currentSection)
						self.memberNodes = [-1, -1]
						self.membercurrentnode = 'start'
						self.redraw()
						return
					else:
						self.newnode(mx, my)
						self.memberNodes[1] = len(self.nodesList)-1
						self.newmember(self.memberNodes[0], self.memberNodes[1], self.currentMaterial, self.currentSection)
						self.memberNodes = [-1, -1]
						self.membercurrentnode = 'start'		
						self.redraw()
						return

			elif self.ClickType == 'support' and d < 8:
				i = int(itemtags[1])
				self.nodesList[i].setrestr(self.restrictions[0], self.restrictions[1], self.restrictions[2],
											self.springConstants[0], self.springConstants[1], self.springConstants[2],
											self.pDisplacements[0], self.pDisplacements[1], self.pDisplacements[2])
				self.redraw()
				return

			elif self.ClickType == 'nodalforces' and d < 8:
				i = int(itemtags[1])
				self.loadCasesList[0].nodalForces(i, self.nodalForces[0], self.nodalForces[1], self.nodalForces[2])
				self.redraw()
				return

		elif itemtags[0] == 'Member':
			d = distPointLine(mx, my, c[0], c[1], c[2], c[3])

			if self.ClickType == 'select':
				if d < 8:
					self.item_tags = itemtags
				else:
					self.item_tags = [None, -1]
				self.redraw()
				return
			elif self.ClickType == 'member':
				if d < 8:
					self.item_tags = itemtags
					i = int(itemtags[1])
					self.membersList[i].matname = self.currentMaterial
					self.membersList[i].secname = self.currentSection
					self.redraw()
				return

			elif self.ClickType == 'memberloads' and d < 8:
				i = int(itemtags[1])
				self.loadCasesList[0].memberLoads(i, self.memberLoads[0], self.memberLoads[1])
				self.redraw()
				return
		else: return

	def pressdel(self, event):
		'''
		Defines what happens when pressing the 'Delete' key.
		'''
		i = int(self.item_tags[1])
		if self.item_tags[0] == 'Node':
			self.nodesList.pop(i)
			for loadcase in self.loadCasesList:
				loadcase.delNode(i)
			for member in self.membersList:
				if i in member.nodes:
					n = self.membersList.index(member)
					self.membersList.pop(n)
					for loadcase in self.loadCasesList:
						loadcase.delMember(n)
		elif self.item_tags[0] == 'Member':
			self.membersList.pop(i)
			for loadcase in self.loadCasesList:
				loadcase.delMember(i)
		self.item_tags = [None, -1]
		self.redraw()

	def newnode(self, mx, my):
		'''
		Adds a new node at the current mouse position
		'''
		p = truecoords(mx, my, self.scale)
		n = Node(p[0], p[1])
		self.nodesList.append(n)
		for loadcase in self.loadCasesList:
			loadcase.newNode()
		self.redraw()
		return

	def newmember(self, start, end, material, section):
		if start == end:
			messagebox.showwarning('Erro', 'Selecione pontos diferentes para início e fim da barra.')
			return
		elif not material:
			messagebox.showwarning('Erro', 'Selecione um material.')
			return
		elif not section:
			messagebox.showwarning('Erro', 'Selecione uma seção.')
			return
		else:
			n = [start, end]
			for i in range(len(self.membersList)):
				if sorted(n) == sorted(self.membersList[i].nodes):
					messagebox.showwarning('Erro', 'Já existe uma barra nos pontos indicados.')
					return
			else:
				m = Member(int(start), int(end), material, section)
				self.membersList.append(m)
				for loadcase in self.loadCasesList:
					loadcase.newMember()
				self.redraw()
				return

	def pan_start(self, event):
		'''
		Marks the current mouse position as anchor for movement.
		'''
		self.canvas.focus_set()
		self.canvas.scan_mark(event.x, event.y)

	def pan_move(self, event):
		'''
		Pans the canvas using mouse movement.
		'''
		self.canvas.focus_set()
		self.canvas.scan_dragto(event.x, event.y, gain=1)

	def zoom(self, event):
		'''
		Zoom into canvas with mouse wheel
		'''
		s = 1.0
		if event.delta < 0: f = 0.95
		if event.delta > 0: f = 1.05
		self.scale *= f
		s *= f
		x = self.canvas.canvasx(event.x)
		y = self.canvas.canvasy(event.y)
		self.canvas.scale('all', x, y, s, s)

	def drawDeformed(self, results):
		'''
		Draws the deformed shape of the structure.
		'''
		self.canvas.delete('all')

		for member in self.membersList:
			start = member.nodes[0]
			end = member.nodes[1]

			x1 = self.nodesList[start].coords[0]
			y1 = self.nodesList[start].coords[1]
			x2 = self.nodesList[end].coords[0]
			y2 = self.nodesList[end].coords[1] 

			dG = [results[0][start], results[1][start], results[2][start], results[0][end], results[1][end], results[2][end]]

			L = distance(x1, y1, x2, y2)
			if x2 == x1 and y2 > y1: theta = np.pi/2
			elif x2 == x1 and y1 > y2: theta = -np.pi/2
			else: theta = np.arctan((y2-y1)/(x2-x1))
			cos = np.cos(theta)
			sin = np.sin(theta)

			dL = [dG[0]*cos+dG[1]*sin, dG[1]*cos-dG[0]*sin, dG[2], dG[3]*cos+dG[4]*sin, dG[4]*cos-dG[3]*sin, dG[5]]
			p1 = canvascoords(x1, y1, self.scale)
			p2 = canvascoords(x2, y2, self.scale)
			p1p = canvascoords(x1+dG[0], y1+dG[1], self.scale)
			p2p = canvascoords(x2+dG[3], y2+dG[4], self.scale)
			xy = [p1p[0], p1p[1]]
			for i in range(1, 200):
				xP = x1 + i*L*np.cos(theta)/200
				yP = y1 + i*L*np.sin(theta)/200
				xL = i*L/200
				sL = shapeFunction(L, xL, dL[0], dL[1], dL[2], dL[3], dL[4], dL[5])
				sG = [sL[0]*cos-sL[1]*sin, sL[1]*cos+sL[0]*sin]
				p = canvascoords(xP+sG[0], yP+sG[1], self.scale)
				xy.append(p[0])
				xy.append(p[1])
			xy.append(p2p[0])
			xy.append(p2p[1])
			self.canvas.create_line(xy, fill='gray60', width=1.2)
			self.canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill='gray25', width=2)

		for i in range(len(self.nodesList)):
			x = self.nodesList[i].coords[0]
			y = self.nodesList[i].coords[1]
			p = canvascoords(x, y, self.scale)
			x = p[0]
			y = p[1]
			self.canvas.create_image(x, y, image=self.img_nodecanvas, tags = ('Node', i))

			# Support conditions
			rx = self.nodesList[i].restr[0]
			ry = self.nodesList[i].restr[1]
			rz = self.nodesList[i].restr[2]
			kx = self.nodesList[i].springs[0]
			ky = self.nodesList[i].springs[1]
			kz = self.nodesList[i].springs[2]

			if rx == 1:
				if ry == 1:
					if rz == 1:
						self.canvas.create_image(x, y, image=self.img_rxyz, anchor=tk.N)
					else:
						self.canvas.create_image(x, y, image=self.img_rxy, anchor=tk.N)
				elif rz == 1:
					self.canvas.create_image(x, y, image=self.img_rxz, anchor=tk.E)
				else:
					self.canvas.create_image(x, y, image=self.img_rx, anchor=tk.E)
			else:
				if ry == 1:
					if rz == 1:
						self.canvas.create_image(x, y, image=self.img_ryz, anchor=tk.N)
					else:
						self.canvas.create_image(x, y, image=self.img_ry, anchor=tk.N)
				elif rz == 1:
					self.canvas.create_image(x, y, image=self.img_rz, anchor=tk.CENTER)

			if kx != 0:
				self.canvas.create_image(x, y, image=self.img_kx, anchor=tk.E)
			if ky != 0:
				self.canvas.create_image(x, y, image=self.img_ky, anchor=tk.N)
		return

	def drawBending(self, results):
		'''
		Draws the bending moment diagram for the structure.
		'''
		self.canvas.delete('all')

		for member in self.membersList:
			start = member.nodes[0]
			end = member.nodes[1]
			i = self.membersList.index(member)
			f = 0.01

			x1 = self.nodesList[start].coords[0]
			y1 = self.nodesList[start].coords[1]
			x2 = self.nodesList[end].coords[0]
			y2 = self.nodesList[end].coords[1]

			p1 = canvascoords(x1, y1, self.scale)
			p2 = canvascoords(x2, y2, self.scale)

			M = [-results[3][i][2], results[3][i][5]]
			V = results[3][i][1]
			q = self.loadCasesList[0].qy[i]
			if q != 0: xmax = -V/q
			else: xmax = 0
			L = distance(x1, y1, x2, y2)
			if x2 == x1 and y2 > y1: theta = np.pi/2
			elif x2 == x1 and y1 > y2: theta = -np.pi/2
			else: theta = np.arctan((y2-y1)/(x2-x1))
			cos = np.cos(theta)
			sin = np.sin(theta)

			p1m = canvascoords(x1-f*(-M[0])*sin, y1+f*(-M[0])*cos, self.scale)
			p2m = canvascoords(x2-f*(-M[1])*sin, y2+f*(-M[1])*cos, self.scale)

			xy = [p1m[0], p1m[1]]
			for i in range(1, 200):
				xP = x1 + i*L*cos/200
				yP = y1 + i*L*sin/200
				xL = i*L/200
				Mx = M[0] + q*xL*xL/2 + V*xL
				p = canvascoords(xP-f*(-Mx)*sin, yP+f*(-Mx)*cos, self.scale)
				if xL > xmax-L/200 and xL < xmax + L/200:
					xyP = canvascoords(xP, yP, self.scale)
					self.canvas.create_line(xyP[0], xyP[1], p[0], p[1], fill='green')
					self.canvas.create_text(p[0], p[1]+15*self.scale, text=str(Mx), fill='green')
				xy.append(p[0])
				xy.append(p[1])
			xy.append(p2m[0])
			xy.append(p2m[1])
			if np.absolute(M[0]) > 0.0001: 
				self.canvas.create_line(p1[0], p1[1], p1m[0], p1m[1], fill='green')
				self.canvas.create_text(p1m[0], p1m[1]+15*self.scale, text='{:.2f}'.format(np.absolute(M[0])), fill='green')
			self.canvas.create_line(xy, fill='green')
			if np.absolute(M[1]) > 0.0001:
				self.canvas.create_line(p2[0], p2[1], p2m[0], p2m[1], fill='green')
				self.canvas.create_text(p2m[0], p2m[1]+15*self.scale, text='{:.2f}'.format(np.absolute(M[1])), fill='green')
			self.canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill='gray25')

		for i in range(len(self.nodesList)):
			x = self.nodesList[i].coords[0]
			y = self.nodesList[i].coords[1]
			p = canvascoords(x, y, self.scale)
			x = p[0]
			y = p[1]
			self.canvas.create_image(x, y, image=self.img_nodecanvas, tags = ('Node', i))

		return

	def drawShear(self, results):
		'''
		Draws the shearing force diagram for the structure.
		'''
		self.canvas.delete('all')

		for member in self.membersList:
			start = member.nodes[0]
			end = member.nodes[1]
			i = self.membersList.index(member)
			f = 1.0

			x1 = self.nodesList[start].coords[0]
			y1 = self.nodesList[start].coords[1]
			x2 = self.nodesList[end].coords[0]
			y2 = self.nodesList[end].coords[1]

			p1 = canvascoords(x1, y1, self.scale)
			p2 = canvascoords(x2, y2, self.scale)

			V = [results[3][i][1], -results[3][i][4]]
			q = self.loadCasesList[0].qy[i]

			L = distance(x1, y1, x2, y2)
			if x2 == x1 and y2 > y1: theta = np.pi/2
			elif x2 == x1 and y1 > y2: theta = -np.pi/2
			else: theta = np.arctan((y2-y1)/(x2-x1))
			cos = np.cos(theta)
			sin = np.sin(theta)

			p1m = canvascoords(x1-f*(V[0])*sin, y1+f*(V[0])*cos, self.scale)
			p2m = canvascoords(x2-f*(V[1])*sin, y2+f*(V[1])*cos, self.scale)

			xy = [p1m[0], p1m[1]]
			for i in range(1, 200):
				xP = x1 + i*L*cos/200
				yP = y1 + i*L*sin/200
				xL = i*L/200
				Vx = V[0] + q*xL
				p = canvascoords(xP-f*(Vx)*sin, yP+f*(Vx)*cos, self.scale)
				xy.append(p[0])
				xy.append(p[1])
			xy.append(p2m[0])
			xy.append(p2m[1])
			if np.absolute(V[0]) > 0.0001: 
				self.canvas.create_line(p1[0], p1[1], p1m[0], p1m[1], fill='red')
				self.canvas.create_text(p1m[0], p1m[1]+15*self.scale, text='{:.2f}'.format(V[0]), fill='red')
			self.canvas.create_line(xy, fill='red')
			if np.absolute(V[1]) > 0.0001:
				self.canvas.create_line(p2[0], p2[1], p2m[0], p2m[1], fill='red')
				self.canvas.create_text(p2m[0], p2m[1]+15*self.scale, text='{:.2f}'.format(V[1]), fill='red')
			self.canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill='gray25', width=2)

		for i in range(len(self.nodesList)):
			x = self.nodesList[i].coords[0]
			y = self.nodesList[i].coords[1]
			p = canvascoords(x, y, self.scale)
			x = p[0]
			y = p[1]
			self.canvas.create_image(x, y, image=self.img_nodecanvas, tags = ('Node', i))
		return

	def drawNormal(self, results):
		'''
		Draws the normal force diagram for the structure.
		'''
		self.canvas.delete('all')

		for member in self.membersList:
			start = member.nodes[0]
			end = member.nodes[1]
			i = self.membersList.index(member)
			f = 1.0

			x1 = self.nodesList[start].coords[0]
			y1 = self.nodesList[start].coords[1]
			x2 = self.nodesList[end].coords[0]
			y2 = self.nodesList[end].coords[1]

			p1 = canvascoords(x1, y1, self.scale)
			p2 = canvascoords(x2, y2, self.scale)

			N = [-results[3][i][0], results[3][i][3]]
			q = self.loadCasesList[0].qx[i]

			L = distance(x1, y1, x2, y2)
			if x2 == x1 and y2 > y1: theta = np.pi/2
			elif x2 == x1 and y1 > y2: theta = -np.pi/2
			else: theta = np.arctan((y2-y1)/(x2-x1))
			cos = np.cos(theta)
			sin = np.sin(theta)

			p1m = canvascoords(x1-f*(N[0])*sin, y1+f*(N[0])*cos, self.scale)
			p2m = canvascoords(x2-f*(N[1])*sin, y2+f*(N[1])*cos, self.scale)

			xy = [p1m[0], p1m[1]]
			for i in range(1, 200):
				xP = x1 + i*L*cos/200
				yP = y1 + i*L*sin/200
				xL = i*L/200
				Nx = N[0] + q*xL
				p = canvascoords(xP-f*(Nx)*sin, yP+f*(Nx)*cos, self.scale)
				xy.append(p[0])
				xy.append(p[1])
			xy.append(p2m[0])
			xy.append(p2m[1])
			if np.absolute(N[0]) > 0.0001:
				self.canvas.create_line(p1[0], p1[1], p1m[0], p1m[1], fill='blue')
				self.canvas.create_text(p1m[0], p1m[1]+15*self.scale, text='{:.2f}'.format(N[0]), fill='blue')
			self.canvas.create_line(xy, fill='blue')
			if np.absolute(N[1]) > 0.0001:
				self.canvas.create_line(p2[0], p2[1], p2m[0], p2m[1], fill='blue')
				self.canvas.create_text(p2m[0], p2m[1]+15*self.scale, text='{:.2f}'.format(N[0]), fill='blue')
			self.canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill='gray25', width=2)

		for i in range(len(self.nodesList)):
			x = self.nodesList[i].coords[0]
			y = self.nodesList[i].coords[1]
			p = canvascoords(x, y, self.scale)
			x = p[0]
			y = p[1]
			self.canvas.create_image(x, y, image=self.img_nodecanvas, tags = ('Node', i))
		return