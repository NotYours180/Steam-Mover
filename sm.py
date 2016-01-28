import re
import os
import shutil
import threading

def thread(func, *args, **kwargs):
    thread = threading.Thread(target=func, args=args, kwargs=kwargs)
    thread.start()
    return thread

def acfgetreg(string, key):
    '''ACF property extracting regular expression'''
    found = re.findall('"%s"\s+"(.+)"' % key, string)
    if found:
        return found[0]
    else:
        return False

def dirsize(path):
    '''Gets bytes used by directory and amount of files.'''
    if os.path.isfile(path):
        return os.path.getsize(path)
    
    totalsize = 0
    totalcount = 0
    for dirpath, dirs, files in os.walk(path):
        for file in files:
            file = os.path.join(dirpath, file)
            try:
                size = os.path.getsize(file)
            except OSError:
                continue
            
            totalcount += 1
            totalsize += os.path.getsize(file)
    
    return totalsize, totalcount

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
                if ('steam.dll' in files or 'Steam.dll' in files) and 'steamapps' in dirs:
                    path = path_
                    break
            else: #No result
                return False
    
    return os.path.realpath(path)


class Operation:
    '''Folder copying operation w/ status. Does not attempt to see if free space is available.'''

    def copy(self, src, dst):
        '''Copies SRC to DST, updates internal stats.'''
        relsrc = os.path.relpath(src, self.src) # Relative source path for display
        size = os.path.getsize(src) #Size of file to be copied

        self._status('Copying file %s' % relsrc)
        try:
            shutil.copy2(src, dst, follow_symlinks=False)
        except FileNotFoundError:
            return None
        self.copysize += size
        self.copycount += 1
    
    def start(self):
        '''Starts operation.'''
        self._status('Scanning tree')
        
        for dirpath, dirs, files in self.list:
            for d in dirs:
                newpath = os.path.join(self.dst, d) #Get new destination folder
                
                if not os.path.exists(newpath):
                    os.makedirs(newpath) #Make directory if nonexistent
                    
            relpath = os.path.relpath(dirpath, self.src)
            newpath = os.path.join(self.dst, relpath) #Get destination again
            
            for file in files:
                file = os.path.realpath(os.path.join(dirpath, file))
                self.copy(file, newpath)

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
        
        self.size, self.count = dirsize(src) #Bytes to copy
        self.copysize = self.copycount = 0 # Bytes copied
