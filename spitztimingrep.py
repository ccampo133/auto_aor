# $Author: ccampo $
# $Revision: 257 $
# $Date: 2010-04-22 17:54:57 -0400 (Thu, 22 Apr 2010) $
# $HeadURL: file:///home/esp01/svn/code/auto_aor/trunk/spitztimingrep.py $
# $Id: spitztimingrep.py 257 2010-04-22 21:54:57Z ccampo $
import numpy as np

def spitztimingrep(planet, event, evphase, obsdur, startwin, obswin,\
                       teph, period, toff=0, ctrshift=0,\
                       type='ingress', errphase=0, ecldur=None):
    """
NAME:
      spitztimingrep

PURPOSE:
      This function calculates when planetary transit and eclipse
      events occur within a set of observing windows.  It also
      prints the corresponding Spitzer timing constraints in AOR
      format.  It returns the timing constraint string list. It can
      also return the event mid-times with their error estimates.

INPUTS:
      planet:   String name of the planet

      event:    String name of the event
      
      evphase:  Float, in range [0,1), giving phase of event to
                be reported.
      
      obsdur:   Duration (in seconds) of observations

      startwin: Duration (in seconds) of observation start-time
                window.

      obswin:   [2,nwin] array of Julian dates for the start and end
                of each observing window.  Only events within these 
                pairs of times will be returned.

      teph:     Passed to routine circorbphase; see that routine's header.

      period:   Passed to routine circorbphase; see that routine's header.

      toff:     Optional parameter; Passed to routine circorbphase; see 
                that routine's header.

      ctrshift: Shift (in seconds) of event center relative to observation
                center.  Positive shift puts more time before the event.

      type:     Optional; the type of constraints you want returned
                (ingress / egress) or the mid-times (midtimes). All
                other inputs will return the ingress timing constraints
                by default.

OUTPUTS:
      This function returns the spitzer timing constraint string
      for ingress or egress OR the event mid-times with error estimates.

RESTRICTIONS:
      Numpy must be installed, and the routines circorbphase, spitztiming,
      and caldat must be in Python's search path.

SIDE EFFECTS:
      None.

EXAMPLE/TEST:

import spitztimingrep as sptr
import julday as jd
import numpy as np

teph = np.array([24445678.0, 0.04])
period = np.array([2.18575, 0.000003])
planet = 'mars'
obswin = np.array([[jd.julday(11, 12, 2005, 15, 34, 0),\
                        jd.julday(12, 27, 2005, 8, 14, 0)]])
obsdur = 6 * 3600.
startwin = 60. * 60.
evphase = .5
event = 'secl'
sptr.spitztimingrep(planet, event, evphase, obsdur, startwin, obswin, \
                    teph, period)


NOTES:
      This routine is adopted from Dr. Joseph Harrington's original IDL
      routine, spitztimingrep.pro.

MODIFICATION HISTORY:
     2009-01-07   0.1    Christopher Campo, UCF    Initial version
                         ccampo@gmail.com

     2009-01-11   0.2    Christopher Campo, UCF    Added mid-times
                         ccampo@gmail.com
    """
    import numpy as np
    import circorbphase as cop
    import spitztiming as st
    import caldat as cal

    if ecldur == None:
        ecldur = obsdur - 3600.
        
    ictrshift = 0

    if ctrshift != 0:
        ictrshift = ctrshift

    s2d = 1. / 86400. # conversion factor for seconds to days
  
    for i in range(len(obswin)):
        if i == 0:
            ecl = cop.circorbphase(teph, period, obswin[i][0], obswin[i][1], \
                                       toff, evphase, errphase=errphase)
        else:
            ecl = np.concatenate((ecl, cop.circorbphase(teph, \
                                                            period, obswin[i][0], \
                                                            obswin[i][1], toff, \
                                                            evphase, errphase=errphase)), axis=1)

    # event mid-times with errors
    dates = np.array(cal.caldat(ecl[0][:]), dtype=np.float64)
    dates = np.transpose(dates)
    mon   = dates[0]
    day   = dates[1]
    year  = dates[2]
    hour  = dates[3]
    min   = dates[4]
    sec   = dates[5]

    uncert = ecl[1][:] * 24. * 60. * 60.
    mid    = np.transpose([year, mon, day, hour, min, sec, \
                            uncert])
    
    midtimes = 'Times of %s %s, solar-system barycenter:\n'  % (planet, event)
    
    # format the string of event midtimes and errors
    for i in range(len(mid)):
        midtimes += '%4.0f   %2.0f   %2.0f   %4.0f   %2.0f   %6.3f  +- %10.3f sec\n' % \
            (mid[i][0], mid[i][1], mid[i][2], mid[i][3], mid[i][4], mid[i][5],\
                 mid[i][6])
            
    # constraints for ingress
    dt      = np.max((ecldur/2., 2*3600.)) # ecl offset FINDME
    jdstart = ecl[0][:] - (dt + ictrshift + ecldur/2. + startwin / 2.) * s2d  # start evnt before baseline 
    jdend   = jdstart + startwin * s2d
    iconst  = st.spitztiming(jdstart, jdend)

    # constraints for egress
    jdstart = ecl[0][:] - (ictrshift + startwin / 2.) * s2d
    jdend   = jdstart + startwin * s2d
    econst  = st.spitztiming(jdstart, jdend)

    if type == 'midtimes':
        return midtimes
    elif type == 'egress':
        return econst
    elif type == 'ingress':
        return iconst
