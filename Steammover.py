version = 1.11 #Upgrade Library Cleaner's capabilities
# Version 1.1: Add library-cleaning resources
# Version 1.0: release

import sm
import re
import os
import shutil
thread = sm.thread

import tkinter as tk
import tkinter.messagebox as ask
from webbrowser import open_new_tab as web
import urllib.request

thiscodeurl = 'https://raw.githubusercontent.com/yunruse/Steam-Mover/master/Steammover.py'

def checkupdate():
    try:
        data = urllib.request.urlopen(thiscodeurl).read().decode()
    except urllib.error.HTTPError: #Not found, or not present
        return False, ''
    regex = re.findall('version = ([0-9\.]+) #(.+)\n', data)
    if regex:
        ver, log = regex[0]
        if float(ver) > version:
            return ver, log
        else:
            return False, ''
    else:
        return False, ''

bgcolor = '#dddddd'
usedcolor = '#000000'
withcolor = '#448844'
ohnecolor = '#ff4444'

defaultlist = ["Library not found.",
        "Not sure where it is? Try providing a home path", "and we'll try to scan for a library."]

redundantfolders = ['dotnet', '_commonredist', '.*directx.*', 'dotnetfx' 'redist', 'dependencies',
                     'directx_redist', 'vcredist.*', 'installers', 'dxmin']

redundantfiles = ['.*redist\.msi', '.*dotNet.*\.exe']



for i in ('C:/Program Files (x86)/Steam/','C:/Program Files/Steam/',
          '~/Library/Application Support/Steam/', '~/.local/share/Steam'):
    # Find Steam library
    configpath = os.path.join(i, 'steamapps', 'libraryfolders.vdf') #List of other libraries
    if os.path.isfile(configpath): #Config exists; set as default
        defaultleft = i
        with open(configpath) as f: #Set right path:
            for line in f.readlines():
                result = re.findall('"\d+"\s+"(.+)"', line) #Scan lines for numbered paths indicating libraries 
                if result:
                    result = result[0]
                    result = os.path.realpath(result).replace('\\\\','\\') #Normalise escapes
                    if result != defaultleft:
                        defaultright = result
                        break
            else: #none found
                defaultright = ''
        break
else:
    defaultleft = ''

def updateitem(box, item):
    '''Updates a tkinter item with given text or iterable.'''
    if type(box) == tk.Label:
        box.config(text=item)
    else:
        box.delete(0, 'end')
        if type(item) == str:
            box.insert('end', item)
        else:
            for i in item:
                box.insert('end', i)

class DriveClean:
    def __init__(self, main):
        self.main = main
        window = self.window = tk.Toplevel(main.window)
        window.resizable(0,0)
        window.protocol('WM_DELETE_WINDOW', self.hide)
        self.hide()

        tk.Label(window, text="Steam Mover can attempt to remove some redundant files (like\nDirectX installation files.) If you clean a drive with a game you\nhaven't run yet, try verifyïng its cache (Tools > verify cache)\nto get them back.",                 width=50).grid()

        self.path = tk.Entry(window)
        self.path.grid(row=1, sticky='we')
        self.path.bind('<Return>', lambda e: thread(self.clean))

        self.button = tk.Button(window, text='Clean library', command=lambda: thread(self.clean))
        self.button.grid(row=2, sticky='we')

        self.doing = False #No operation in progress

    def clean(self, event=None):
        self.title() #Clear title
        if self.doing:
            return None
        
        inp = self.path.get()
        path = getpath(inp)
        if not path:
            print("Can't find library at path '%s'" % inp)
            self.title("can't find library")
            return None

        self.button.config(state='disabled')
        self.doing = True
        
        path = os.path.join(path, 'steamapps', 'common')
        size = sm.dirsize(path)
        
        for paths, folders, files in os.walk(path):
            for f in folders:
                for i in redundantfolders:
                    match = re.findall(i, f.lower())
                    if match:
                        f = os.path.join(paths, match[0])
                        if os.path.isdir(f):
                            self.title(os.path.relpath(f, path))
                            shutil.rmtree(f)
            for f in files:
                for i in redundantfiles:
                    match = re.findall(i, f.lower())
                    if match:
                        f = os.path.join(paths, match[0])
                        if os.path.isfile(f):
                            self.title(os.path.relpath(f, path))
                            os.remove(f)

        
        deleted = abs(size - sm.dirsize(path))        
        if deleted:
            print('%s saved from %s' % (sm.bytesize(deleted), path))
            self.title('%s saved' % sm.bytesize(deleted))
        else:
            print('%s has no redundant files' % path)
            self.title('Already clean :D')

        self.doing = False
        self.button.config(state='active')
        

    def title(self, text=None):
        if text:
            self.window.title('Library Cleaner – %s' % text)
        else:
            self.window.title('Library Cleaner')

    def show(self):
        self.title()
        self.window.deiconify()
        self.window.lift()
        updateitem(self.path, self.main.ltype.get())

    __call__ = show

    def hide(self):
        self.window.state('withdrawn')




