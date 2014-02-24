#!/usr/bin/env python

import os.path
import pickle
import sys

import pylab
import numpy
import scipy.signal
import scipy.interpolate
import scipy.ndimage
import scipy.stats

import snakes
import snakes.energy as energy
import plots.snake
import plots
import util


df = numpy.load("out.npz")
image = df["echogram_clean"]
slope = df["slope"]

pick = pickle.load(file(sys.argv[1]))
snaxels = pick["snaxels"]

print "PICKS", len(pick["picked"])

""" CONFIG """
stepsize =  10
moves = [1]
subplot = False
image[numpy.isnan(image)] = 0
height, width = image.shape

""" NORMALIZE """

imageorig = image.copy()

image[image < 0] = 0
image[image > 10] = 10

image -= numpy.min(image[:])
image /= numpy.max(image[:])

image = 1-image

image = scipy.ndimage.filters.gaussian_filter1d(image, 2, axis=0, mode='nearest')

imageorig = image.copy()


""" PLOT AND PICK """
pylab.ion()
plots.fullscreen()
plots.snake.snakeplot(imageorig, snaxels, subplot=subplot)
pickedsnake = []

""" SETUP ENERGY FUNCTION """
energy_fn = energy.energy_function(image)
snake = snakes.Flat(snaxels, moves, energy_fn, cached=True)
plots.snake.snakeplot(imageorig, snaxels, energy_fn, use_prev=True, subplot=subplot)

previous_energy = []
while True:
    energy = snake.iterate()
    print energy
    if energy in previous_energy:
      break
    previous_energy.append(energy)
    plots.snake.snakeplot(imageorig, snaxels, energy_fn, use_prev=True, subplot=subplot)

plots.snake.snakeplot(imageorig, snaxels, energy_fn, use_prev=True, subplot=subplot)

pylab.title("DONE")
pylab.draw()

pylab.ioff()
pylab.show() 

