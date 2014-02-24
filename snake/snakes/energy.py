import math
import numpy

def energy_function(image, alpha=10, beta=1, gamma=50, delta=1, critical_angle=6, calc_backwards=True):

    def calc_internal(prev, current, next):

        if prev is None: return 0

        prev = numpy.array(prev)
        current = numpy.array(current)
        next = numpy.array(next)

        A = next-current
        B = prev-current

        #deviation from 180 deg
        x = 1 + numpy.dot(A, B) / (numpy.linalg.norm(A)*numpy.linalg.norm(B))
        
        add = 0
        if x > 1: # over 90 degrees
            x -= 1
            add = 1

        # tan(asin(x)) = x / sqrt(1-x^2)
        angle = (x / math.sqrt(1-pow(x, 2))) + add

        # crit^(abs(angle)+1)-crit
        return (pow(critical_angle, abs(angle)+1)-critical_angle) 


    def calc_external(cur, next, discrete=False):
        
        yr = 70
        xr = 5

        b = 100

        x, y = map(int, cur)

        try:
            baseline = 0#numpy.min(image[y-b:y+b, x-b:x+b])
        except: 
            baseline = 0

        data_current = numpy.sum(image[y-yr:y+yr, x-xr:x+xr], axis=1)

        x, y = map(int, next)
        data_next = numpy.sum(image[y-yr:y+yr, x-xr:x+xr], axis=1)

        rss = sum(pow(data_current-data_next, 2))

        # Extract the data between cur and next
        # generate x and y coordinates for the valley
        # include endpoints
        index_x = numpy.arange(cur[0], next[0]+1).astype('i')
        index_y = numpy.linspace(cur[1], next[1], num=len(index_x), endpoint=True)
        index_floor_y = numpy.floor(index_y).astype('i')

        data_current = image[index_floor_y, index_x]
        data_next = image[index_floor_y + 1, index_x]
        ratio = index_y - index_floor_y

        # interpolation
        data = ratio * data_next + (1 - ratio) * data_current

        # data is in range [0..1]
        mean = pow(numpy.median(data) - baseline + 1, 2) 

        if discrete:
            return (mean * gamma, rss *delta)

        
        return mean * gamma + rss * delta
              
    def energy(prev, current, next, discrete=False):

        internal = calc_internal(prev, current, next) 

        external = calc_external(current, next)

        if prev is not None and calc_backwards:
            external += calc_external(prev, current)
            external /= 2.0

        if discrete:
            return calc_external(current, next, discrete=True)
            return (alpha*internal, external)

        return alpha*internal + external * beta


    return energy
