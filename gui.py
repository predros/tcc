from classes import *
from functions import *
import tkinter as tk
from tkinter import messagebox, Frame, ttk, Listbox, Canvas
# Initial parameters

width = 700
height = 500
results = []

# Window declarations
window_main = tk.Tk()
window_main.title('Zap 2000')
frame_parent = Frame(window_main)
frame_buttons = Frame(window_main, width=width)
canvas_main = MainCanvas(window_main, width, height)
frame_buttons.pack(fill=tk.BOTH, expand=True)
canvas_main.frame.pack(fill=tk.BOTH, expand=True)

m = Material('teste', 2380, 0.000001)
s = Section('teste', 4200, 225, 15, 7.5)
canvas_main.materialsList.append(m)
canvas_main.sectionsList.append(s)

loadcase = LoadCase('Case 01', canvas_main.nodesList, canvas_main.membersList)
canvas_main.loadCasesList.append(loadcase)


def selection():
	'''
	Enables the 'Selection' cursor.
	'''
	canvas_main.ClickType = 'select'
	canvas_main.redraw()

def newnode():
	'''
	Opens the 'Add new node' window.
	'''
	for child in frame_parent.winfo_children():
		child.destroy()
	canvas_main.ClickType = 'node'
	win_newnode = tk.Toplevel(frame_parent, padx=10, pady=10)
	frame_newnode = ttk.LabelFrame(win_newnode, text='Adicionar pontos')
	frame_newnode.grid(row=0, column=0)
	win_newnode.title('Adicionar pontos')
	win_newnode.geometry('+800+100')
	win_newnode.attributes('-topmost', 'true')
	win_newnode.resizable(False, False)
	win_newnode.focus()
	win_newnode.grid_rowconfigure(0, minsize=40)
	ttk.Label(frame_newnode, text='Coordenada X:').grid(column=0, row=0)
	ttk.Label(frame_newnode, text='Coordenada Y:').grid(column=0, row=1)
	x = ttk.Entry(frame_newnode, width=8, justify=tk.RIGHT)
	x.insert(0, '0')
	x.grid(column=1, row=0)
	y = ttk.Entry(frame_newnode, width=8, justify=tk.RIGHT)
	y.insert(0, '0')
	y.grid(column=1, row=1)

	def add_node():
		'''
		Adds a new node to the structure.
		'''
		if x.get() == '' or y.get() == '':
			messagebox.showwarning('Erro', 'Preencha dados válidos.')
			return
		coord = [float(x.get()), float(y.get())]
		for i in range(len(canvas_main.nodesList)):
			if coord == canvas_main.nodesList[i].coords:
				messagebox.showwarning('Erro', 'Já existe um ponto nas coordenadas indicadas.')
				return
		n = Node(coord[0], coord[1])
		canvas_main.nodesList.append(n)
		for loadcase in canvas_main.loadCasesList:
			loadcase.newNode()
		canvas_main.redraw()

	def when_closed():
		'''
		Closes the 'New node' window.
		'''
		canvas_main.ClickType = 'select'
		win_newnode.destroy()

	win_newnode.protocol('WM_DELETE_WINDOW', when_closed)
	button_closeframe = ttk.Button(frame_newnode, text='Fechar', command=when_closed)
	button_addnode = ttk.Button(frame_newnode, text='Adicionar', command=add_node)
	button_closeframe.grid(column=0, row=2)
	button_addnode.grid(column=1,row=2)

