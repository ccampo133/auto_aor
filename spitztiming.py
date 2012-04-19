# $Author: ccampo $
# $Revision: 31 $
# $Date: 2009-06-18 09:55:27 -0400 (Thu, 18 Jun 2009) $
# $HeadURL: file:///home/esp01/svn/code/auto_aor/trunk/spitztiming.py $
# $Id: spitztiming.py 31 2009-06-18 13:55:27Z ccampo $
import numpy as np
import caldat

def spitztiming(jdstart, jdend):
    """
NAME:
      SPITZTIMING

PURPOSE:
      This function prints a list, in Spitzer AOR format, of timing
      constraints.  Also returns the output as a string.  Originally
      adapted from Dr. Joe Harrington's IDL routine, spitztiming.pro.

INPUTS:
      jdstart: Julian date of the start of the timing window (may be array).
      jdend:   Julian date of the end of the timing window (may be array).

OUTPUTS:
      This function returns a list of strings. Each cell of the list represents
      a separate constraint.

SIDE EFFECTS:
      None.

RESTRICTIONS:
     Numpy must be imported.
     Caldat must be imported.
     Jdstart and Jdend must both be arrays of the same shape.  Each element of
     of jdstart must be less than the corresponding element of jdend.

EXAMPLE/TEST:
     import numpy
     from julday import *
     from spitztiming import *
     print spitztiming(julday(10, 10, 2005, 2, 34, 56),
                       julday(12, 12, 2006, 3, 45, 34)

MODIFICATION HISTORY:
2008-12-29 0.1  Christopher Campo, UCF     Initial version.
                ccampo@gmail.com

2009-01-06 0.2  Christopher Campo, UCF     Added support for arrays
                ccampo@gmail.com

2009-01-06 0.3  Christopher Campo, UCF     Added support for scalars
                ccampo@gmail.com
    """
    
    # default assumes input is a scalar
    scalar = True

    # check if input is an array
    if type(jdstart) == np.ndarray and type(jdend) == np.ndarray:
        scalar = False
        # check shape of arrays
        if(jdstart.shape != jdend.shape):
            raise TypeError, 'Error: arrays jdstart and jdend must have the same shape'
    else:
        try:
            # simple arithmetic test; lists and tupples do not
            # support this action however, and will throw an
            # exception.
            test = jdend * jdstart
        except:
            raise IOError, 'Error: input must be either scalars or arrays'
  
    dif = jdend - jdstart

    if scalar == False:
        # make sure each end date is after the start date
        difar = dif < 0
        if(difar.all() == True):
            raise TypeError, 'Error: each end time must be later than corresponding start time'
    elif dif < 0:
        raise TypeError, 'Error: each end time must be later than corresponding start time'

    if scalar == False:
        # number of timing constraints to be generated
        ntime = jdstart.size
    else:
        ntime = 1

    # the list of strings (constraints) to be returned
    tlist = []
  
    # converts julian to gregorian
    sdate = caldat.caldat(jdstart, verbose=True)
    edate = caldat.caldat(jdend, verbose=True)

    # append the list with each timing constraint;
    # loops through the entire range of timing constraints.
    for i in range(ntime):
        if scalar == True:
            hr  = np.array([sdate[3], edate[3]])
            min = np.array([sdate[4], edate[4]])
            sec = np.array([sdate[5], edate[5]])
        else:
            hr  = np.array([sdate[i][3], edate[i][3]])
            min = np.array([sdate[i][4], edate[i][4]])
            sec = np.array([sdate[i][5], edate[i][5]])

        # FINDME: 7/20/2010 remove 60 seconds bug
        if np.round(sec[0]) == 60:
            min[0] += 1
            sec[0]  = 0
        if np.round(sec[1]) == 60:
            min[1] += 1
            sec[1]  = 0

        # FINDME: 7/28/2011 remove 60 minute bug
        if np.round(min[0]) == 60:
            hr[0] += 1
            min[0] = 0
        if np.round(min[1]) == 60:
            hr[1] += 1
            min[1] = 0

        # get start and end times
        stvals = (hr[0], min[0], sec[0])
        etvals = (hr[1], min[1], sec[1])
        stime  = '%02d:%02d:%02.0f' % (stvals) 
        etime  = '%02d:%02d:%02.0f' % (etvals)
        
        if scalar == False:
            str_var = (i+1, sdate[i][2], sdate[i][0], sdate[i][1], stime, \
                         edate[i][2], edate[i][0], edate[i][1], etime)
        else:
            str_var = (i+1, sdate[2], sdate[0], sdate[1], stime, edate[2],\
                         edate[0], edate[1], etime)
      
        tstr = 'TIMING%d:  START_DATE=%d %s %2d, START_TIME=%8s, END_DATE=%d %s %2d, END_TIME=%s' % str_var
        tlist.append(tstr)
      
    # the list of strings (timing constraints)
    return tlist
