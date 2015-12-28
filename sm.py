import json
import re
import os
import shutil
import threading

getreg = lambda f, x: re.findall('"%s"\s+"(.+)"' % x, f)[0]

def dirsize(path):
    total = 0
    for dirpath, n, files in os.walk(path):
        for file in files:
            file = os.path.join(dirpath, file)
            total += os.path.getsize(file)
    return total

def bytesize(num):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f %sB" % (num, unit)
        num /= 1024.0
    return "%.1f %sB" % (num, 'Yi')

def buildfolder(path):
    '''Taking steamapps path, builds a list of games'''
    total, used, free = shutil.disk_usage(path)
    games = {}
    
    games_path = os.path.join(path, 'steamapps')
    files = [x for x in os.listdir(games_path) if re.findall('appmanifest_\d+.acf', x)]
    
    for acfname in files:
        acfpath = os.path.join(games_path, acfname)
        f = ''.join(open(acfpath).readlines())
        
        gamepath = os.path.join(games_path, 'common', getreg(f, 'installdir'))
        size = dirsize(gamepath)
        gameid = re.findall('appmanifest_(\d+).acf', acfname)[0]
        name = getreg(f, 'name')

        games[gameid] = {'name': name, 'size': size, 'path': gamepath, 'acfpath': acfpath, 'id': gameid}

    return {'path': path, 'capacity': total, 'free': free, 'used': used, 'games': games}


class MoveOperation:
    '''Folder copying operation w/ status. Does not attempt to see if free space is available.'''

    def copy(self, src, dst):
        relsrc = os.path.relpath(src, self.src) # Relative source path for display
        size = os.path.getsize(src) #Size of file to be copied

        self.status_('Copying file %s' % relsrc)
        shutil.copy2(src, dst, follow_symlinks=False)
        self.copied += size
    
    def start(self):
        self.status_('Scanning tree')
        
        for dirpath, dirs, files in self.list:
            for d in dirs:
                d = os.path.join(dirpath, d)
                relpath = os.path.relpath(d, self.src)
                newpath = os.path.join(self.dst, relpath)
                
                if not os.path.exists(newpath):
                    os.makedirs(newpath)
                    
            relpath = os.path.relpath(dirpath, self.src)
            newpath = os.path.join(self.dst, relpath)
            
            for file in files:
                file = os.path.realpath(os.path.join(dirpath, file))
                thread = threading.Thread(target=lambda: self.copy(file, newpath))
                thread.run()

    def status_(self, status):
        self.status = status
        if callable(self.callback):
            try:
                self.callback(status)
            except ZeroDivisionError: # Presumably, (deleted/size) was referenced; it must ergo be zero
                self.size = self.copied = 1
                self.callback(status)
        
    def __init__(self, src, dst, callback=None):
        '''Copies folder SRC to DST. Whenever status updates, calls CALLBACK with it, if existent.'''
        if os.path.exists(dst):
            raise FileExistsError
            return None
        
        self.src = src
        self.dst = dst
        self.callback = callback

        self.list = os.walk(self.src) #List of files
        
        self.size = dirsize(src) #Bytes to copy
        self.copied = 0 # Bytes copied

def move(sender, game, library, delete=True, callback=lambda x,y:...):
    '''Moves game with ID `game` from library `sender` to `library`. If `delete` is true, deletes original copy.
    If callback is set, every operation done does callback(statusmsg, percentdone)'''
    
    if library['path'] == sender['path']:
        raise Exception('The libraries are identical.')
    
    game = sender['games'][str(game)]

    needed = game['size'] - library['free']
    if needed > 0:
        raise Exception('You need more space (%s) on the recipient drive to copy all of the game.' %
                        bytesize(needed))

    srcpath = game['path']
    gamepath = os.path.basename(game['path'])
    dstpath = os.path.join(library['path'], 'steamapps', 'common', gamepath)
    
    copyop = MoveOperation(srcpath, dstpath, library['path'])
    copyop.callback = lambda x: callback(x, 100*(copyop.copied/copyop.size))
    threading.Thread(target=lambda: copyop.start()).run()

    callback('Copying metadata', 100)
    
    shutil.copy2(game['acfpath'], os.path.join(library['path'], 'steamapps')) # Copy ACF

    if delete:
        shutil.rmtree(game['path'])
        os.remove(game['acfpath'])

def delete(library, game):
    '''Deletes game with ID `game` from library `library`. No callback.'''
    game = library['games'][str(game)]

    path = os.path.realpath(game['path'])
    acfpath = os.path.realpath(game['acfpath'])

    if os.path.exists(path):
        shutil.rmtree(path)
    if os.path.exists(acfpath):
        os.remove(acfpath)
    