def newmember():
	'''
	Opens the 'Add new node' window.
	'''
	for child in frame_parent.winfo_children():
		child.destroy()
	mat = []
	sec = []
	for x in canvas_main.materialsList:
		mat.append(x.name)
	for x in canvas_main.sectionsList:
		sec.append(x.name)
	canvas_main.ClickType = 'member'
	win_newmember = tk.Toplevel(frame_parent, padx=20, pady=20)
	win_newmember.title('Adicionar pontos')
	win_newmember.geometry('+800+100')
	win_newmember.attributes('-topmost', 'true')
	win_newmember.resizable(False, False)
	win_newmember.focus()
	ttk.Label(win_newmember, text='Adicionar barra:').grid(column=0, row=0, columnspan=2)
	ttk.Label(win_newmember, text='Nó inicial:').grid(column=0, row=1)
	ttk.Label(win_newmember, text='Nó final:').grid(column=0, row=2)
	ttk.Label(win_newmember, text='Material:').grid(column=0, row=3)
	ttk.Label(win_newmember, text='Seção:').grid(column=0, row=4)
	start = ttk.Entry(win_newmember, width=8, justify=tk.RIGHT)
	start.insert(0, '0')
	start.grid(column=1, row=1)
	start.focus()
	end = ttk.Entry(win_newmember, width=8, justify=tk.RIGHT)
	end.insert(0, '1')
	end.grid(column=1, row=2)
	material = tk.StringVar(win_newmember)
	mat_list = ttk.Combobox(win_newmember, textvariable=material, state='readonly')
	mat_list['values'] = tuple(mat)
	mat_list.grid(column=1, row=3, columnspan=2)
	section = tk.StringVar(win_newmember)
	sec_list = ttk.Combobox(win_newmember, textvariable=section, state='readonly')
	sec_list['values'] = tuple(sec)
	sec_list.grid(column=1, row=4, columnspan=2)

	def CurSel(evt):
		canvas_main.currentMaterial = str(material.get())
		canvas_main.currentSection = str(section.get())
		return

	def addMember():
		'''
		Adds a new member to the structure, if all conditions are met.
		'''
		n = [int(start.get()), int(end.get())]
		mat = str(material.get())
		sec = str(section.get())
		if n[0] == n[1]:
			messagebox.showwarning('Erro', 'Selecione pontos diferentes para início e fim da barra.')
			return
		elif n[0] not in range(len(canvas_main.nodesList)) or n[1] not in range(len(canvas_main.nodesList)):
			messagebox.showwarning('Erro', 'Selecione pontos válidos.')
			return
		elif not mat:
			messagebox.showwarning('Erro', 'Selecione um material.')
			return
		elif not sec:
			messagebox.showwarning('Erro', 'Selecione uma seção.')
			return
		else:
			for i in range(len(canvas_main.membersList)):
				if sorted(n) == sorted(canvas_main.membersList[i].nodes):
					messagebox.showwarning('Erro', 'Já existe uma barra nos pontos indicados.')
					return
			m = Member(n[0], n[1], mat, sec)
			canvas_main.membersList.append(m)
			for loadcase in canvas_main.loadCasesList:
				loadcase.newMember()
			canvas_main.redraw()
	
	mat_list.bind('<<ComboboxSelected>>', CurSel)
	sec_list.bind('<<ComboboxSelected>>', CurSel)
	frame_ok = ttk.Button(win_newmember, text='Adicionar barra', command=addMember)
	frame_ok.grid(column=1, row=7)

