#!/usr/bin/env python

import os.path
import pickle

import pylab
import numpy
import scipy.signal
import scipy.interpolate
import scipy.ndimage
import scipy.stats
import copy

import plots.snake
import plots
import util

df = numpy.load("out.npz")
image = df["echogram_clean"]
slope = df["slope"]


""" CONFIG """
stepsize =  10
image[numpy.isnan(image)] = 0
height, width = image.shape
snaxels_x = range(stepsize/2, width, stepsize)
snaxels = map(list, zip(snaxels_x, [height/2]*len(snaxels_x)))
subplot=False
saved = []
""" NORMALIZE """

def pick_seed(event):
    global pickedsnake

    x = event.xdata
    y = event.ydata

    if event.button == 1:
        pickedsnake.append((x,y))
    elif event.button == 2:
        save()
    elif event.button == 3:
        if len(pickedsnake):
            pickedsnake.pop()

    if len(pickedsnake) > 0:
        build_snake()

    draw_snake()


def build_snake():
    global pickedsnake, stepsize, snaxels, snaxels_x, slope

    tmpsnake = pickedsnake[:]
    tmpsnake.append([snaxels_x[0], None])
    tmpsnake.append([snaxels_x[-1], None])

    tmpsnake.sort(key=lambda x: x[0])

    near_x = lambda x: numpy.argmin(numpy.abs(numpy.array(snaxels_x)-x))

    for a, b in util.pairwise(tmpsnake):

        ya = a[1]
        yb = b[1]

        targets = range(near_x(a[0]), near_x(b[0])+1)
        results = []
        weights = []

        if ya:

            localresult = []
            localweights = []

            for dst, x in enumerate(range(snaxels_x[targets[0]], snaxels_x[targets[-1]]+1)):
                ya += slope[round(ya), x]
                if x in snaxels_x:
                    i = near_x(x)
                    #snaxels[i][1] = round(ya)
                    localweights.insert(0,dst+1)
                    localresult.append(round(ya))

            results.append(localresult)
            weights.append(localweights)


        if yb:

            localresult = []
            localweights = []

            for dst, x in enumerate(range(snaxels_x[targets[-1]], snaxels_x[targets[0]]-1,-1)):
                yb -= slope[round(yb), x]
                if x in snaxels_x:
                    i = near_x(x)
                    #snaxels[i][1] = round(yb)
                    localweights.append(dst+1)
                    localresult.insert(0, round(yb))

            results.append(localresult)
            weights.append(localweights)

        results = numpy.array(results)
        weights = numpy.array(weights).astype('f')
        weights /= numpy.sum(weights, axis=0).astype('f')
        results = numpy.sum(results * weights, axis=0).tolist()

        for i, j in enumerate(targets):
            try:
                snaxels[j][1] = results[i]
            except IndexError:
                pass


def draw_snake():
    global image, snaxels, subplot, pickedsnake, saved
    if len(pickedsnake):
        plots.snake.snakeplot(image, snaxels, subplot=subplot)
    else:
        plots.snake.snakeplot(image, subplot=subplot)

    (ylim, xlim) = (pylab.ylim(), pylab.xlim())

    if len(pickedsnake):
        pick = numpy.array(pickedsnake)
        pylab.plot(pick[:,0], pick[:,1], 'xg', alpha=1)

    for obj in saved:
        snake = numpy.array(obj["snaxels"])
        pylab.plot(snake[:,0], snake[:,1], 'r', alpha=0.3)
        pick = numpy.array(obj["picked"])
        pylab.plot(pick[:,0], pick[:,1], 'xr', alpha=0.3)
            
    pylab.xlim(xlim)
    pylab.ylim(ylim)
    pylab.draw()

def save():
    global snaxels, pickedsnake, saved
    obj = {"picked": pickedsnake, "snaxels": copy.deepcopy(snaxels)}
    saved.append(obj)
    pickle.dump(obj, file("layers/pick%03d.pkl" % len(saved), "wb"))
    pickedsnake = []

    

""" PLOT AND PICK """
pickedsnake = []
fig, current_ax = pylab.subplots() 
plots.fullscreen()
draw_snake()
fig.canvas.mpl_connect('button_press_event', pick_seed)
pylab.show() 

