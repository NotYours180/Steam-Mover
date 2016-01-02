from sm import *
import tkinter as tk
from webbrowser import open_new_tab as web
ask = tk.messagebox.askyesno

bgcolor = '#dddddd'
usedcolor = '#000000'
withcolor = '#448844'
ohnecolor = '#ff4444'

defaultlist = ["Library not found.",
        "Not sure where it is? Try providing a home path", "and we'll try to scan for a library."]


for i in ('C:/Program Files (x86)/Steam/','C:/Program Files/Steam/',
          '~/Library/Application Support/Steam/', '~/.local/share/Steam'):
    configpath = os.path.join(i, 'steamapps', 'libraryfolders.vdf') #List of other libraries
    if os.path.isfile(configpath): #Config exists
        defaultleft = i
        with open(configpath) as f: #Set right path
            for line in f.readlines():
                e = acfgetreg(line, '\d+')
                if e and (e != defaultleft):
                    defaultright = e
                    break
            else: #none found
                defaultright = ''
        break
else:
    defaultleft = ''

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

def getpath(path):
    '''Attempts to resolve to Steam library path.'''
    base = os.path.basename(path)
    if os.path.exists(os.path.join(path, 'steam.dll')):
        pass #If DLL is present, it's valid
    elif base == 'steamapps': #Work down directories
        path = os.path.join(path, '..')
    elif base in ('common', 'downloading', 'sourcemods', 'temp'):
        path = os.path.join(path, '..', '..')
    else:
        downpath = os.path.join(path, 'Steam')
        if os.path.exists(downpath): #Try to work one up
            path = downpath
        else:
            walk = os.walk(path)
            for path_, dirs, files in walk:
                if ('steam.dll' in files or 'Steam.dll' in files)\
                   and 'steamapps' in dirs:
                    path = path_
                    break
            else: #No result
                return False
        

    return os.path.realpath(path)

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
        for side, inp, lab, lis, bar in (
            ('left', self.ltype, self.llab, self.llis, self.lbar),
            ('right', self.rtype, self.rlab, self.rlis, self.rbar)):
          
            try:
                self.title('Looking for %s library' % side)
                path = getpath(inp.get())
                self.title('Scanning %s library' % side)
                lib = buildfolder(path)
            except:
                lib = False
                updateitem(lab, 'No drive found')
                updateitem(lis, defaultlist)
                self.canvas(bar, 1, [(bgcolor,0,1)])
            else:
                updateitem(inp, path)
                self.canvas(bar, lib['capacity'],[
                           (bgcolor,0,lib['capacity']),(usedcolor, 0, lib['used'])])
                updateitem(lab, '%s (%s free)' %
                           (bytesize(lib['capacity']), bytesize(lib['free']))
                           )
                updateitem(lis, sorted(names(lib),
                            key=lambda x: x.lower().replace('the ','').replace('a ','')))
            if side == 'left':
                self.llib = lib
            else:
                self.rlib = lib
        
        self.title() # Clear title

    def title(self, update=None, percent=None):
        '''Update title from callback.'''
        if percent == None:
            if update == None:
                self.window.title('Steam Mover')
            else:
                self.window.title('Steam Mover – %s' % update)
        elif percent > 99.9:
            self.window.title('Steam Mover')
        else:
            self.window.title('Steam Mover – %.2f%% – %s' %(percent, update)) 

    def op(self, typ):
        '''Do operation on game.'''
        if typ == 'delete':
            if ask('Delete game?','Are you sure you want to delete %s (%s)?' %
                   (self.game['name'], bytesize(self.game['size'])), icon='warning',default='no'):
                delete(self.srclib, self.game['id'])
        elif typ == 'deletesteam':
            if ask('Delete game via Steam?','Are you sure you want to delete %s (%s) with Steam? Steam may mistake it for another copy of the game if not reloaded.' %
                   (self.game['name'], bytesize(self.game['size'])), icon='warning',default='no'):
                web('steam://uninstall/%s' % self.game['id'])
        elif typ == 'move':
            if ask('Move game?', 'Are you sure you want to move %s (%s)?' %
                   (self.game['name'], bytesize(self.game['size'])), icon='warning',default='no'):
                move(self.srclib, self.game['id'], self.dstlib, True, self.title)
        elif typ == 'copy':
            if ask('Copy game?', 'Are you sure you want to copy %s (%s)?' %
                   (self.game['name'], bytesize(self.game['size'])), icon='warning',default='no'):
                move(self.srclib, self.game['id'], self.dstlib, False, self.title)

        self.refresh()
        
    def button(self, cat='move', state='normal'):
        '''Changes status for operation buttons.'''
        if cat == 'move':
            btns = (self.bcopy, self.bmove)
        else:
            btns = (self.bopen, self.bplay, self.bdel, self.btool)
        for i in btns:
            i.config(state=state)

    def open(self):
        '''Open selected game in file explorer of choice.'''
        if self.game:
            os.startfile(self.game['path'])

    def play(self):
        if self.game:
            web('steam://run/%s' % self.game['id'])

    def tools(self):        
        if self.game:
            x = self.window.winfo_rootx() + self.btool.winfo_x()
            y = self.window.winfo_rooty() + self.btool.winfo_y()
            self.popup.tk_popup(x,y, 0)

    def select(self, side):
        if side == 'l':
            if not self.llib:
                return False
            gamen = self.llis.get('active')
            lib = self.llib
            dstlib = self.rlib
            srclab = self.llab
            dstlab = self.rlab
            srcnam = 'left'
            dstnam = 'right'
            srcbar = self.lbar
            dstbar = self.rbar
        else:
            if not self.rlib:
                return False
            gamen = self.rlis.get('active')
            lib = self.rlib
            dstlib = self.llib
            srclab = self.rlab
            dstlab = self.llab
            srcbar = self.rbar
            dstbar = self.lbar
            srcnam = 'right'
            dstnam = 'left'
            
        
        game = False
        for g in lib['games']:
            if lib['games'][g]['name'] == gamen:
                game = lib['games'][g]

        if game: # if game is found
            self.game = game
            name = game['name']
            if len(name) > 50:
                name = name[:50] + '...' #Truncate name for display

            self.button('manip')
            
            remaining = dstlib['free'] - game['size']

            updateitem(srclab, '%s (%s free, without game %s free)' % (
                        bytesize(lib['capacity']), bytesize(lib['free']),
                        bytesize(lib['free'] + game['size'])
                        ))

            self.canvas(srcbar, lib['capacity'],[
                       (bgcolor,0,lib['capacity']),(usedcolor, 0, lib['used']),
                       (ohnecolor, lib['used'] - game['size'], lib['used'])
                       ])
            
            
            if remaining > 0:
                updateitem(self.info, '%s (%s side)\nSize: %s – ID: %s' % (
                    name, srcnam, bytesize(game['size']), game['id']))
                self.srclib = lib
                self.dstlib = dstlib
                self.button() #Allow movement buttons

                updateitem(dstlab, '%s (%s free, with game %s free)' % (
                            bytesize(dstlib['capacity']), bytesize(dstlib['free']),
                            bytesize(dstlib['free'] - game['size'])
                            ))

                self.canvas(dstbar, dstlib['capacity'],[
                            (bgcolor,0, dstlib['capacity']),(usedcolor, 0, dstlib['used']),
                            (withcolor, dstlib['used'], dstlib['used'] + game['size'])
                            ])
            else:
                updateitem(self.info, '%s\nSize: %s – %s more needed on %s library' % (
                    name, bytesize(game['size']), bytesize(abs(remaining)), dstnam))
                
                self.button('move', 'disabled') #Disallow movement buttons

                updateitem(dstlab, '%s (%s free)' % (
                            bytesize(dstlib['capacity']), bytesize(dstlib['free'])))
                
                self.canvas(dstbar, dstlib['capacity'],[
                            (ohnecolor, 0, dstlib['capacity']),
                            (usedcolor, 0, dstlib['used']),
                            ])
        else:
            defaultcanv = True
            updateitem(self.info, 'No game selected.')

    def window(self):
        w = tk.Tk()
        w.resizable(0,1)
        w.minsize(600,300)
        self.window = w

        w.grid_rowconfigure(3, weight=1)
        
        ltype = tk.Entry(w, width=50) #Path entry
        rtype = tk.Entry(w, width=50)

        ltype.bind('<Return>', lambda e: self.refresh())
        rtype.bind('<Return>', lambda e: self.refresh())
        
        ltype.grid(row=0)
        rtype.grid(row=0,column=1, columnspan=3)

        ltype.insert(0, defaultleft)
        rtype.insert(0, defaultright)

        llab = tk.Label(w)
        rlab = tk.Label(w)
        
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

        info = tk.Label(w, text='No game selected. Doubleclick one from either library.', width=42)
        info.grid(row=4, rowspan=2)

        bcopy = tk.Button(w, text='Copy', command=lambda: self.op('copy'), state='disabled')
        bcopy.grid(row=4, column=1, sticky='nwe')
        
        bmove = tk.Button(w, text='Move', command=lambda: self.op('move'), state='disabled')
        bmove.grid(row=4, column=2, sticky='nwe')

        bdel = tk.Button(w, text='Delete', command=lambda: self.op('delete'), state='disabled')
        bdel.grid(row=4, column=3, sticky='nwe')

        btool = tk.Button(w, text='Tools...', state='disabled', command=self.tools)
        btool.grid(row=5, column=1, sticky='nwe')
        
        bopen = tk.Button(w, text='Open folder', command=self.open, state='disabled')
        bopen.grid(row=5, column=2, sticky='nwe')

        bplay = tk.Button(w, text='Play game', command=lambda: self.play(), state='disabled')
        bplay.grid(row=5, column=3, sticky='nwe')

        popup = tk.Menu(w, tearoff=0)
        popup.add_command(label='Details in Steam', command = lambda: web('steam://nav/games/details/%s' % self.game['id']))
        popup.add_command(label='Verify cache', command = lambda: web('steam://validate/%s' % self.game['id']))
        popup.add_command(label='Backup to file...', command = lambda: web('steam://backup/%s' % self.game['id']))
        popup.add_command(label='Uninstall by ID...', command = lambda: self.op('deletesteam'))

        visit = tk.Menu(popup, tearoff=0)
        visit.add_command(label='SteamDB stats', command = lambda: web('https://steamdb.info/app/%s' % self.game['id']))
        visit.add_command(label='Store page', command = lambda: web('steam://url/StoreAppPage/%s' % self.game['id']))
        visit.add_command(label='Game hub', command = lambda: web('steam://url/GameHub/%s' % self.game['id']))
        visit.add_command(label='News page', command = lambda: web('steam://appnews/%s' % self.game['id']))

        popup.add_cascade(label='Visit...', menu=visit)
    
        self.ltype = ltype
        self.rtype = rtype
        self.llis = llis
        self.rlis = rlis
        self.llab = llab
        self.rlab = rlab
        self.lbar = lbar
        self.rbar = rbar
        self.info = info
        self.popup = popup
        
        self.bcopy = bcopy
        self.bmove = bmove
        self.bdel = bdel
        self.bopen = bopen
        self.bplay = bplay
        self.btool = btool        

    def __init__(self):
        self.window()
        self.game = False
        self.refresh()
        
        

if __name__ == '__main__':
    win = Window()
    win.window.mainloop()