def managematerials():
	'''
	Opens the 'Manage materials' window.
	'''
	for child in frame_parent.winfo_children():
		child.destroy()
	win_material = tk.Toplevel(frame_parent, padx=10, pady=10)
	win_material.title('Gerenciar materiais')
	frame_materialsList = ttk.LabelFrame(win_material, text='Materiais')
	frame_newMaterial = ttk.LabelFrame(win_material, text='Propriedades')
	frame_materialsList.pack(side=tk.LEFT, fill=tk.Y)
	frame_newMaterial.pack(side=tk.LEFT, fill=tk.Y)
	win_material.geometry("+400+300")
	win_material.resizable(False, False)
	win_material.grab_set()

	def CurSel(evt):
		'''
		Changes the properties displayed on the entry boxes after clicking a name on the listbox.
		'''
		name = str(mat_list.get(mat_list.curselection()))
		E = str(next((material.E for material in canvas_main.materialsList if material.name == name), None))
		alpha = str(next((material.alpha for material in canvas_main.materialsList if material.name == name), None))
		mat_name.delete(0, tk.END)
		mat_E.delete(0, tk.END)
		mat_alpha.delete(0, tk.END)
		mat_name.insert(tk.END, name)
		mat_E.insert(tk.END, str(E))
		mat_alpha.insert(tk.END, str(alpha))
	mat_list = Listbox(frame_materialsList, selectmode='BROWSE')
	mat_list.grid(row=0, column=0, columnspan=4)
	mat_list.bind('<<ListboxSelect>>',CurSel)
	for x in canvas_main.materialsList:
		mat_list.insert(0, x.name)
	frame_newMaterial.grid_rowconfigure(0, minsize=25) 
	ttk.Label(frame_newMaterial, text='Nome:').grid(row=1, column=0)
	mat_name = ttk.Entry(frame_newMaterial, width=8, justify=tk.RIGHT)
	mat_name.insert(0, '')
	mat_name.grid(row=1, column=1)
	mat_name.focus()
	ttk.Label(frame_newMaterial, text='E =').grid(row=2, column=0)
	mat_E = ttk.Entry(frame_newMaterial, width=8, justify=tk.RIGHT)
	mat_E.insert(0, '0')
	mat_E.grid(row=2, column=1)
	ttk.Label(frame_newMaterial, text='α =').grid(row=3, column=0)
	mat_alpha = ttk.Entry(frame_newMaterial, width=8, justify=tk.RIGHT)
	mat_alpha.insert(0, '0')
	mat_alpha.grid(row=3, column=1)

	def add_material():
		'''
		Adds a new material or edits an existing one, depending on the name given.
		'''
		name = mat_name.get()
		E = mat_E.get()
		alpha = mat_alpha.get()
		if not name.strip():
			messagebox.showwarning('Erro', 'Preencha todos os dados.')
			return
		for mat in canvas_main.materialsList:
			if mat.name == name:
				mat.setprop(float(E), float(alpha))
				return
		else:
			m = Material(name, float(E), float(alpha))
			canvas_main.materialsList.append(m)
			mat_list.insert(tk.END, name)
			return

	def delete_material():
		'''
		Deletes the selected material.
		'''
		name = mat_name.get()
		canvas_main.materialsList.remove(next((material for material in canvas_main.materialsList if material.name == name), None))
		mat_list.delete(tk.ACTIVE)
		return
	frame_newMaterial.grid_rowconfigure(4, minsize=45) 
	mat_ok = ttk.Button(frame_newMaterial, text='Adicionar/editar', command=add_material)
	mat_ok.grid(row=5, column=0)
	mat_del = ttk.Button(frame_newMaterial, text='Remover', command=delete_material)
	mat_del.grid(row=5, column=1)

