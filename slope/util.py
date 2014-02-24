import numpy 

from itertools import tee, izip

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

def gaussian2d(size, sigma, theta):
    x, y = numpy.meshgrid(numpy.arange(float(size[0])),numpy.arange(float(size[1])))
    xc = x - size[0]/2.0
    yc = y - size[1]/2.0
    xm  = (xc)*numpy.cos(theta) - (yc)*numpy.sin(theta)
    ym  = (xc)*numpy.sin(theta) + (yc)*numpy.cos(theta)
    u   = pow(xm / sigma[0], 2) + pow(ym / sigma[1], 2)
    gaussian = numpy.exp(-u/2)
    return gaussian / numpy.sum(gaussian)