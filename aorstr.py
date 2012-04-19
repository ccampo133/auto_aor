import datetime

def header():
    """
    Generate a header for a SPOT compatible AOR.

    Parameters
    ----------
    None

    Returns
    -------
    head : string
        The header in SPOT's strict format.  This contains line breaks.

    Examples
    --------
    >>> import aorhead
    >>> aorhead.aorhead()
    '# Please edit this file with care to maintain the\n# correct
    format so that SPOT can still read it\n# Generated by auto_aor on:
    05/17/2010 19:35:48\n\nHEADER: FILE_VERSION=17.0,
    STATUS=PROPOSAL\n'

    Revisions
    ---------
    2010-05-17  Christopher J. Campo, UCF (ccampo@gmail.com)
                Initial version.
    """
    # get the date
    date = datetime.datetime.now()
    date = date.strftime("%m/%d/%Y  %H:%M:%S")  # convert to string

    # the Spitzer SPOT specified header string
    head = '''#  Please edit this file with care to maintain the
#  correct format so that SPOT can still read it
#  Generated by auto_aor on: {0}

HEADER: FILE_VERSION=17.0, STATUS=PROPOSAL
'''.format(date)
    return head

##################################

def body(mission, aorlabel, targname, ra, dec, pmra, pmdec, offrow, offcol, readmode, chan, exptime, nfrms, tconst):
    """
    Generate a SPOT compatible AOR body string.

    Parameters
    ----------
    mission : string
        Spitzer mission type (warm or cold)
    aorlabel : string
        Label of the AOR
    targname : string
        Name of the target
    ra : string
        Right ascension of target (in format hh:mm:ss.ss)
    dec : string
        Declination of target (in format dd:mm:ss.ss)
    pmra : scalar
        Proper motion of target in RA
    pmdec : scalar
        Proper motion of target in DEC
    offrow : scalar
        IRAC row offsets
    offcol : scalar
        IRAC column offsets
    readmode : string
        IRAC readout mode (full_array or subarray)
    chan : scalar
        IRAC channel (1, 2, 3, or 4)
    exptime : scalar
        IRAC exposure time.
    nfrms : scalar
        Number of frames to shoot
    tconst : ndarray or list
        List of timing constraints.  Output of spitztimingrep.
    
    Returns
    -------
    bodstr : string
        The full AOR body string including timing constraints.

    Revisions
    ---------
    2010-05-20  Christopher J. Campo, UCF (ccampo@gmail.com)
                Initial version.   
    """
    # warm and cold missions have a few formatting differences
    if mission == 'cold':
        typestr  = ''
    else:
        typestr = 'Post-Cryo '
        if chan == 1:
            arraystr = '36u=YES, 45u=NO'
        else:
            arraystr = '36u=NO, 45u=YES'

    # make ra and dec into correct format
    ra  = ra.split(':')
    ra  = ra[0] + "h" + ra[1] + "m" + ra[2] +"s"
    dec = dec.split(':')
    dec = dec[0] + "d" + dec[1] + "m" + dec[2] + "s"

    # make timing constraints string
    tconststr = ''
    for line in tconst:
        tconststr += line + '\n'
    
    # the body string as specifed strictly by SPOT
    bodstr = """
      AOT_TYPE:  IRAC {0}Mapping
     AOR_LABEL:  {1}
    AOR_STATUS:  new

 MOVING_TARGET:  NO
   TARGET_TYPE:  FIXED CLUSTER - OFFSETS
   TARGET_NAME:  {2}
  COORD_SYSTEM:  Equatorial J2000
     POSITION1:  RA_LON={3}, DEC_LAT={4}, PM_RA={5:0.2}\", PM_DEC={6:0.2}\", EPOCH=2000.0
     OFFSET_P2:  EAST_ROW_PERP={7:0.5}\", NORTH_COL_PARA={8:0.5}\"
OFFSETS_IN_ARRAY:  YES
OBSERVE_OFFSETS_ONLY:  YES
OBJECT_AVOIDANCE:  EARTH = YES, OTHERS = YES

          READOUT_MODE: {9}
                 ARRAY: {10}
       DATA_COLLECTION: {10}
            HI_DYNAMIC: NO
            FRAME_TIME: {11}
        DITHER_PATTERN: TYPE=none
 N_FRAMES_PER_POINTING: {12}
SPECIAL:  IMPACT = none, LATE_EPHEMERIS = NO,SECOND_LOOK = NO
{13}





""".format(typestr, aorlabel, targname, ra, dec, pmra, pmdec, offrow, offcol, readmode.upper(), arraystr, exptime, nfrms, tconststr)
    return bodstr