def managesections():
	'''
	Opens the 'Manage sections' window.
	'''
	for child in frame_parent.winfo_children():
		child.destroy()
	win_section = tk.Toplevel(frame_parent, padx=10, pady=10)
	win_section.title('Gerenciar seções')
	win_section.resizable(False, False)
	win_section.geometry("+400+300")
	win_section.grab_set()

	frame_sectionsList = ttk.LabelFrame(win_section, text='Seções')
	frame_newSection = ttk.LabelFrame(win_section, text='Propriedades')
	frame_sectionsList.pack(side=tk.LEFT, fill=tk.Y)
	frame_newSection.pack(side=tk.LEFT, fill=tk.Y)

	def CurSel(evt):
		'''
		Changes the properties displayed on the entry boxes after clicking a name on the listbox.
		'''
		name = str(sec_list.get(sec_list.curselection()))
		I = str(next((section.I for section in canvas_main.sectionsList if section.name == name), None))
		A = str(next((section.A for section in canvas_main.sectionsList if section.name == name), None))
		h = str(next((section.h for section in canvas_main.sectionsList if section.name == name), None))
		yg = str(next((section.yg for section in canvas_main.sectionsList if section.name == name), None))
		sec_name.delete(0, tk.END)
		sec_I.delete(0, tk.END)
		sec_A.delete(0, tk.END)
		sec_h.delete(0, tk.END)
		sec_yg.delete(0, tk.END)
		sec_name.insert(tk.END, name)
		sec_I.insert(tk.END, str(I))
		sec_A.insert(tk.END, str(A))
		sec_h.insert(tk.END, str(h))
		sec_yg.insert(tk.END, str(yg))

	sec_list = Listbox(frame_sectionsList, selectmode='BROWSE')
	sec_list.grid(column=0, row=0, rowspan=3)
	sec_list.bind('<<ListboxSelect>>',CurSel)
	for x in canvas_main.sectionsList:
		sec_list.insert(0, x.name)
	frame_newSection.grid_rowconfigure(0, minsize=20)
	ttk.Label(frame_newSection, text='Nome:').grid(column=0, row=1)
	sec_name = ttk.Entry(frame_newSection, width=8, justify=tk.RIGHT)
	sec_name.insert(0, '')
	sec_name.grid(column=1,row=1)
	sec_name.focus()
	ttk.Label(frame_newSection, text='Inércia:').grid(column=0, row=2)
	sec_I = ttk.Entry(frame_newSection, width=8, justify=tk.RIGHT)
	sec_I.insert(0, '0')
	sec_I.grid(column=1,row=2)
	ttk.Label(frame_newSection, text='Área:').grid(column=0, row=3)
	sec_A = ttk.Entry(frame_newSection, width=8, justify=tk.RIGHT)
	sec_A.insert(0, '0')
	sec_A.grid(column=1,row=3)
	ttk.Label(frame_newSection, text='Altura:').grid(column=0, row=4)
	sec_h = ttk.Entry(frame_newSection, width=8, justify=tk.RIGHT)
	sec_h.insert(0, '0')
	sec_h.grid(column=1,row=4)
	ttk.Label(frame_newSection, text='Centroide:').grid(column=0, row=5)
	sec_yg = ttk.Entry(frame_newSection, width=8, justify=tk.RIGHT)
	sec_yg.insert(0, '0')
	sec_yg.grid(column=1,row=5)

	def add_section():
		'''
		Adds a new section or edits an existing one, depending on the given name.
		'''
		name = sec_name.get()
		I = sec_I.get()
		A = sec_A.get()
		h = sec_h.get()
		yg = sec_yg.get()
		if not name.strip():
			messagebox.showwarning('Erro', 'Preencha todos os dados.')
			return
		for sec in canvas_main.sectionsList:
			if sec.name == name:
				sec.setprop(float(I), float(A), float(h), float(yg))
				return
		else:
			s = Section(name, float(I), float(A), float(h), float(yg))
			canvas_main.sectionsList.append(s)
			sec_list.insert(tk.END, name)
			return

	def delete_section():
		'''
		Deletes the selected section.
		'''
		name = sec_name.get()
		canvas_main.sectionsList.remove(next((section for section in canvas_main.sectionsList if section.name == name), None))
		mat_list.delete(tk.ACTIVE)
		return
	frame_newSection.grid_rowconfigure(6, minsize=20)
	sec_ok = ttk.Button(frame_newSection, text='Adicionar/editar seção', command=add_section)
	sec_ok.grid(column=1,row=7)
	sec_del = ttk.Button(frame_newSection, text='Remover seção', command=delete_section)
	sec_del.grid(column=0, row=7)

