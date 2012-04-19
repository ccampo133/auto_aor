# $Author: ccampo $
# $Revision: 31 $
# $Date: 2009-06-18 09:55:27 -0400 (Thu, 18 Jun 2009) $
# $HeadURL: file:///home/esp01/svn/code/auto_aor/trunk/circorbphase.py $
# $Id: circorbphase.py 31 2009-06-18 13:55:27Z ccampo $

def circorbphase(teph, period, start, last, toff=0, evphase=0, errphase=0):
    """
NAME:
      circorbphase

PURPOSE:
      This function calculates the times when an orbit reaches
      a given phase.  It is useful for caucluating times of
      transit and given eclipse for extrasolar planets.  THE
      ORBIT IS ASSUMED CIRCULAR!

INPUTS:
      teph:    Time of transit and error; 2-element array (Julian day)
      
      period:  Period of planet and error; 2-element array (days)
            
      start:   Date of start of list (Julian day)
      
      last:    Date of end of list (Julian day)

      toff:    Optional parameter; added to teph to get julian date.
               (days, default is 0)

      evphase: Optional parameter; keyword param; phase of event to
               calculate (default 0 - primary eclipse)

OUTPUTS:
      Returns an array of orbital event Julian dates.

RESTRICTIONS:
      Accepts only Numpy arrays, lists, and tuples as input
      on many of the parameters.
      
      Error values MUST be passed in input (2-element arrays).
      
      Values MUST be double precision (float64 is default).

EXAMPLE/TEST:

import numpy as np
import julday as jd
import circorbphase as cop 
import circorbphase as cop
teph   = np.array([2454746.28890, 0.0007])
toff   = 0.
period = np.array([2.2437563, 0.000009])
tdur   = np.array([8246., 216.]) / 86400.
planet = 'wasp-14b'
obswin = np.array([\
[jd.julday(2,17,2009,17,57,0), jd.julday(4, 6, 2009, 20, 23, 0)],\
[jd.julday(7,22,2009, 5,55,0), jd.julday(9, 10, 2009, 1, 7,  0)]])
event  = 'full eclipse'
evphase = 0.48375
obsdur = tdur[0] * 2. * 86400.
ctrshift = 0
startwin = 30. * 60.
start = obswin[0][0]
last = obswin[0][1]
ecl = cop.circorbphase(teph, period, start, last, toff, evphase)

SIDE EFFECTS:
      Numpy is imported.

NOTES:
      Adapted from circorbphase.pro by Dr. Joseph Harrington,
      University of Central Florida.  The original routine
      is written in IDL.
     
MODIFICATION HISTORY:
      2009-01-07   0.1    Christopher Campo, UCF    Initial version
                         ccampo@gmail.com

    """
    import numpy as np

    # calculate orbital phase of starting time
    # force that and event phase to range (-1,1)
    div    = (start - toff - teph[0]) / period[0]
    ephase = evphase % 1

    # tricky; IDL uses sign of the dividend, where Python
    # seems to use the sign of the divisor.
    if div < 0:
        phasestart = div % -1.
    else:
        phasestart = div % 1.

    # phase adjustment from start time to first event, range (-1,0]
    phadj = ephase - phasestart
    phadj -= np.ceil(phadj)

    # ensure that happens before start
    phadj -= 1.

    # time of an event before start
    first = start + phadj * period[0]

    # covering number of events
    nev = np.ceil((last-start) / period[0]) + 2
    
    # lists of event times and errors
    event = first + (period[0] * np.arange(0, nev, 1, dtype=np.float64))

    error = np.sqrt((period[1] * (event - (toff + teph[0])) / period[0])**2\
                         + teph[1]**2 + (period[0]*errphase)**2)
    
    #error = np.sqrt((period[1] * (event - (toff + teph[0])) / period[0])**2\
    #                     + teph[1]**2 + errphase**2)

    #trim to start and last
    condition = (event > start) & (event < last)
    indices   = np.where(condition)
    event     = event[indices]
    error     = error[indices]

    return np.array((event, error))
