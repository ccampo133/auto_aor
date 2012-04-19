# module contains multiple routines for calculating information
# needed for every AOR (pointing offsets, number of frames, etc).
import numpy as np
import orbit
import tepclass as tc

def exppars(mode, exptime):
    """
    Calculates the expected readout time and initial overhead of a
    Spitzer observation (AOR).

    Parameters
    ----------
    mode : string
        The read mode, either `full_array` or `subarray`.
    exptime : scalar
        The exposure time (readout mode) of the observation in
        seconds.  Accepted values for full array mode are:
        12, 6, 2, 0.4
        Accepted values for subarray mode are:
        2, 0.4, 0.1, 0.02

    Returns
    -------
    rdout : scalar
        The readout time of the observation (seconds).
    overhead : scalar
        The initial overhead (seconds) of the observaiton.

    Notes
    -----
    All values were calculated by taking output from SPOT (number of
    frames and observation duration) and comparing them to the model
    values defined by: duration = nframes*(exptime + rdout) +
    overhead.  SPOT lists a default overhead of 215s.  Each readout
    mode has an additional offset to the 215s, which is typically
    between 15-20s for unknown reasons.  All values can be found in
    /home/esp01/doc/spitzer_obs_planning for reference.

    Examples
    --------

    Revisions
    ---------
    2010-05-19  Christopher J. Campo, UCF (ccampo@gmail.com)
                Initial version.
    """
    # initial overhead as stated in SPOT
    overhead = 215.
    
    # full array 
    if mode == 'full_array':
        if exptime == 12 or exptime == 6:
            rdout     =   1.20
            overhead +=  20.50
            
        elif exptime == 2:
            rdout     =   1.40
            overhead +=  17.40
            
        elif exptime == 0.4:
            rdout     =   2.00
            overhead +=  17.40
            
    elif mode == 'subarray':
        # overhead is the same for all subarray modes
        overhead += 18.4  
        if exptime == 2:
            rdout     = 127.40
            
        elif exptime == 0.4:
            rdout     =  27.00
            
        elif exptime == 0.1:
            rdout     =   8.30

        elif exptime == 0.02:
            rdout     =   3.38

    try:
        return np.array([rdout, overhead])
    except UnboundLocalError as detail:
        print('Either the readout mode is not supported OR the ' +\
              'specified exposure time is not supported for that ' +\
              'particular readout mode: {0}'.format(detail))

def get_nfrms(dur, exptime, rdout, overhead):
    """
    Calculates the SPOT required number of exposures to reach the
    specified observation `dur`.

    Parameters
    ----------
    dur : scalar
        The total observation duration in seconds.
    exptime : scalar
        The exposure time of the observation in seconds.
    rdout : scalar
        The readout time of the observation in seconds.
    overhead : scalar
        The initial overhead of the observation in seconds.

    Returns
    -------
    nfrms : int
        The number of frames of the observation.

    Notes
    -----
    If you need the readout and overhead times calculated for a
    particular readout mode, please see the routine `exppars`.

    Examples
    --------
    
    Revisions
    ---------
    2010-05-19  Christopher J. Campo, UCF (ccampo@gmail.com)
                Initial version.
    """
    # inverse of dur(nfrms) = nfrms*(exptime + rdout) + overhead
    nfrms = (dur - overhead)/(exptime + rdout)
    return int(np.ceil(nfrms))

def get_dur(nfrm, exptime, rdout, overhead):
    """
    Calculates the duration of an AOR given the exposure time,
    readout time, overhead, and number of frames.

    Parameters
    ----------
    nfrm : int
        The total number of frames to shoot.
    exptime : scalar
        The exposure time of the observation in seconds.
    rdout : scalar
        The readout time of the observation in seconds.
    overhead : scalar
        The initial overhead of the observation in seconds.

    Returns
    -------
    dur : scalar
        The total duration of the AOR in seconds.
        
    Notes
    -----
    If you need the readout and overhead times calculated for a
    particular readout mode, please see the routine `exppars`.
    This function is the inverse of `get_nfrms`.

    Examples
    --------
    
    Revisions
    ---------
    2010-05-19  Christopher J. Campo, UCF (ccampo@gmail.com)
                Initial version.
    """
    dur = nfrm*(exptime + rdout) + overhead
    return dur