class Window:
    '''Steam Mover default window'''
    def checkupdate(self):
        '''Checks for update'''
        self.title('Checking for updates...')
        ver, log = checkupdate()
        if ver:
            self.title('Update found!')
            if ask.askyesno('A new update is available!', 'Update %s is available (you are on %s.) Download? In this update:\n%s' % (ver, version, log)):
                web('https://github.com/yunruse/Steam-Mover/')
        else:
            self.title('No updates found')
        
    def canvas(self, canvas, cap, col):
        '''Update CANVAS with x proportional to CAP. COL is a list of (colour, x1, x2).'''
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
        
    def getlibrary(self, side):
        '''Fetches library of given side ('l' or 'r')'''
        updateitem(self.info, 'No game selected. Double-click one from either library.')
        side, inp, lab, lis, bar = (
            ('left', self.ltype, self.llab, self.llis, self.lbar),
            ('right', self.rtype, self.rlab, self.rlis, self.rbar))[side == 'r']
        
        self.title('Finding %s library' % side)
        path = sm.getpath(inp.get())
        updateitem(inp, path)
        
        if path:
            gamespath = os.path.join(path, 'steamapps')
            self.title('Scanning %s library' % side)
            capacity, used, free = shutil.disk_usage(path)

            games = [] # List of library's game IDs.
            
            for i in os.listdir(gamespath):
                if not (i.endswith('.acf') and i.startswith('appmanifest_')):
                    continue
                ID = i[12:-4]
                if not ID in self.sources:
                    acfpath = os.path.join(gamespath, i)
                    with open(acfpath) as f:
                        f = f.readlines()
                        for line in f:
                            if 'installdir' in line:
                                gamepath = re.findall('"installdir"\s+"(.+)"', line)[0]
                                gamepath = os.path.join(gamespath, 'common', gamepath)
                            elif 'name' in line:
                                name = re.findall('"name"\s+"(.+)"', line)[0]
                    
                    self.sources[ID] = {'name': name, 'path': gamepath}
                    
                games.append(ID)
                
                
            lib = {'capacity': capacity, 'free': free, 'used': used, 'games': games}

            self.canvas(bar, capacity, [
                       (bgcolor, 0, capacity),(usedcolor, 0, used)])
            updateitem(lab, '%s (%s free)' %
                       (sm.bytesize(capacity), sm.bytesize(free)))
            
            names = [self.sources[ID]['name'] for ID in games]
            updateitem(lis, sorted(names,
                        key = lambda x: x.lower().replace('the ','').replace('a ','')))
            
        else:
            lib = False
            updateitem(lab, 'No drive found')
            updateitem(lis, defaultlist)
            self.canvas(bar, 1, [(bgcolor,0,1)])

        
        if side == 'right':
            self.rlib = lib
        else:
             self.llib = lib
        
        self.title() # Clear title

    def title(self, update=None, percent=None):
        '''Update title from callback.'''
        if update:
            if percent:
                self.operation = percent
                title = '%.2f%% – %s' % (percent, update)
                
                
                if (percent <= 0) or (percent >= 100) or \
                    (percent > self.lastpercent + 0.2):
                    self.lastpercent = percent
                    self.window.title('Steam Mover – ' + title)
                    print(title.replace('Copying file ','').replace(' –',''))
            else:
                print(update)
                self.window.title('Steam Mover – ' + update)
        else:
            self.window.title('Steam Mover')
             

    def op(self, verb):
        '''Do operation on game.'''
        ID = self.game
        game = self.sources[ID]
        if self.operation == False and \
           ask.askyesno('%s game?' % verb,'Are you sure you want to %s %s?' %
                           (verb.lower(), self.sourcesgame['name']),
                            icon='warning', default='no'):
            self.operation = 0
            self.lastpercent = 0
            self.button('move', False)
            for i in (self.ltype, self.rtype):
                i.unbind('<Return>') #Disallow refreshing during operation

            if verb != 'Delete':
                sm.move(self.srclib, self.game, self.dstlib, callback=self.title)
                self.dstlib.append(ID)

            if verb == 'Move':
                self.title('Deleting original files', 100)
            
            if verb != 'Copy':
                sm.delete(self.srclib, game)
                self.srclib.remove(ID)

            for lib, lab, lis, bar in ((self.llib, self.llab, self.llis, self.lbar),
                                       (self.llib, self.llab, self.llis, self.lbar)):
                self.canvas(bar, capacity, [
                       (bgcolor, 0, capacity),(usedcolor, 0, used)])
                updateitem(lab, '%s (%s free)' %
                       (sm.bytesize(capacity), sm.bytesize(free)))
            
                names = [self.sources[ID]['name'] for ID in games]
                updateitem(lis, sorted(names,
                        key = lambda x: x.lower().replace('the ','').replace('a ','')))
            
            self.operation = False
            self.button() #Reset movement
            for i in (self.ltype, self.rtype):
                i.bind('<Return>', self.refresh) #Reällow refresh
        
    def button(self, category='move', state=True):
        '''Changes status for operation buttons.'''
        if category == 'move':
            btns = (self.bcopy, self.bmove)                    
        else:
            btns = (self.bopen, self.bplay, self.bdel, self.btool)
        for i in btns:
            i.config(state=['disabled', 'active'][state])

    def tools(self):
        '''Opens tools popup menu'''
        if self.game:
            x = self.window.winfo_rootx() + self.btool.winfo_x()
            y = self.window.winfo_rooty() + self.btool.winfo_y()
            self.popup.tk_popup(x,y, 0)

    def toggledrive(self):
        self.title()
        for i in (self.llab, self.rlab, self.lbar, self.rbar):
            if self.showdrives:
                i.grid_remove()
            else:
                i.grid()
        self.showdrives = not self.showdrives
            
        
    def select(self, side):
        if side == 'l':
            if not self.llib:
                return False
            lib = self.llib
            selectedgame = self.llis.get('active')
        else:
            if not self.rlib:
                return False
            lib = self.rlib
            selectedgame = self.rlis.get('active')
            
        for g in lib['games']:
            if self.sources[g]['name'] == selectedgame:
                game = self.sources[g]
                ID = g
                break
        else:
            updateitem(self.info, 'No game selected.')
            return None

        #Rest of block relies on game existing, naturally

        self.button('misc') #Allow single-library buttons
        self.game = game

        
        size = sm.dirsize(game['path'])
        
        if side == 'l':
            dstlib = self.rlib
            srclab = self.llab
            dstlab = self.rlab
            srcnam = 'left'
            dstnam = 'right'
            srcbar = self.lbar
            dstbar = self.rbar
        else:
            dstlib = self.llib
            srclab = self.rlab
            dstlab = self.llab
            srcbar = self.rbar
            dstbar = self.lbar
            srcnam = 'right'
            dstnam = 'left'
        
        name = game['name']
        if len(name) > 50:
            name = name[:50] + '...' #Truncate name for display
        
        needed = size - dstlib['free'] #Bytes needed on other drive

        #Update canvas for own game showing space taken
        self.canvas(srcbar, lib['capacity'],[
                   (bgcolor,0,lib['capacity']),(usedcolor, 0, lib['used']),
                   (ohnecolor, lib['used'] - size, lib['used'])
                   ])
        
        
        if needed < 0: #Can move to destination drive
            self.srclib = lib
            self.dstlib = dstlib
            
            self.button() #Allow movement to other library

            updateitem(self.info, '%s (%s side)\nSize: %s – ID: %s' % (
                name, srcnam, sm.bytesize(size), ID))

            self.canvas(dstbar, dstlib['capacity'],[
                        (bgcolor, 0, dstlib['capacity']), (usedcolor, 0, dstlib['used']),
                        (withcolor, dstlib['used'], dstlib['used'] + size)
                        ])
        else:
            self.button('move', False) #Disallow movement buttons
            
            updateitem(self.info, '%s\nSize: %s – %s more needed on %s library' % (
                name, sm.bytesize(size), sm.bytesize(needed), dstnam))
            
            self.canvas(dstbar, dstlib['capacity'],[
                        (ohnecolor, 0, dstlib['capacity']),
                        (usedcolor, 0, dstlib['used'])
                        ])


    def __init__(self):            
        self.window = window = tk.Tk()
        window.resizable(0,1)
        window.minsize(600,300)

        window.grid_rowconfigure(3, weight=1)

        #Path entry boxes
        ltype = tk.Entry(window, width=50)
        rtype = tk.Entry(window, width=50)

        ltype.bind('<Return>', lambda e: self.getlibrary('l'))
        rtype.bind('<Return>', lambda e: self.getlibrary('r'))
        
        ltype.grid(row=0)
        rtype.grid(row=0,column=1, columnspan=3)

        ltype.insert(0, defaultleft)
        rtype.insert(0, defaultright)

        #Sizing labels
        llab = tk.Label(window)
        rlab = tk.Label(window)
        
        llab.grid(row=1)
        rlab.grid(row=1,column=1, columnspan=3)

        #Canvases for size
        lbar = tk.Canvas(window, height=20, width=300) 
        rbar = tk.Canvas(window, height=20, width=300)

        lbar.grid(row=2)
        rbar.grid(row=2,column=1, columnspan=3)

        self.showdrives = True

        #Lists of games
        llis = tk.Listbox(window, width=50)
        rlis = tk.Listbox(window, width=50)

        llis.grid(row=3, sticky='ns')
        rlis.grid(row=3, column=1, sticky='ns', columnspan=3)

        llis.bind('<Double-Button-1>', lambda e: self.select('l'))
        rlis.bind('<Double-Button-1>', lambda e: self.select('r'))

        #Information label
        info = tk.Label(window, text='No game selected. Double-click one from either library.', width=42)
        info.grid(row=4, rowspan=2)

        #Buttons
        bcopy = tk.Button(window, text='Copy', command = lambda: thread(self.op, 'Copy'), state='disabled')
        bcopy.grid(row=4, column=1, sticky='nwe')
        
        bmove = tk.Button(window, text='Move', command = lambda: thread(self.op, 'Move'), state='disabled')
        bmove.grid(row=4, column=2, sticky='nwe')

        bdel = tk.Button(window, text='Delete', command = lambda: thread(self.op, 'Delete'), state='disabled')
        bdel.grid(row=4, column=3, sticky='nwe')

        btool = tk.Button(window, text='Tools...', command = self.tools, state='disabled')
        btool.grid(row=5, column=1, sticky='nwe')
        
        bopen = tk.Button(window, text='Open folder', command = lambda: os.startfile(self.game['path']), state='disabled')
        bopen.grid(row=5, column=2, sticky='nwe')

        bplay = tk.Button(window, text='Play game', command = lambda: web('steam://run/%s' % self.game['id']), state='disabled')
        bplay.grid(row=5, column=3, sticky='nwe')

        self.drivewin = DriveClean(self)
        
        #Menu bar
        menu = tk.Menu(window, tearoff=0)
        menu.add_command(label='Refresh libraries', command = lambda: (self.getlibrary(s) for s in 'lr'))
        menu.add_command(label='Check for updates', command = lambda: thread(self.checkupdate))
        menu.add_command(label='Library Cleaner...', command = self.drivewin.show)
        menu.add_command(label='Toggle drive display', command = self.toggledrive)
        menu.add_command(label='About...', command = lambda: ask.showinfo('Steam Mover version %s' % version, 'Copyright © 2016 Ami yun Ruse @yunruse. See LICENSE for legal stuff.'))
        window.config(menu=menu)

        #Tools menu popup
        popup = tk.Menu(window, tearoff=0)
        popup.add_command(label='Details in Steam', command = lambda: web('steam://nav/games/details/%s' % self.game['id']))
        popup.add_command(label='Verify cache', command = lambda: web('steam://validate/%s' % self.game['id']))
        popup.add_command(label='Backup to file...', command = lambda: web('steam://backup/%s' % self.game['id']))

        visit = tk.Menu(popup, tearoff=0)
        visit.add_command(label='SteamDB stats', command = lambda: web('https://steamdb.info/app/%s' % self.game['id']))
        visit.add_command(label='Store page', command = lambda: web('steam://url/StoreAppPage/%s' % self.game['id']))
        visit.add_command(label='Game hub', command = lambda: web('steam://url/GameHub/%s' % self.game['id']))
        visit.add_command(label='News page', command = lambda: web('steam://appnews/%s' % self.game['id']))

        popup.add_cascade(label='Visit...', menu=visit)

        self.ltype = ltype
        self.rtype = rtype
        self.llab = llab
        self.rlab = rlab
        self.lbar = lbar
        self.rbar = rbar
        self.llis = llis
        self.rlis = rlis
        self.info = info
        self.popup = popup
        self.bcopy = bcopy
        self.bmove = bmove
        self.bdel = bdel
        self.bopen = bopen
        self.bplay = bplay
        self.btool = btool
        
        
        
        self.game = False
        self.operation = False # If true, don't do other operations!
        self.sources = {}

        

        thread(self.getlibrary('l'))
        thread(self.getlibrary('r'))
        
        self.loop = window.mainloop
        

if __name__ == '__main__':
    win = Window()
    win.loop()