def setsupports():
	'''
	Opens the 'Set support conditions' window.
	'''
	for child in frame_parent.winfo_children():
		child.destroy()
	win_support = tk.Toplevel(frame_parent, padx=10, pady=10)
	win_support.title('Restrições nodais')
	win_support.resizable(False, False)
	win_support.geometry("+800+100")
	win_support.attributes('-topmost', 'true')
	win_support.focus()

	tabs = ttk.Notebook(win_support)
	label_main = ttk.Frame(tabs)
	tabs.add(label_main, text='Restrições')
	tabs.pack(expand=1, fill='both')
	label_pdispl = ttk.Frame(tabs)
	tabs.add(label_pdispl, text='Prescritos')
	tabs.pack(expand=1, fill='both')
	label_springs = ttk.Frame(tabs)
	tabs.add(label_springs, text='Molas')
	tabs.pack(expand=1, fill='both')

	ttk.Label(label_main, text='Deslocamento X:').grid(row=1, column=0)
	ttk.Label(label_main, text='Deslocamento Y:').grid(row=2, column=0)
	ttk.Label(label_main, text='Rotação Z:').grid(row=3, column=0)
	dx = tk.IntVar()
	dy = tk.IntVar()
	rz = tk.IntVar()

	def restr_state():
		x = int(dx.get())
		y = int(dy.get())
		z = int(rz.get())
		if x == 0:
			pdx.config(state=tk.DISABLED)
			kx.config(state=tk.NORMAL)
		else:
			pdx.config(state=tk.NORMAL)
			kx.config(state=tk.DISABLED)
		if y == 0:
			pdy.config(state=tk.DISABLED)
			ky.config(state=tk.NORMAL)
		else:
			pdy.config(state=tk.NORMAL)
			ky.config(state=tk.DISABLED)
		if z == 0:
			pdz.config(state=tk.DISABLED)
			kz.config(state=tk.NORMAL)
		else:
			pdz.config(state=tk.NORMAL)
			kz.config(state=tk.DISABLED)
		return

	ttk.Radiobutton(label_main, text='Liberado', variable=dx, value=0, command=restr_state).grid(row=1, column=1)
	ttk.Radiobutton(label_main, text='Restringido', variable=dx, value=1, command=restr_state).grid(row=1, column=2)
	ttk.Radiobutton(label_main, text='Liberado', variable=dy, value=0, command=restr_state).grid(row=2, column=1)
	ttk.Radiobutton(label_main, text='Restringido', variable=dy, value=1, command=restr_state).grid(row=2, column=2)
	ttk.Radiobutton(label_main, text='Liberado', variable=rz, value=0, command=restr_state).grid(row=3, column=1)
	ttk.Radiobutton(label_main, text='Restringido', variable=rz, value=1, command=restr_state).grid(row=3, column=2)

	label_pdispl.grid_columnconfigure(1, minsize=110)
	label_pdispl.grid_columnconfigure(3, minsize=110)
	ttk.Label(label_pdispl, text='Prescrito X:').grid(row=1, column=0, columnspan=2)
	ttk.Label(label_pdispl, text='Prescrito Y:').grid(row=2, column=0, columnspan=2)
	ttk.Label(label_pdispl, text='Prescrito Z:').grid(row=3, column=0, columnspan=2)
	pdx = ttk.Entry(label_pdispl, width=8, justify=tk.RIGHT)
	pdx.insert(0, '0')
	pdx.config(state=tk.DISABLED)
	pdx.grid(row=1, column=3)
	pdy = ttk.Entry(label_pdispl, width=8, justify=tk.RIGHT)
	pdy.insert(0, '0')
	pdy.config(state=tk.DISABLED)
	pdy.grid(row=2, column=3)
	pdz = ttk.Entry(label_pdispl, width=8, justify=tk.RIGHT)
	pdz.insert(0, '0')
	pdy.config(state=tk.DISABLED)
	pdz.grid(row=3, column=3)

	label_springs.grid_columnconfigure(1, minsize=110)
	label_springs.grid_columnconfigure(3, minsize=110)
	ttk.Label(label_springs, text='Constante KX:').grid(row=1, column=0, columnspan=2)
	ttk.Label(label_springs, text='Constante KY:').grid(row=2, column=0, columnspan=2)
	ttk.Label(label_springs, text='Constante KZ:').grid(row=3, column=0, columnspan=2)
	kx = ttk.Entry(label_springs, width=8, justify=tk.RIGHT)
	kx.insert(0, '0')
	kx.grid(row=1, column=3, columnspan=2)
	ky = ttk.Entry(label_springs, width=8, justify=tk.RIGHT)
	ky.insert(0, '0')
	ky.grid(row=2, column=3, columnspan=2)
	kz = ttk.Entry(label_springs, width=8, justify=tk.RIGHT)
	kz.insert(0, '0')
	kz.grid(row=3, column=3, columnspan=2)



	def when_apply():
		canvas_main.ClickType = 'support'
		x = int(dx.get())
		y = int(dy.get())
		z = int(rz.get())
		canvas_main.restrictions = [x, y, z]
		if x == 0:
			canvas_main.pDisplacements[0] = 0
			canvas_main.springConstants[0] = np.absolute(float(kx.get()))
		else:
			canvas_main.pDisplacements[0] = float(pdx.get())
			canvas_main.springConstants[0] = 0
		if y == 0:
			canvas_main.pDisplacements[1] = 0
			canvas_main.springConstants[1] = np.absolute(float(ky.get()))
		else:
			canvas_main.pDisplacements[1] = float(pdy.get())
			canvas_main.springConstants[1] = 0
		if z == 0:
			canvas_main.pDisplacements[2] = 0
			canvas_main.springConstants[2] = np.absolute(float(kz.get()))
		else:
			canvas_main.pDisplacements[2] = float(pdz.get())
			canvas_main.springConstants[2] = 0
		canvas_main.canvas.focus()
		return

	def when_closed():
		canvas_main.ClickType = 'select'
		win_support.destroy()
		canvas_main.restrictions = [0, 0, 0]
		return

	win_support.protocol('WM_DELETE_WINDOW', when_closed)
	button_close = ttk.Button(win_support, text='Fechar', command=when_closed)
	button_close.pack(side=tk.LEFT, fill=tk.X)
	button_apply = ttk.Button(win_support, text='Aplicar', command=when_apply)
	button_apply.pack(side=tk.LEFT, fill=tk.X)

