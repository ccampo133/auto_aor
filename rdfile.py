import numpy    as np
import julday   as jd
import datetime as dt

def rdfile(fname):
    """
    Read, parse, and return the contents of an observation
    preparation file (aai, tep) as a dictionary.

    Parameters
    ----------
    fname :  string
        The .tep file to be read.  May include the path as well, if it
        is not in the current working directory.

    Returns
    -------
    data : dict
        A dictionary of the contents of the specified file. Each key of
        the dictionary is the respective parameter in the file. The
        parameters have been lowercased for convience.  If the file contains
        parameters with uncertainties, each key's value is a 2-tuple, where
        the first index represents the value and the second index reprxesents
        the uncertainty of that value.  Otherwise, the key's value is just
        that.

    Example
    -------
    >>> from readtep import *
    >>> tepfile = open('/home/me/tep.tep', 'r') # open file to READ
    >>> tepdata = readtep(tepfile)
    >>> tepdata
    {'a': ('-1', '-1'),
    'announcedate': ('-1', '-1'),
    'date': ('-1', '-1'),
    ...
    }

    Revisions
    ---------
    2010-05-18  ccampo : fixed doc string; made general (aai, tep)
    2009-01-20  Christopher Campo, UCF (ccampo@gmail.com)
                Initial version
    """
    # open the file
    handle = open(fname, 'r')

    data = {} # empty dictionary

    # read the file, line by line
    for line in handle:
        line = line.rstrip()  # strip off \n

        # ignore comments and blank lines
        if len(line) < 1:
            continue
        if line[0] == "#":    # comments start with '#' char
            continue

        # create a list of words on the particular line.
        # each index of parts is a word on the line.
        parts = line.split()

        # removes the comments at the end of each line.
        # makes the list 3 fields long as a side effect.
        for i, item in enumerate(parts):
            if item == "#":
                del parts[i:len(parts)]
        
        key = parts[0].lower() # the parameter

        # check if an uncertainty exists
        if len(parts) == 3:
            # try block converts every numerical value to a float. All others
            # are left as strings
            try:
                # data tup          value       error
                data[key] = (float(parts[1]), float(parts[2]))
            except ValueError:
                data[key] = (parts[1], float(parts[2])) # leaves strings
        else:
            try:
                data[key] = float(parts[1])
            except ValueError:
                data[key] = parts[1]  # leaves strings
            
    handle.close()  # done; close the file
    return data

def rdvis(fname, juldat=False):
    """
SYNTAX:
    viswindows = readvis(filename)

PURPOSE:
    To read, parse, and return the contents of a Spitzer Target Visibility
    Windows (.vis) file.

INPUTS:
    fname: The .vis file to be read.  May include the path as well, if it
           is not in the current working directory.
    
       jd: Optional param; if specified as True, it will return an array
           of Julian dates.

OUTPUTS:
    This function returns a 3D array containing each visibility window 
    contained in the .vis file that is passed as input.  The format of 
    the output is as follows:

    Each row holds an array of windows.  The columns of each row represent
    the window open and close, respectively.  Each window is also an array,
    in which the fields are:
    [month, day, year, hours, minutes, seconds]

    The shape will always be (n, 2, 6) where n is the number of window sets
    (open and close) you have.

RESTRICTIONS:
    Input MUST be a text file in the form .vis provided by Spitzer's SPOT.

    Numpy must be installed and imported.
    
    Julday must be installed and imported.

SIDE EFFECTS:
    None

EXAMPLE/TEST:

import readvis as rv
vis = rv.readvis(example.vis)
print vis

MODIFICATION HISTORY:
2009-02-01 0.1    Christopher Campo, UCF    Initial Version
                  ccampo@gmail.com 

2009-02-10 0.2    Christopher Campo, UCF    Only returns dates from today+
                  ccampo@gmail.com
    """
    fin = open(fname, 'r')

    flag = False
    
    # used to convert words to numbers
    months = {
        'Jan': 1.,
        'Feb': 2.,
        'Mar': 3.,
        'Apr': 4.,
        'May': 5.,
        'Jun': 6.,
        'Jul': 7.,
        'Aug': 8.,
        'Sep': 9.,
        'Oct': 10.,
        'Nov': 11.,
        'Dec': 12.,
        }
    
    windows = []

    for line in fin:
        line = line.rstrip()
        
        # ignore comments and white space
        if len(line) < 1:
            continue
        elif line[0] == '#':
            continue
        
        # split the line into words
        parts = line.split()

        # everything after the word windows becomes data we need
        if parts[0].lower() == 'windows':
            flag = True
            continue

        if flag == True:
            win = []

            hmd_open  = parts[3].split(':') 
            hmd_close = parts[-2].split(':') 
            
            # window open list
            mon     = months[parts[1]]
            day     = float(parts[2])
            year    = float(parts[0])
            hr      = float(hmd_open[0])
            min     = float(hmd_open[1])
            sec     = float(hmd_open[2])
            openwin = [mon, day, year, hr, min, sec]

            # window close list
            mon      = months[parts[-4]]
            day      = float(parts[-3])
            year     = float(parts[-5])
            hr       = float(hmd_close[0])
            min      = float(hmd_close[1])
            sec      = float(hmd_close[2])
            closewin = [mon, day, year, hr, min, sec]
        
            # the date NOW (to compare)
            now  = dt.datetime.now()
            now  = jd.julday(now.month, now.day, now.year, now.hour, \
                                 now.minute, now.second)
            
            # current date, in Julian
            crnt = jd.julday(closewin[0], closewin[1], closewin[2], \
                                 closewin[3], closewin[4], closewin[5])

            # check if date is in the past
            if now - crnt <= 0:
                win.append(openwin)
                win.append(closewin)
                windows.append(win)

    fin.close()
    windows = np.array(windows, dtype=np.float64)

    if juldat == False:
        return windows
    else:        
        # the final array of julian dates
        dates = []

        # loop thru each window, convert to dates.
        for i in range(len(windows)):
            temp = []
            for k in range(len(windows[i])):
                j = jd.julday(windows[i][k][0], windows[i][k][1], \
                                  windows[i][k][2], windows[i][k][3], \
                                  windows[i][k][4], windows[i][k][5])
                temp.append(j)
            dates.append(temp)

        return np.array(dates, dtype=np.float64)
