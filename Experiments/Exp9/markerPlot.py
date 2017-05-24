#!/usr/bin/env python

# markerPlot.py: Plots to generate visualizations of cloth markers
# Author: Nishanth Koganti
# Date: 2016/11/6

# import the modules
import os
import sys
import GPy
import csv
import time
import random
import numpy as np
import cPickle as pickle
import matplotlib as mpl
import matplotlib.cm as cm
import scipy.stats as stats
from GPy.plotting import Tango
import sklearn.metrics as metrics
from sklearn import preprocessing
from itertools import combinations
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from GPy.plotting.matplot_dep.visualize import matplotlib_show
from GPy.inference.latent_function_inference import InferenceMethodList, VarDTC, VarDTC_minibatch


class cloth_show(matplotlib_show):
    """Base class for visualizing motion capture data."""

    def __init__(self, vals, limits, axes=None, connect=None, colors=np.array(12*['b'])):
        if axes==None:
            fig = plt.figure(facecolor='white')
            axes = fig.add_subplot(111, projection='3d', aspect='equal')

        if len(vals.shape)==1:
            vals = vals[None,:]

        self.fig = fig
        matplotlib_show.__init__(self, vals, axes)

        self.colors = colors
        self.limits = limits
        self.connect = connect

        self.process_values()

        self.initialize_axes()
        self.axes.set_xticklabels([])
        self.axes.set_yticklabels([])
        self.axes.set_zticklabels([])
        self.axes.set_xlabel('X Axis')
        self.axes.set_ylabel('Y Axis')
        self.axes.set_zlabel('Z Axis')

        self.draw_edges()
        self.draw_vertices()
        self.axes.figure.canvas.draw()

    def draw_vertices(self):
        self.points_handle = self.axes.scatter(self.vals[:, 0], self.vals[:, 1], self.vals[:, 2], color=self.colors, s=40)

    def draw_edges(self):
        self.line_handle = []
        if self.connect != None:
            x = []
            y = []
            z = []
            for item in connect:
                x.append(self.vals[item[0], 0])
                x.append(self.vals[item[1], 0])
                x.append(np.NaN)
                y.append(self.vals[item[0], 1])
                y.append(self.vals[item[1], 1])
                y.append(np.NaN)
                z.append(self.vals[item[0], 2])
                z.append(self.vals[item[1], 2])
                z.append(np.NaN)
            self.line_handle = self.axes.plot(np.array(x), np.array(y), np.array(z), '-', color='b', linewidth=3)

    def modify(self, vals):
        if len(vals.shape)==1:
            vals = vals[None,:]
        self.vals = vals.copy()

        self.axes_modify()
        self.process_values()

        self.draw_edges()
        self.draw_vertices()
        self.axes.figure.canvas.draw()

    def process_values(self):
        self.vals = self.vals.T.reshape((self.vals.shape[1]/3, 3))

    def initialize_axes(self, boundary=0.001):
        """Set up the axes with the right limits and scaling."""
        bs = [(self.limits[i,0]-self.limits[i,1])*boundary for i in range(3)]
        self.axes.set_xlim([self.limits[0,1]-bs[0], self.limits[0,0]+bs[0]])
        self.axes.set_ylim([self.limits[1,1]-bs[1], self.limits[1,0]+bs[1]])
        self.axes.set_zlim([self.limits[2,1]-bs[2], self.limits[2,0]+bs[2]])

    def axes_modify(self):
        self.points_handle.remove()
        if self.connect != None:
            self.line_handle[0].remove()

font = {'size':18}
mpl.rc('font', **font)

connect = [[0,1,'b'],[1,2,'b'],[2,3,'b'],[3,4,'b'],[4,5,'b'],[5,0,'b'],
           [6,7,'g'],[7,8,'g'],[8,6,'g'],[9,10,'g'],[10,11,'g'],[11,9,'g']]

model = pickle.load(open('Models/model.p','rb'))

fig, (sense_axes, latent_axes) = plt.subplots(1,2,facecolor='white')

plt.sca(latent_axes)
model.plot_latent(ax=latent_axes,marker='o')
latent_axes.set_xticks([])
latent_axes.set_yticks([])

trainData = model.Y.copy()
limits = np.asarray([[trainData[:,0::3].max(),trainData[:,0::3].min()],
                     [trainData[:,1::3].max(),trainData[:,1::3].min()],
                     [trainData[:,2::3].max(),trainData[:,2::3].min()]])

data_show = cloth_show(model.Y[:1, :].copy(), limits, connect=connect)
dim_select = GPy.plotting.matplot_dep.visualize.lvm_dimselect(model.X.mean[:1, :].copy(), model, data_show,
                                                              latent_axes=latent_axes, sense_axes=sense_axes)
sense_axes.set_ylabel('ARD Weight', fontsize=15)
sense_axes.set_xlabel('Latent Dimensions', fontsize=15)

fig.canvas.draw()
fig.tight_layout()

data_show.fig.canvas.draw()
data_show.fig.tight_layout()

plt.show()
raw_input('Press enter to finish')
