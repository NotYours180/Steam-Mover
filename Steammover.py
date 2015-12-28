from sm import *
import tkinter as tk
ask = tk.messagebox.askyesno

bgcolor = '#dddddd'
usedcolor = '#000000'
withcolor = '#448844'
ohnecolor = '#ff4444'

defaultlist = ["Library not found!, Make sure the path", "contains both 'steam.dll' and 'steamapps'!"]

def names(library):
    lib = library['games']
    return [lib[x]['name'] for x in lib] 

def updateitem(box, item):
    if type(box) == tk.Label:
        box.config(text=item)
    else:
        box.delete(0, 'end')
        if type(item) == str:
            box.insert('end', item)
        else:
            for i in item:
                box.insert('end', i)

class Window:
    def createdefault(self):
        try:
            with open('libraries.txt', 'x') as f:
                f.write(defaultsettings)
        except FileExistsError:
            ...
        os.startfile(os.path.realpath('libraries.txt'))

    def canvas(self, canvas, cap, col):
        canvas.delete('bar')
        if type(col[0])== str:
            col = [col]

        for colour, left, right in col:
            if colour == 'none':
                continue #Do not draw
            left /= cap
            right /= cap
            left *= 300
            right *= 300
            canvas.create_rectangle(left, 0, right, 20, fill=colour, width=0, tags='bar')
        
    def refresh(self):
        '''Updates libary list'''
        try:
            llib = buildfolder(self.ltype.get())
        except:
            llib = False
            updateitem(self.llab, 'No drive found!')
            updateitem(self.llis, defaultlist)
        else:
            self.canvas(self.lbar, llib['capacity'],[
                       (bgcolor,0,llib['capacity']),(usedcolor, 0, llib['used'])])
            updateitem(self.llab, '%s (%s free)' %
                       (bytesize(llib['capacity']), bytesize(llib['free']))
                       )
            updateitem(self.llis, sorted(names(llib)))
                        
        try:
            rlib = buildfolder(self.rtype.get())
        except:
            rlib = False
            updateitem(self.rlab, 'No drive found!')
            updateitem(self.rlis, defaultlist)
        else:
            self.canvas(self.rbar, rlib['capacity'],[
                        (bgcolor,0,rlib['capacity']),(usedcolor, 0, rlib['used'])])
            updateitem(self.rlab, '%s (%s free)' %
                       (bytesize(rlib['capacity']), bytesize(rlib['free']))
                       )
            updateitem(self.rlis, sorted(names(rlib)))
        
        self.llib = llib
        self.rlib = rlib

    def title(self, update, percent):
        if percent > 99.9:
            self.window.title('Steam mover')
        else:
            self.window.title('Steam mover – %.2f%% – %s' %(percent, update)) 

    def op(self, typ):
        if typ == 'delete':
            if ask('Delete game?','Are you sure you want to delete %s (%s)?' %
                   (self.game['name'], bytesize(self.game['size'])), icon='warning',default='no'):
                delete(self.srclib, self.game['id'])
        elif typ == 'move':
            if ask('Move game?', 'Are you sure you want to move %s (%s)?' %
                   (self.game['name'], bytesize(self.game['size'])), icon='warning',default='no'):
                move(self.srclib, self.game['id'], self.dstlib, True, self.title)
        elif typ == 'copy':
            if ask('Copy game?', 'Are you sure you want to copy %s (%s)?' %
                   (self.game['name'], bytesize(self.game['size'])), icon='warning',default='no'):
                move(self.srclib, self.game['id'], self.dstlib, False, self.title)

        self.refresh()
        
    def button(self, state):
        for i in self.bcopy, self.bmove, self.bdel:
            i.config(state=state)

    def select(self, side):
        if side == 'l':
            if not self.llib:
                return False
            gamen = self.llis.get('active')
            lib = self.llib
            dstlib = self.rlib
            dstnam = 'right'
        else:
            if not self.rlib:
                return False
            gamen = self.rlis.get('active')
            lib = self.rlib
            dstlib = self.llib
            dstnam = 'left'

        if dstnam == 'left':
            srcbar = self.rbar
            dstbar = self.lbar
        else:
            srcbar = self.lbar
            dstbar = self.rbar
        
        game = False
        for g in lib['games']:
            if lib['games'][g]['name'] == gamen:
                game = lib['games'][g]

        if game: # if game is found
            name = game['name']
            if len(name) > 50:
                name = name[:50] + '...' #Truncate name for display
            
            remaining = dstlib['free'] - game['size']

            self.canvas(srcbar, lib['capacity'],[
                       (bgcolor,0,lib['capacity']),(usedcolor, 0, lib['used']),
                       (ohnecolor, lib['used'] - game['size'], lib['used'])
                       ])
            
            if remaining > 0:
                updateitem(self.info, '%s\nSize: %s – %s remaining if moved to %s' % (
                    name, bytesize(game['size']), bytesize(remaining), dstnam))
                self.game = game
                self.srclib = lib
                self.dstlib = dstlib
                self.button('normal')
                
                self.canvas(dstbar, dstlib['capacity'],[
                            (bgcolor,0, dstlib['capacity']),(usedcolor, 0, dstlib['used']),
                            (withcolor, dstlib['used'], dstlib['used'] + game['size'])
                            ])
            else:
                updateitem(self.info, '%s\nSize: %s – %s more needed on %s library' % (
                    name, bytesize(game['size']), bytesize(abs(remaining)), dstnam))
                self.button('disabled')

                self.canvas(dstbar, dstlib['capacity'],[
                            (ohnecolor, 0, dstlib['capacity']),
                            (usedcolor, 0, dstlib['used']),
                            ])
        else:
            defaultcanv = True
            updateitem(self.info, 'No game selected.')

    def window(self):
        w = tk.Tk()
        w.title('Steam mover')
        w.resizable(0,1)
        w.minsize(600,300)
        self.window = w

        w.grid_rowconfigure(3, weight=1)
        
        ltype = tk.Entry(w, width=50) #Path entry
        rtype = tk.Entry(w, width=50)

        ltype.insert(0, 'C:/Program Files (x86)/Steam')
        rtype.insert(0, 'N:/Steam')

        ltype.bind('<Return>', lambda e: self.refresh())
        rtype.bind('<Return>', lambda e: self.refresh())
        
        ltype.grid(row=0)
        rtype.grid(row=0,column=1, columnspan=3)


        llab = tk.Label(w, text='Left drive')
        rlab = tk.Label(w, text='Right drive')
        
        llab.grid(row=1)
        rlab.grid(row=1,column=1, columnspan=3)


        lbar = tk.Canvas(w, height=20, width=300) 
        rbar = tk.Canvas(w, height=20, width=300)

        lbar.grid(row=2)
        rbar.grid(row=2,column=1, columnspan=3)


        llis = tk.Listbox(w, width=50)
        rlis = tk.Listbox(w, width=50)

        llis.grid(row=3, sticky='ns')
        rlis.grid(row=3, column=1, sticky='ns', columnspan=3)

        llis.bind('<Double-Button-1>', lambda e: self.select('l'))
        rlis.bind('<Double-Button-1>', lambda e: self.select('r'))
        

        info = tk.Label(w, text='No game selected.', width=42)
        info.grid(row=4, rowspan=2)

        bcopy = tk.Button(w, text='Copy', command=lambda: self.op('copy'))
        bcopy.grid(row=4, column=1, sticky='nwe')
        
        bmove = tk.Button(w, text='Move', command=lambda: self.op('move'))
        bmove.grid(row=4, column=2, sticky='nwe')

        bdel = tk.Button(w, text='Delete', command=lambda: self.op('delete'))
        bdel.grid(row=4, column=3, sticky='nwe')

        self.ltype = ltype
        self.rtype = rtype
        self.llis = llis
        self.rlis = rlis
        self.llab = llab
        self.rlab = rlab
        self.lbar = lbar
        self.rbar = rbar
        self.info = info
        self.bcopy = bcopy
        self.bmove = bmove
        self.bdel = bdel

        self.button('disabled')

    def __init__(self):
        self.window()
        self.refresh()


w = Window()
