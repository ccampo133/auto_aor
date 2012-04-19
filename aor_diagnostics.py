import numpy as np
import spitztimingrep
import orbit

def diagnostics(info):
    """
    Returns a string containing all timing information of
    an AOR.

    Parameters
    ----------
    info : dict
        A dictionary containing all AOR information (see auto_aor).

    Returns
    -------
    diagstr : string
        A formatted string with all diagnostic information.

    Revisions
    ---------
    2010-05-20  Christopher J. Campo, UCF (ccampo@gmail.com)
                Initial version.
    """
    # get the eclipse phase
    if info['event'] == 'transit':
        eclphase = info['eclphase'][0]
    else:
        eclphase = info['evphase']
    
    # get the error in eclipse phase
    if info['phasecalc'] == True:
        errphase = orbit.error_eclipse(info['e'][0], info['e'][1], info['omega'][0], info['omega'][1])
        print("Eclipse phase and error calculated: {0} +/- {1}".format(info['evphase'], errphase))
    elif info['eclphase'][1] == -1:
        errphase = 0
    else:
        errphase = info['eclphase'][1]
        
    # eclipse times (assuming circular orbit)
    ecltimes = spitztimingrep.spitztimingrep(info['planetname'],  # planet name
                                             'eclipse',           # type of event
                                             eclphase,            # orbit phase of eclipse
                                             info['duration'],    # event duration
                                             info['startwin'],    # start wime window
                                             info['vis'],         # visibility windows
                                             info['ttrans'],      # transit mid-time and error
                                             info['period'],      # orbit period and error
                                             info['toff'],        # offset time from ephemeris
                                             info['ctrshift'],    # shift from event center
                                             errphase=errphase,   # error in eclipse phase
                                             type='midtimes'
                                             )

    # transit times (assuming circular orbit)
    transtimes = spitztimingrep.spitztimingrep(info['planetname'], # planet name
                                               'transit',          # type of event
                                               0,                  # orbit phase of transit
                                               info['duration'],   # event duration
                                               info['startwin'],   # start wime window
                                               info['vis'],        # visibility windows
                                               info['ttrans'],     # transit mid-time and error
                                               info['period'],     # orbit period and error
                                               info['toff'],       # offset time from ephemeris
                                               info['ctrshift'],   # shift from event center
                                               errphase=errphase,  # error in eclphase
                                               type='midtimes'
                                               )

    diagstr = """Filename of AOR generated:
{0}

Filename of .tep file used in auto generation:
{1}

Filename of .aai file used in auto generation:
{2}

Filename of .vis file used in auto generation:
{3}

Object: {4}    Event: {5}
{6}

Object: {7}    Event: {8}
{9}
""".format(info['filename'], info['tepname'], info['aainame'], info['visname'],
           info['planetname'], 'ECLIPSE', ecltimes, info['planetname'], 'TRANSIT',
           transtimes)

    return diagstr
