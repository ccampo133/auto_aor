# $Author: ccampo $
# $Revision: 31 $
# $Date: 2009-06-18 09:55:27 -0400 (Thu, 18 Jun 2009) $
# $HeadURL: file:///home/esp01/svn/code/auto_aor/trunk/caldat.py $
# $Id: caldat.py 31 2009-06-18 13:55:27Z ccampo $

def caldat(juldate, verbose=False):
    """
NAME:
      caldat

PURPOSE:
      Calculate the Gregorian date from a Julian date.  This routine
      is the inverse to JULDAY.

INPUTS:
      julday:  The julian date to be converted (can be array)

      verbose: Optional parameter; if set to True, the abbreviated
               name of the month is returned instead of the number.
               (ie: Dec instead of 12)

OUTPUTS:
     A tuple (1D or 2D, depending on input specifications) that 
     represents the year, month, day, hour, minute, second.

     Format (rows):
     (yyyy, mm, dd, hh, mm, ss.ssss)

RESTRICTIONS:
     Numpy must be installed.

SIDE EFFECTS:
     None.

NOTES:
     Loosely based off of IDL's caldat routine, which does the same
     calculation.  This function has support for an array of input
     values.  If the input is an array, the output is a 2D tuple.

     Can also input a list or tuple in place of an array. The result
     will be the same as an array.

MODIFICATION HISTORY:
     2009-01-06   0.1    Christopher Campo, UCF    Initial version
                         ccampo@gmail.com
    """
    import numpy as np

    if type(juldate) == np.ndarray or type(juldate) == list \
            or type(juldate) == tuple:
        date = []
            
        # loop through array; calculate the date for each
        # index.
        for i in range(len(juldate)):
            if verbose == False:
                date.append(get_date(juldate[i]))
            else:
                date.append(get_date(juldate[i], True))
                
        # returns a 2D tuple of the dates calculated.
        return tuple(date)
    else:
        # the input is a scalar; only need to calculate for
        # one value. return is a tuple.
        if verbose == False:
            return get_date(juldate)
        else:
            return get_date(juldate, True)

# used by caldat function to do the actual date calculations.
# may be used outside of this routine, but it only works for
# scalar types.  sticking with caldat is the safest and best
# way to use this routine, since it works for both scalars 
# AND arrays/list/tuples as input.
def get_date(jd, verbose=False):
    # Julian to Gregorian formulae: wikipedia 
    jd = float(jd)
    jd = jd +  0.5
    z  = int(jd)
    f  = jd - z
    
    alpha = int((z - 1867216.25)/36524.25)

    a = z + 1 + alpha - int(alpha/4)
    b = a + 1524
    c = int((b - 122.1)/365.25)
    d = int(365.25 * c)
    e = int((b - d)/30.6001)
    
    # day of the month (dd)
    dd = b - d - int(30.6001 * e) + f
    
    # calculate month number (mm)
    if e < 13.5:
        mm = e - 1
    else:
        mm = e - 13

    # calculate year (yyyy)
    if mm > 2.5:
        yyyy = c - 4716
    else:
        yyyy = c - 4715

    # hour of the day
    h = int((dd - int(dd)) * 24)
    
    # minute of the hour
    min = int((((dd - int(dd)) * 24) - h) * 60)

    # second of the minute
    sec = 86400 * (dd - int(dd)) - h * 3600 - min * 60

    # the final date
    date = [mm, int(dd), yyyy, h, min, sec]
    
    months = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',\
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
    
    if verbose == False:
        return tuple(date)
    else:
        date[0] = months[mm - 1]
        return tuple(date)