def nodalforces():
	'''
	Opens the 'Nodal forces' window.
	'''
	for child in frame_parent.winfo_children():
		child.destroy()
	win_nodalforces = tk.Toplevel(frame_parent, padx=5, pady=5)
	win_nodalforces.title('Forças nodais')
	win_nodalforces.resizable(False, False)
	win_nodalforces.geometry("+800+100")
	win_nodalforces.attributes('-topmost', 'true')
	frame_nodalforces = ttk.LabelFrame(win_nodalforces, text='Forças nodais')
	frame_nodalforces.pack()
	win_nodalforces.focus()

	frame_nodalforces.grid_rowconfigure(0, minsize=10)
	frame_nodalforces.grid_columnconfigure(0, minsize=10)
	frame_nodalforces.grid_columnconfigure(4, minsize=10)
	ttk.Label(frame_nodalforces, text='Força X:').grid(column=1, row=1)
	PX = ttk.Entry(frame_nodalforces, width=8, justify=tk.RIGHT)
	PX.insert(0, '0')
	PX.grid(column=2, row=1)
	ttk.Label(frame_nodalforces, text='Força Y:').grid(column=1, row=2)
	PY = ttk.Entry(frame_nodalforces, width=8, justify=tk.RIGHT)
	PY.insert(0, '0')
	PY.grid(column=2, row=2)
	ttk.Label(frame_nodalforces, text='Momento Z:').grid(column=1, row=3)
	MZ = ttk.Entry(frame_nodalforces, width=8, justify=tk.RIGHT)
	MZ.insert(0, '0')
	MZ.grid(column=2, row=3)

	def when_apply():
		canvas_main.ClickType = 'nodalforces'
		canvas_main.nodalForces = [float(PX.get()), float(PY.get()), float(MZ.get())]
		canvas_main.canvas.focus()

	def when_closed():
		'''
		Closes the 'New node' window.
		'''
		canvas_main.ClickType = 'select'
		win_nodalforces.destroy()

	win_nodalforces.protocol('WM_DELETE_WINDOW', when_closed)
	button_closeframe = ttk.Button(frame_nodalforces, text='Fechar', command=when_closed)
	frame_nodalforces.grid_rowconfigure(4, minsize=10)
	button_closeframe.grid(column=0, row=5, columnspan=2)
	button_apply = ttk.Button(frame_nodalforces, text='Aplicar', command=when_apply)
	button_apply.grid(column=2, row=5, columnspan=2)

