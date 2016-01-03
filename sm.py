import re
import os
import shutil
import threading

def thread(func, *args, **kwargs):
    thread = threading.Thread(target=func, args=args, kwargs=kwargs)
    thread.run()
    return thread

def acfgetreg(string, key):
    '''ACF property extracting regular expression'''
    found = re.findall('"%s"\s+"(.+)"' % key, string)
    if found:
        return found[0]
    else:
        return False

def dirsize(path):
    '''Gets size of given directory.'''
    total = 0
    for dirpath, dirs, files in os.walk(path):
        for file in files:
            file = os.path.join(dirpath, file)
            total += os.path.getsize(file)
    return total

def bytesize(num, binary=True):
    '''Given a number of bytes, human-formats as binary(kibi, mebi; *1024) or non-binary (kilo, mega; *1000) up to yotta/yobibytes.'''
    if binary:
        divisor = 1024.0
    else:
        divisor = 1000.0
    
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < divisor:
            return "%3.1f %s%sB" % (num,  unit, 'i'*binary*bool(unit))
        num /= divisor
    return "%.1f Y%sB" % (num, 'i' * binary)

def buildfolder(path):
    '''Taking path to folder containing steamapps, returns stats and list of games.'''
    total, used, free = shutil.disk_usage(path)
    games = {}
    
    games_path = os.path.join(path, 'steamapps')
    files = [x for x in os.listdir(games_path)
             if re.findall('appmanifest_\d+.acf', x)] #List of valid ACF files.
    
    for acfname in files:
        acfpath = os.path.join(games_path, acfname)
        f = ''.join(open(acfpath).readlines())
        
        gamepath = os.path.join(games_path, 'common', acfgetreg(f, 'installdir'))
        size = dirsize(gamepath)
        gameid = re.findall('appmanifest_(\d+).acf', acfname)[0] #First result = ID
        name = acfgetreg(f, 'name')

        games[gameid] = {'name': name, 'size': size, 'path': gamepath, 'acfpath': acfpath, 'id': gameid}

    return {'path': path, 'capacity': total, 'free': free, 'used': used, 'games': games}


class Operation:
    '''Folder copying operation w/ status. Does not attempt to see if free space is available.'''

    def _copy(self, src, dst):
        '''Copies SRC to DST, updates internal stats.'''
        relsrc = os.path.relpath(src, self.src) # Relative source path for display
        size = os.path.getsize(src) #Size of file to be copied

        self._status('Copying file %s' % relsrc)
        shutil.copy2(src, dst, follow_symlinks=False)
        self.copied += size
    
    def start(self):
        '''Starts operation.'''
        self._status('Scanning tree')
        
        for dirpath, dirs, files in self.list:
            for d in dirs:
                d = os.path.join(dirpath, d) #Make absolute
                relpath = os.path.relpath(d, self.src) #Get relative to top source
                newpath = os.path.join(self.dst, relpath) #Get new destination folder
                
                if not os.path.exists(newpath):
                    os.makedirs(newpath) #Make directory if nonexistent
                    
            relpath = os.path.relpath(dirpath, self.src)
            newpath = os.path.join(self.dst, relpath) #Get destination again
            
            for file in files:
                file = os.path.realpath(os.path.join(dirpath, file)) #Make newpath
                thread(self._copy, file, newpath)

    def _status(self, status):
        '''Runs callback with status and attempts to stop divison by zero errors.'''
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


def move(sender, game, library, delete=True, callback=None):
    '''Moves game with ID `game` from library `sender` to `library`. If `delete` is true, deletes original copy.
    If callback is set, every operation done does callback(statusmsg, percentdone)'''
    
    assert library['path'] != sender['path'], 'The libraries are identical.'
    
    game = sender['games'][str(game)]

    needed = game['size'] - library['free'] #Needed in destination drive to move. If below zero, can copy.
    
    assert needed < 0, (
           'You need more space (%s) on the recipient drive to copy all of the game.' % bytesize(needed))

    srcpath = game['path']
    gamepath = os.path.basename(game['path']) # Name of folder
    dstpath = os.path.join(library['path'], 'steamapps', 'common', gamepath)

    if os.path.isdir(dstpath):
        callback('Deleting existent paths', 0)
        shutil.rmtree(dstpath)

    copyop = Operation(srcpath, dstpath, library['path'])
    if callable(callback):
        copyop.callback = lambda status: callback(status, 100*(copyop.copied/copyop.size))
    copyop.start()

    if callable(callback):
        callback('Copying metadata file', 100)
    shutil.copy2(game['acfpath'], os.path.join(library['path'], 'steamapps')) # Copy ACF file

    if delete:
        callback('Deleting original files', 100)
        shutil.rmtree(game['path'])
        os.remove(game['acfpath'])


def delete(library, ID):
    '''Deletes game with ID from library. No callback.'''
    game = library['games'][str(ID)]

    path = os.path.realpath(game['path'])
    acfpath = os.path.realpath(game['acfpath'])

    if os.path.exists(path):
        shutil.rmtree(path)
    if os.path.exists(acfpath):
        os.remove(acfpath)
    
