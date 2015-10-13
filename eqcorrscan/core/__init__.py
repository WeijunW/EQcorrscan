#!/usr/bin/python

#------------------------------------------------------------------------------
#   Purpose:    Convenience imports for EQcorrscan.core module
#   Author:     Calum John Chamberlain
#------------------------------------------------------------------------------

"""
EQcorrscan is a python module designed to run match filter routines for
seismology, within it are routines for integration to seisan and obspy.
With obspy integration (which is necessary) all main waveform formats can be
read in and output.

This main section contains a script, LFE_search.py which demonstrates the usage
of the built in functions from template generation from picked waveforms
through detection by match filter of continuous data to the generation of lag
times to be used for relative locations.

The match-filter routine described here was used a previous Matlab code for the
Chamberlain et al. 2014 G-cubed publication.  The basis for the lag-time
generation section is outlined in Hardebeck & Shelly 2011, GRL.

Code generated by Calum John Chamberlain of Victoria University of Wellington,
2015.

All rights reserved.

Pre-requisites:
    gcc             - for the installation of the openCV correlation routine
    python-joblib   - used for parallel processing
    python-obspy    - used for lots of common seismological processing
                    - requires:
                        numpy
                        scipy
                        matplotlib
    python-pylab    - used for plotting
"""

import sys
sys.path.insert(0,"/home/processor/Desktop/EQcorrscan/core")

__all__ = ['template_gen', 'match_filter', 'bright_lights']

if __name__ == '__main__':
    import doctest
    doctest.testmod(exclude_empty=True)
