import numpy
import pylab

def multiscatter(x, y, data, normalize=True, **kwargs):

    if normalize:
        alldata = numpy.concatenate(data)
        alldata = alldata[~numpy.isnan(alldata)]
        allmin = numpy.min(alldata)
        allmax = numpy.max(alldata)-allmin

    divisions = float(len(data))

    for index, dataset in enumerate(data):

        if normalize: dataset = (dataset-allmin)/allmax
        
        circ_points = numpy.linspace(2*numpy.pi*((index)/divisions + 0.25), 2*numpy.pi*((index+1)/divisions + 0.25), 10)
        circ_x = [0] + numpy.cos(circ_points).tolist()
        circ_y = [0] + numpy.sin(circ_points).tolist()
        
        pylab.scatter(x, y, c=dataset, marker=(list(zip(circ_x, circ_y)), 0), **kwargs)