def memberloads():
	'''
	Opens the 'Member loads' window.
	'''
	for child in frame_parent.winfo_children():
		child.destroy()
	win_memberloads = tk.Toplevel(frame_parent, padx=5, pady=5)
	win_memberloads.title('Carregamentos')
	win_memberloads.resizable(False, False)
	win_memberloads.geometry("+800+100")
	win_memberloads.attributes('-topmost', 'true')
	win_memberloads.focus()
	frame_memberloads = ttk.LabelFrame(win_memberloads, text='Carregamentos')
	frame_memberloads.pack(side=tk.TOP, fill=tk.X)
	frame_memberloads.grid_rowconfigure(0, minsize=10)
	frame_memberloads.grid_columnconfigure(0, minsize=10)
	frame_memberloads.grid_columnconfigure(1, minsize=20)
	frame_memberloads.grid_columnconfigure(4, minsize=10)
	ttk.Label(frame_memberloads, text='Direção X:').grid(column=0, row=1)
	qx = ttk.Entry(frame_memberloads, width=8, justify=tk.RIGHT)
	qx.insert(0, '0')
	qx.grid(column=2, row=1)
	ttk.Label(frame_memberloads, text='Direção Y:').grid(column=0, row=2)
	qy = ttk.Entry(frame_memberloads, width=8, justify=tk.RIGHT)
	qy.insert(0, '0')
	qy.grid(column=2, row=2)

	def when_apply():
		canvas_main.ClickType = 'memberloads'
		canvas_main.memberLoads = [float(qx.get()), float(qy.get())]
		canvas_main.canvas.focus()

	def when_closed():
		'''
		Closes the 'New node' window.
		'''
		canvas_main.ClickType = 'select'
		win_memberloads.destroy()

	win_memberloads.protocol('WM_DELETE_WINDOW', when_closed)
	button_closeframe = ttk.Button(win_memberloads, text='Fechar', command=when_closed)
	button_closeframe.pack(side=tk.LEFT)
	button_apply = ttk.Button(win_memberloads, text='Aplicar', command=when_apply)
	button_apply.pack(side=tk.LEFT)

#def otherloads():
def run():
	N_X = []
	N_Y = []
	N_PX = []
	N_PY = []
	N_MZ = []
	N_RESTRX = []
	N_RESTRY = []
	N_RESTRZ = []
	N_KX = []
	N_KY = []
	N_KZ = []
	N_PDX = []
	N_PDY = []
	N_PDZ = []

	FR_START = []
	FR_END = []
	FR_E = []
	FR_alpha = []
	FR_I = []
	FR_A = []
	FR_ysup = []
	FR_yinf = []
	FR_qx = []
	FR_qy = []
	FR_Tinf = []
	FR_Tsup = []
	FR_tensile = []
	FR_curvature = []
	P = []

	for node in canvas_main.nodesList:
		i = canvas_main.nodesList.index(node)
		N_X.append(node.coords[0])
		N_Y.append(node.coords[1])

		N_RESTRX.append(node.restr[0])
		N_RESTRY.append(node.restr[1])
		N_RESTRZ.append(node.restr[2])

		PX = canvas_main.loadCasesList[0].Px[i]
		PY = canvas_main.loadCasesList[0].Py[i]
		MZ = canvas_main.loadCasesList[0].Mz[i]
		N_PX.append(PX)
		N_PY.append(PY)
		N_MZ.append(MZ)

		N_KX.append(node.springs[0])
		N_KY.append(node.springs[1])
		N_KZ.append(node.springs[2])

		N_PDX.append(node.pdispl[0])
		N_PDY.append(node.pdispl[1])
		N_PDZ.append(node.pdispl[2])

	for member in canvas_main.membersList:
		i = canvas_main.membersList.index(member)
		FR_START.append(member.nodes[0])
		FR_END.append(member.nodes[1])
		
		for material in canvas_main.materialsList:
			if member.matname == material.name:
				E = material.E
				alpha = material.alpha
		FR_E.append(E)
		FR_alpha.append(alpha)

		for section in canvas_main.sectionsList:
			if member.secname == section.name:
				I = section.I
				A = section.A
				ysup = section.ysup
				yinf = section.yg
		FR_I.append(I)
		FR_A.append(A)
		FR_ysup.append(ysup)
		FR_yinf.append(yinf)

		qx = canvas_main.loadCasesList[0].qx[i]
		qy = canvas_main.loadCasesList[0].qy[i]
		FR_qx.append(qx)
		FR_qy.append(qy)

		FR_Tinf.append(0)
		FR_Tsup.append(0)
		FR_tensile.append(0)
		FR_curvature.append(0)
		P.append(0)

	results = G_Run(N_X, N_Y, N_PX, N_PY, N_MZ, N_RESTRX, N_RESTRY, N_RESTRZ, N_KX, N_KY, N_KZ, N_PDX, N_PDY, N_PDZ, FR_START, FR_END, FR_qx, FR_qy, FR_Tinf, FR_Tsup, FR_yinf, FR_ysup, FR_tensile, FR_curvature, FR_E, FR_I, FR_A, FR_alpha, P)
	canvas_main.drawBending(results)

