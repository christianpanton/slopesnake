import pylab
import numpy

import util
import plots.scatter

def snakeplot(image, snaxels=None, energy_fn=None, use_prev=False, point_size=10, point_alpha=0.6, subplot=True):

        pylab.clf()

        if subplot:
            ax1=pylab.subplot(2,1,1)
    
        ref = pylab.imshow(image, cmap=pylab.cm.gray, aspect='auto')
        
        (ylim, xlim) = (pylab.ylim(), pylab.xlim())

        if snaxels:

            ie = numpy.empty(len(snaxels))
            ee = ie.copy()
            
            ie[:] = 0
            ee[:] = 0

            for i in range(len(snaxels)-1):
                current = snaxels[i]
                next = snaxels[i+1]
                if i > 0:
                    prev = snaxels[i-1]
                else:
                    prev = None

                if energy_fn:
                    if use_prev:
                        (_i, _e) = energy_fn(prev, current, next, discrete=True)
                    else:
                        (_i, _e) = energy_fn(current, next, discrete=True)

                    ie[i] = _i 
                    ee[i] = _e

            dsnake = numpy.array(snaxels)
            pylab.plot(dsnake[:,0], dsnake[:,1], 'b')

            if energy_fn:
                plots.scatter.multiscatter(dsnake[:,0], dsnake[:,1], (ie, ee), s=point_size, alpha=point_alpha, cmap=pylab.cm.hot)

            pylab.xlim(xlim)
            pylab.ylim((numpy.max(dsnake[:,1])+100, numpy.min(dsnake[:,1])-100))

            if subplot:
                pylab.subplot(2,1,2, sharex=ax1)

                for cur, next in util.pairwise(snaxels):
                
                    index_x = numpy.arange(cur[0], next[0]+1)
                    index_y = numpy.linspace(cur[1], next[1], num=len(index_x), endpoint=True)
                    index_floor_y = numpy.floor(index_y)

                    data_current = image[index_floor_y.astype('i'), index_x.astype('i')]
                    data_next = image[(index_floor_y + 1).astype('i'), index_x.astype('i')]
                    ratio = index_y - index_floor_y

                    # interpolation
                    data = ratio * data_next + (1 - ratio) * data_current

                    pylab.plot(index_x, data)
                
                pylab.xlim(xlim)






        pylab.draw()

        return ref