###############################################################

def footer(sciname, postname, tepname, aainame, visname):
    """
    Generate footer text for a SPOT compatible AOR.

    Parameters
    ----------
    sciname : string
        Name of science AOR.
    postname : string
        Name of post AOR.        
    tepname : string
        Filename of tep file used in generation of AOR.
    aainame : string
        Filename of aai file used in generation of AOR.
    visname : string
        Filename of vis file used in generation of AOR.

    Returns
    -------
    footstr : string
        The formatted footer string for the AOR.
 
    Revisions
    ---------
    2010-05-20  Christopher J. Campo, UCF (ccampo@gmail.com)
                Initial version.          
    """
    footstr = """
CONSTRAINT: TYPE=CHAIN, NAME=ch-{0}
AORS: AOR1={1},
      AOR2={2}
COMMENT_START:
tep used: {3} 
aai used: {4}
vis used: {5}
COMMENT_END:






""".format(sciname, sciname, postname, tepname, aainame, visname)
    footstr = footstr.lstrip() # remove extra whitespace
    return footstr

#########################################

def aorstr(info):
    """
    Return the complete AOR as a string which can be written
    to a file.

    Parameters
    ----------
    info : dict
        A dictionary containing all necessary information about
        the AOR, contained in the tep, vis, and aai files.

    Returns
    -------
    aor : str
        The complete AOR text in string format.
        
    Revisions
    ---------
    2010-05-20  Christopher J. Campo, UCF (ccampo@gmail.com)
                Initial version.           
    """
    # aor header
    head   = header()

    # science AOR body
    scibod = body(info['mission'],     # mission type (warm/cold)
                  info['aorname'],     # label of aor
                  info['aorname'],     # name of target
                  info['ra'],          # ra of targ
                  info['dec'],         # dec of targ
                  info['pmra'][0],     # proper motion in ra
                  info['pmdec'][0],    # proper motion in dec
                  info['off_row'],     # row offsets
                  info['off_col'],     # column offsets
                  info['readmode'],    # array readout mode
                  info['chan'],        # IRAC channel
                  info['frametime'],   # exposure time
                  info['nframes'],     # number of frames
                  info['tconst'],      # timing constaints list
                  )

    # post AOR name
    postname = info['aorname'] + '-co'

    # subarray gets one cycle (64frm); full array gets 10 frames
    if info['readmode'] == 'subarray':
        postfrm = 1
    else:
        postfrm = 10

    # post AOR body
    cobod  = body(info['mission'],     # mission type (warm/cold)
                  postname,            # label of aor
                  postname,            # name of target
                  info['co_ra'],       # ra of targ
                  info['co_dec'],      # dec of targ
                  0.0,                 # proper motion in ra  (none for co)
                  0.0,                 # proper motion in dec (diddo)
                  info['off_row'],     # row offsets
                  info['off_col'],     # column offsets
                  info['readmode'],    # array readout mode
                  info['chan'],        # IRAC channel
                  info['frametime'],   # exposure time
                  postfrm,             # number of frames (10 for co)
                  '',                  # no timing constraints for co
                  )

    # AOR footer
    foot     = footer(info['aorname'],
                      postname,
                      info['tepname'],
                      info['aainame'],
                      info['visname'],
                      )

    # the final aor
    aor = head + scibod + cobod + foot
    return aor