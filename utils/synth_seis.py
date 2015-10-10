"""
Test function to do a **very** basic simulation of a seismogram to see how well
a simple model would fit with real data.

Written as part of the EQcorrscan project, but not yet distributed.

All copyright and ownership of this script belongs to Calum Chamberlain.

"""
import numpy as np
def seis_sim(SP, amp_ratio=1.5, flength=False):
    """
    Function to generate a simulated seismogram from a given S-P time.
    Will generate spikes separated by a given S-P time, which are then convolved
    with a decaying sine function.  The P-phase is simulated by a positive
    spike of value 1, the S-arrival is simulated by a decaying boxcar of
    maximum amplitude 1.5.  These ampitude ratios can be altered by changing
    the amp_ratio, which is the ratio S amplitude:P amplitude.

    Note, in testing this can achieve 0.3 or greater cross-correlations with data

    :type SP: int
    :param SP: S-P time in samples
    :type amp_ratio: float
    :param amp_raio: S:P amplitude ratio
    :type flength: int
    :param flength: Fixed length in samples, defaults to False

    :returns: np.ndarray
    """
    if not flength and 2.5*SP < 100.0:
        additional_length=100
    elif not flength:
        additional_length=2.5*SP
    else:
        additional_length=flength-10
    synth=np.zeros(SP+10+additional_length) # Make the array begin 10 samples before the P\
            # and at least 2.5 times the S-P samples after the S arrival
    synth[10]=1.0
    # The length of the decaying S-phase should depend on the SP time,\
            # Some basic estimations suggest this should be atleast 10 samples\
            # and that the coda should be about 1/10 of the SP time
    S_length=int(10+SP/3.0)
    S_spikes=np.arange(amp_ratio, 0, -(amp_ratio/S_length))
    synth[10+SP:10+SP+len(S_spikes)] = S_spikes
    # What we actually want, or what appears better is to have a series of\
            # individual spikes, of alternating polarity...
    for i in xrange(10+SP+1, 10+SP+S_length, 2):
        synth[i]=0
    for i in xrange(10+SP, 10+SP+S_length,3):
        synth[i]*=-1
    # Generate a rough damped sine wave to convolve with the model spikes
    sine_x=np.arange(0, 10.0, 0.5)
    damped_sine=np.exp(-sine_x) * np.sin(2 * np.pi * sine_x)
    # Convolve the spike model with the damped sine!
    synth=np.convolve(synth,damped_sine)
    # Normalize snyth
    synth=synth/np.max(synth)
    return synth

def SVD_sim(SP, lowcut, highcut, samp_rate, amp_range=np.arange(-10,10,0.01)):
    """
    Function to generate a basis vectors of a set of simulated seismograms with
    a range of S-P amplitude ratios.

    :type SP: int
    :param SP: S-P time in seconds - will be converted to samples according to\
            samp_rate
    :type lowcut: float
    :param lowcut: Low-cut for bandpass filter in Hz
    :type highcut: float
    :param highcut: High-cut for bandpass filter in Hz
    :type samp_rate: float
    :param samp_rate: Sampling rate in Hz
    :type amp_range: np.ndarray
    :param amp_range: Amplitude ratio range to generate synthetics for.

    :returns: nd.ndarray, set of output basis vectors
    """
    from obspy import Stream, Trace
    # Convert SP to samples
    SP=int(SP*samp_rate)
    # Scan through a range of amplitude ratios
    synthetics=[Stream(Trace(seis_sim(SP, a))) for a in amp_range]
    for st in synthetics:
        for tr in st:
            tr.stats.station='SYNTH'
            tr.stats.channel='SH1'
            tr.stats.sampling_rate=samp_rate
            tr.filter('bandpass', freqmin=lowcut, freqmax=highcut)
    # We have a list of obspy Trace objects, we can pass this to EQcorrscan's\
            # SVD functions
    from utils import clustering
    V,s,U,stachans = clustering.SVD(synthetics)
    return V, s, U, stachans

def template_grid(stations, nodes, travel_times, phase, PS_ratio=1.68, \
                samp_rate=100, flength=False):
    """
    Function to generate a group of synthetic seismograms to simulate phase
    arrivals from a grid of known sources in a three-dimensional model.  Lags
    must be known and supplied, these can be generated from the bright_lights
    function: read_tt, and resampled to fit the desired grid dimensions and
    spacing using other functions therein.  These synthetic seismograms are very
    simple models of seismograms using the seis_sim function herein.  These
    approximate body-wave P and S first arrivals as spikes convolved with damped
    sine waves.

    :type stations: List
    :param stations: List of the station names
    :type nodes: list of tuple
    :param nodes: List of node locations in (lon,lat,depth)
    :type travel_times: np.ndarray
    :param travel_times: Array of travel times where travel_times[i][:] refers \
        to the travel times for station=stations[i], and travel_times[i][j] \
        refers to stations[i] for nodes[j]
    :type phase: String
    :param phase: Can be either 'P' or 'S'
    :type PS_ratio: float
    :param PS_ratio: P/S velocity ratio, defaults to 1.68
    :type samp_rate: float
    :param samp_rate: Desired sample rate in Hz, defaults to 100.0
    :type flength: int
    :param flength: Length of template in samples, defaults to False

    :returns: List of :class:obspy.Stream
    """
    if not phase in ['S','P']:
        raise IOError('Phase is neither P nor S')
    from obspy import Stream, Trace
    #Initialize empty list for templates
    templates=[]
    # Loop through the nodes, for every node generate a template!
    i=0
    for node in nodes:
        st=[] # Empty list to be filled with synthetics
        # Loop through stations
        j=0
        for station in stations:
            tr=Trace()
            tr.stats.sampling_rate=samp_rate
            tr.stats.station=station
            tr.stats.channel='SYN'
            tt=travel_times[j][i]
            if phase=='P':
                SP_time=(tt*PS_ratio)-tt
                tr.stats.starttime+=tt
            else:
                SP_time=tt-(tt/PS_ratio)
                tr.stats.starttime+=(tt/PS_ratio)
            # Set start-time of trace to be travel-time for P-wave
            tr.data=seis_sim(SP=int(SP_time*samp_rate), amp_ratio=1.5,\
                            flength=600)
            st.append(tr)
            j+=1
        templates.append(Stream(st))
        i+=1
    return templates
