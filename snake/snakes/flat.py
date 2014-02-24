import numpy
import snakes

class Flat(object):

    """ Flat Snake with previous, current and next nodes in the 
        energy calculation """

    def __init__(self, snaxels, moves, energy_callback, cached=False):

        self.snaxels = snaxels
        self.moves = moves
        self.cached = cached
        self.energy = energy_callback

        if self.cached:
            self.cache = snakes.Cache(self.energy)
            self.energy = self.cache.call


        # add the inverse moves
        for move in list(self.moves): # operate from copy
            self.moves.append(-move)

        # add the zero move (stay in place)
        self.moves.insert(0, 0)

        # make sure that moves are unique
        self.moves = list(set(moves))

        # shorthands
        N = len(self.snaxels)
        M = len(self.moves)

        # setup the stored values
        self.minima = numpy.empty((N, M, M, 3))


    def iterate(self):

        inf = float('inf')

        N = len(self.snaxels)
        M = len(self.moves)

        # reset the store
        #           i  j  k  type
        self.minima[0][:][:][:] = 0

        for i in range(N-1):

            for j in range(M): # moves of the forward node
                        
                minimum = (inf, 0, 0) # for each forward node

                next_node = (self.snaxels[i+1][0], self.snaxels[i+1][1] + self.moves[j])

                for k in range(M): # moves of the current node

                    current_node = (self.snaxels[i][0], self.snaxels[i][1] + self.moves[k])

                    if i == 0: # special case, first node

                        energy = self.energy(None, current_node, next_node)
                        if (energy < minimum[0]): minimum = (energy, k, 0)

                    else:

                        for l in range(M): # moves of the previous node

                            prev_node = (self.snaxels[i-1][0], self.snaxels[i-1][1] + self.moves[l])

                            energy = self.minima[i-1][k][l][0] + self.energy(prev_node, current_node, next_node)
                            if (energy < minimum[0]): minimum = (energy, k, l)

                    self.minima[i][j][k][:] = minimum # store the minimum


        # search final column for minimum energy
        final_minimum = (inf, 0, 0)

        for j in range(M):
            for k in range(M):
                if self.minima[N-2][j][k][0] < final_minimum[0]:
                    final_minimum = (self.minima[N-2][j][k][0], j, k)

        (energy, j, k) = final_minimum

        # search backwards through table to find optimum positions
        for i in range(N-1, -1, -1):
            self.snaxels[i][1] = self.snaxels[i][1] + self.moves[j]

            if i > 0:
                j = int(self.minima[i-1][j][k][1])
                k = int(self.minima[i-1][j][k][2])

        return energy
