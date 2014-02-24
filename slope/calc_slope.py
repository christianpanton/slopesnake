#!/usr/bin/env python

import sys

import numpy
import scipy.ndimage
import scipy.interpolate
import pylab

import util

pylab.ion()

if len(sys.argv) != 2:
    print "Usage: %s datafile.npz" % sys.argv[0]
    sys.exit(-1)
else:
    datafile = numpy.load(sys.argv[1])

echogram = datafile["echogram"]
echogram = echogram[:,:30520]

print "Detrending echogram"
echogram -= scipy.ndimage.filters.gaussian_filter(echogram, 5, mode='nearest')


""" Configuration """

binconfig = [
    {
        "filter": (15, 0.125),
        "maxang": 20,
        "nbins": 10,
    },
    {
        "filter": (45, 0.125),
        "maxang": 15,
        "nbins": 10,
    },
    {
        "filter": (100, 0.125),
        "maxang": 3,
        "nbins": 10,
    },
]


clean_correlation = 2

print "Pre-calculate some values"

bins = []
filters = []
configs = []

for idx, bc in enumerate(binconfig):
    tmpbins = numpy.linspace(-bc["maxang"], bc["maxang"], bc["nbins"], endpoint=True)
    tmpnbins = len(tmpbins)
    bins.extend(tmpbins)
    filters.extend([bc["filter"]]*tmpnbins)
    configs.extend([idx]*tmpnbins)

nbins = len(bins)
binang = numpy.deg2rad(bins) # convert to rads
configs = numpy.array(configs)

print "Allocate arrays"
peak_index = numpy.empty(echogram.shape, dtype='i')
peak_response = numpy.empty(echogram.shape)
peak_response[:] = -numpy.inf

print " ... FFT image"
fecho = numpy.fft.fft2(echogram) # echogram in frequency domain

print "Generating sloped smoothing"

for idx, ang in enumerate(binang):
    print " ... %d of %d" % (idx+1, nbins)

    # generate filter

    print " ... ... Generate filter"
    filterfn = util.gaussian2d((echogram.shape[1], echogram.shape[0]), filters[idx], -ang)

    # convert filter to freq domain
    print " ... ... FFT filter"
    ffilt =  numpy.fft.fft2(filterfn)

    print " ... ... Convolve"
    tmp = numpy.fft.ifft2(ffilt * fecho)

    print " ... ... Convert to real"
    tmp = numpy.real(tmp)

    print " ... ... FFT shift"
    tmp = numpy.fft.fftshift(tmp)

    print " ... ... Getting peak response"
    # To avoid building a huge array in memory, the recursive max is taken
    tmp = numpy.dstack((numpy.abs(tmp), peak_response))
    tmpidx = numpy.argmax(tmp, axis=2)
    peak_index[tmpidx==0] = int(idx)
    peak_response = numpy.max(tmp, axis=2)


"""" STAGE 1 DONE """

#peak_response = peak_response - 0.5
peak_response[peak_response<=0] = 0
height, width = echogram.shape

# Bedrock threshold roughly picked with:
pylab.imshow(peak_response, aspect="auto")
bedrock = numpy.array(pylab.ginput(-1))
bedrock_interp = scipy.interpolate.UnivariateSpline(bedrock[:,0], bedrock[:,1], s=1)
bedrock = map(int, bedrock_interp(range(width)))

# Black out bedrock
for i in range(width):
    peak_response[bedrock[i]-35:,i] = 0

print "Echogram: %d by %d" % (height, width)

slope = binang[peak_index]

# Clean the slope with a spline
slope_clean = slope.copy()
slope_clean[:] = numpy.nan

cleanheight, cleanwidth = slope_clean.shape

lookup_slope = slope.copy()
lookup_weight = peak_response.copy() 

lookup_slope[0,:] = 0
lookup_weight[0,:] = numpy.max(lookup_weight, axis=0)*2


for i in range(cleanwidth):
    trace_index_master = numpy.arange(cleanheight)
    trace_index  = numpy.array([])
    trace_slope  = numpy.array([])
    trace_weight = numpy.array([])
    corr_index = numpy.arange(-clean_correlation, clean_correlation+1)
    corr_index[corr_index + i >= cleanwidth] = 0
    corr_index[corr_index + i < 0] = 0
    for j in corr_index:
        trace_index = numpy.concatenate([trace_index, trace_index_master])
        trace_slope = numpy.concatenate([trace_slope, lookup_slope[:,i+j]])
        trace_weight = numpy.concatenate([trace_weight, lookup_weight[:,i+j]/(abs(j)+1)])
    spline = scipy.interpolate.UnivariateSpline(trace_index, trace_slope, w=trace_weight**2)
    value = spline(trace_index_master)
    slope_clean[:, i] = value
    if i % 1000 == 0:
        print " ... Slope clean:", i, "of", width
        

y = numpy.arange(height)

integrated = numpy.cumsum(-slope_clean, axis=1)

newindex = integrated + y.reshape((-1,1))

y = numpy.arange(height+500)

out = numpy.empty((height+500, width))
out[:] = numpy.nan
for j in range(width):
    interp = scipy.interpolate.interp1d(newindex[:,j], echogram[:,j],bounds_error=False)
    out[y, j] = interp(y)
    if j % 1000 == 0:
        print "Folding:", j, "of", width

pylab.imshow(out, aspect="auto")

save = raw_input("Save? ").lower()
if save == "y":
    numpy.savez("out.npz", echogram=echogram, peak_response=peak_response, peak_index=peak_index, slope=slope_clean, slope_raw=slope)