# Button icons
img_selection = tk.PhotoImage(file='./img/icons/img_selection.gif')
img_node = tk.PhotoImage(file="./img/icons/img_node.gif")
img_member = tk.PhotoImage(file='./img/icons/img_member.gif')
img_material = tk.PhotoImage(file='./img/icons/img_material.gif')
img_section = tk.PhotoImage(file='./img/icons/img_section.gif')

img_support = tk.PhotoImage(file='./img/icons/img_support.gif')
img_nodal = tk.PhotoImage(file='./img/icons/img_nodal.gif')
img_load = tk.PhotoImage(file='./img/icons/img_load.gif')
img_hinge = tk.PhotoImage(file='./img/icons/img_hinge.gif')

img_run = tk.PhotoImage(file='./img/icons/img_run.gif')
img_runsettings = tk.PhotoImage(file='./img/icons/img_runsettings.gif')


# Action buttons
frame_geometry = ttk.LabelFrame(frame_buttons, text='Geometria', labelanchor=tk.S)
button_selection = ttk.Button(frame_geometry, text='Selecionar', image=img_selection, command=selection)
button_newnode = ttk.Button(frame_geometry, text='Ponto', image=img_node, command=newnode)
button_managematerials = ttk.Button(frame_geometry, text='Materiais', image=img_material, command=managematerials)
button_managesections = ttk.Button(frame_geometry, text='Seções', image=img_section, command=managesections)
button_newmember = ttk.Button(frame_geometry, text='Barra', image=img_member, command=newmember)

frame_structure = ttk.LabelFrame(frame_buttons, text='Estrutura', labelanchor=tk.S)
button_supportconditions = ttk.Button(frame_structure, text='Apoios', image=img_support, command=setsupports)
button_nodalforces = ttk.Button(frame_structure, text='Nodais', image=img_nodal, command=nodalforces)
button_memberloads = ttk.Button(frame_structure, text='Cargas', image=img_load, command=memberloads)
button_hinges = ttk.Button(frame_structure, text='Rótulas', image=img_hinge, state='disabled')

frame_analysis = ttk.LabelFrame(frame_buttons, text='Análise', labelanchor=tk.S)
button_run = ttk.Button(frame_analysis, text='Rodar', image=img_run, command=run)
button_runsettings = ttk.Button(frame_analysis, text='Config. de análise', image=img_runsettings, state='disabled')

# Button tooltips
tooltip_selection = Tooltip(button_selection, text='Ferramenta de seleção')
tooltip_newnode = Tooltip(button_newnode, text='Adicionar ponto à estrutura')
tooltip_newmember = Tooltip(button_newmember, text='Adicionar barra à estrutura')
tooltip_managematerials = Tooltip(button_managematerials, text='Gerenciar materiais')
tooltip_managesections = Tooltip(button_managesections, text='Gerenciar seções')
tooltip_supportconditions = Tooltip(button_supportconditions, text='Adicionar restrições nodais (apoios/molas)')
tooltip_nodalforces = Tooltip(button_nodalforces, text='Adicionar forças nodais')
tooltip_memberloads = Tooltip(button_memberloads, text='Adicionar carregamentos distribuídos')
tooltip_hinges = Tooltip(button_hinges, text='Adicionar liberações nodais (rótulas/articulações)')
tooltip_run = Tooltip(button_run, text='Rodar análise')
tooltip_runsettings = Tooltip(button_runsettings, text='Parâmetros de análise')

frame_geometry.pack(side=tk.LEFT, fill=tk.X)
button_selection.pack(side=tk.LEFT)
button_newnode.pack(side=tk.LEFT)
button_managematerials.pack(side=tk.LEFT)
button_managesections.pack(side=tk.LEFT)

frame_structure.pack(side=tk.LEFT, fill=tk.X)
button_newmember.pack(side=tk.LEFT)
button_supportconditions.pack(side=tk.LEFT)
button_nodalforces.pack(side=tk.LEFT)
button_memberloads.pack(side=tk.LEFT)
button_hinges.pack(side=tk.LEFT)

frame_analysis.pack(side=tk.LEFT, fill=tk.X)
button_run.pack(side=tk.LEFT)
button_runsettings.pack(side=tk.LEFT)

window_main.mainloop()