def get_offsets(chan):
    """
    Gets pointing offsets for default pixels specified as good by
    SPOT for `full_array` mode.

    Parameters
    ----------
    chan : scalar
        IRAC wavelength channel.  Must be in the range [1, 4].

    Returns
    -------
    rowoff : scalar
        Row array position coordinates.
    coloff : scalar
        Column array position coordinates.

    Examples
    --------

    Revisions
    ---------
    2010-05-20  Christopher J. Campo, UCF (ccampo@gmail.com)
                Initial version.
    """
    chan = int(chan)
    if chan == 13 or chan == 12:
        rowoff = 120.709 
        coloff = -125.532
    elif chan == 24:
        rowoff = 124.424
        coloff = -125.245
    elif chan == 1:
        rowoff = 129.241
        coloff = -125.245
    elif chan == 2:
        rowoff = 124.164
        coloff = -125.515
    elif chan == 3:
        rowoff = 0.000  # FINDME: Chan 3 + 4  missing; needs update
        coloff = 0.000
    elif chan == 4:
        rowoff = 0.000
        coloff = 0.000

    return np.array([rowoff, coloff])

def get_phase(info_dict):
    """
    Check and determine whether or not to calculate eclipse phase
    """
    # check type of event
    evtype = info_dict['event']
    if evtype == 'transit':
        return 0.
    elif evtype == 'eclipse':
        # check if phase, e, and omega are defined.
        eclflag = False
        eflag   = False
        wflag   = False
        if info_dict['omega'][0] != -1:
            w     = info_dict['omega'][0]
            wflag = True
        if info_dict['e'][0] != -1:
            e     = info_dict['e'][0]
            eflag = True
        if info_dict['eclphase'][0] != -1:
            phase   = info_dict['eclphase'][0]
            eclflag = True

        # decide to calculate it
        if eclflag == True:
            print("Orbit has a non-zero eccentricity! Please confirm the eclipse phase!")
            print("  Eclipse phase defined in INPUT FILE(s): {0}".format(phase))
            return phase
        else:
            if eflag == True and wflag == True:
                print("Eclipse phase undefined! Calculating it from e and omega...")
                phase = orbit.eclipse_phase(w, e)
                print("Calculated phase value: {0}".format(phase))
                info['phasecalc'] = True  # flag; phase is calculated
                return phase
            else:
                print("Eclipse phase undefined, as well as e and/or omega!")
                raise ValueError, "Please specifiy a eclipse phase, or e and omega to calculate one."

def check_uncert(info_dict, uncertlist):
    """
    Check if uncertainties exist.
    """
    # loop thru needed uncertainties
    flag = False
    for i in range(len(uncertlist)):
        param  = uncertlist[i]
        uncert = info_dict[param][1]
        if uncert == -1:
            print("{0} uncertainty is undefined!".format(param))
            flag = True

    if flag == False:
        print("All needed parameter uncertainties OK!")
    return

def getduration(info, evdur):
    """
    Calculate the eclipse or transit duration.
    """
    e  = info['e'][0]      # eccentricity
    p  = info['period'][0] # period in SECONDS
    w  = info['omega'][0]  # omega in RADIANS
    ms = info['ms'][0]     # mstar in kg 
    rs = info['rs'][0]     # rstar in m
    rp = info['rp'][0]     # rp in m
    i  = info['i'][0]      # inclination in rad
    b  = info['impactpar'][0] # impact parameter

    pars     = [e, p, w, ms, rs, rp]
    parnames = ['eccentricity', 'period', 'omega', 'mstar', 'rstar', 'rplanet']
    for i in range(len(pars)):
        if pars[i] == -1:
            print("Parameter {0} is undefined (-1)!!! Cannot calculate {1} duration!".format(parnames[i], evdur))
            raise Exception("PLEASE SPECIFY PARAMETER {0} OR {1}!".format(parnames[i], evdur))

    pars[1] *= 86400.      # seconds to days
    pars[2] *= 180./np.pi  # rad to deg
    pars[3] /= tc.msun     # kg to solar masses

    if i == -1:
        useb == True
    else:
        useb == False
        pars[6] *= 180./np.pi  # rad to deg

    # calculate duration for transit or eclipse
    if evdur == 'ecldur':
        ecltype = False

    if useb:
        dur = orbit.duration(*pars, primary=ecltype, b=b) * 60.  # minutes to seconds
    else:
        dur = orbit.duration(*pars, i=i, primary=ecltype) * 60.  # minutes to seconds

    if dur == 0:
        raise Exception("ERROR CALCULATING {0}! Please specify {0} manually to continue!".format(evdur))

    return dur
