# This program was written to remove the time overhead of using IPython. However, this program was not used to generate the final results in the paper.
# hybrid.py: Python program to perform optimization on each frame
# Author: Nishanth Koganti
# Date: 2016/1/7

# Updates to work on larger dataset
# Date: 2016/09/16

# import modules
import os
import GPy
import csv
import sys
import time
import random
import filterpy
import numpy as np
import cPickle as pickle
from matplotlib import cm
import scipy.stats as stats
from tabulate import tabulate
import sklearn.metrics as metrics
from sklearn import preprocessing
import GPy.plotting.Tango as Tango
from itertools import combinations
from matplotlib import pyplot as plt
from filterpy.kalman import KalmanFilter
from sklearn.neighbors import NearestNeighbors
from filterpy.kalman import UnscentedKalmanFilter as UKF

def nnsearchFunc(mrdModel, testData):
    # model variables
    kKey = 'Cloud'
    mKey = 'TopCoord'

    qDim = mrdModel.X.mean.shape[1]
    nDimIn = testData[kKey].shape[1]
    nDimOut = testData[mKey].shape[1]
    nSamples = testData[mKey].shape[0]
    latentVals = np.zeros((nSamples,qDim))
    predictVals = np.zeros((nSamples,nDimOut))

    # obtain the training data latent positions
    latentPositions = mrdModel.X.mean.values
    nn = NearestNeighbors(n_neighbors=5,algorithm='kd_tree').fit(mrdModel.Y0.Y)

    startTime = time.time()
    for n in range(nSamples):
        yIn = testData[kKey][n,:]
        yTrueOut = testData[mKey][n,:]

        _,indices = nn.kneighbors(np.atleast_2d(yIn))
        latentVal = latentPositions[indices[0],:].mean(axis=0)

        yOut = mrdModel.predict(np.atleast_2d(latentVal), Yindex=1)
        latentVals[n,:] = latentVal
        predictVals[n,:] = yOut[0]
        sys.stdout.write('.')
        sys.stdout.flush()
    stopTime = time.time()
    print '\nFinished Strategy NN Search'

    nrmse = np.divide(np.sqrt(metrics.mean_squared_error(testData[mKey],predictVals,multioutput='raw_values')),
                      testData[mKey].max(axis=0) - testData[mKey].min(axis=0))
    rmse = np.sqrt(metrics.mean_squared_error(testData[mKey],predictVals,multioutput='raw_values'))
    corr = np.zeros((1,nDimOut))
    for d in range(nDimOut):
        corr[0,d],_ = stats.pearsonr(testData[mKey][:,d],predictVals[:,d])

    results = {}
    results['corr'] = corr
    results['rmse'] = rmse
    results['nrmse'] = nrmse
    results['pred'] = predictVals
    results['latent'] = latentVals
    results['time'] = nSamples/(stopTime - startTime)
    return results

def optimizeFunc(mrdModel, testData):
    # model variables
    kKey = 'Cloud'
    mKey = 'TopCoord'

    qDim = mrdModel.X.mean.shape[1]
    nDimIn = testData[kKey].shape[1]
    nDimOut = testData[mKey].shape[1]
    nSamples = testData[mKey].shape[0]
    latentVals = np.zeros((nSamples,qDim))
    predictVals = np.zeros((nSamples,nDimOut))

    # obtain the training data latent positions
    latentPositions = mrdModel.X.mean.values
    nn = NearestNeighbors(n_neighbors=5,algorithm='kd_tree').fit(mrdModel.Y0.Y)

    startTime = time.time()
    for n in range(nSamples):
        yIn = testData[kKey][n,:]
        yTrueOut = testData[mKey][n,:]

        [xPredict, infX] = mrdModel.Y0.infer_newX(yIn[None,:], optimize=True)
        latentVal = xPredict.mean

        yOut = mrdModel.predict(np.atleast_2d(latentVal), Yindex=1)
        latentVals[n,:] = latentVal
        predictVals[n,:] = yOut[0]
        sys.stdout.write('.')
        sys.stdout.flush()
    stopTime = time.time()
    print '\nFinished Strategy Optimize'

    nrmse = np.divide(np.sqrt(metrics.mean_squared_error(testData[mKey],predictVals,multioutput='raw_values')),
                      testData[mKey].max(axis=0) - testData[mKey].min(axis=0))
    rmse = np.sqrt(metrics.mean_squared_error(testData[mKey],predictVals,multioutput='raw_values'))
    corr = np.zeros((1,nDimOut))
    for d in range(nDimOut):
        corr[0,d],_ = stats.pearsonr(testData[mKey][:,d],predictVals[:,d])

    results = {}
    results['corr'] = corr
    results['rmse'] = rmse
    results['nrmse'] = nrmse
    results['pred'] = predictVals
    results['latent'] = latentVals
    results['time'] = nSamples/(stopTime - startTime)
    return results

def filterFunc(mrdModel, testData):
    qDim = mrdModel.X.mean.values.shape[1]

    scales1 = mrdModel.Y0.kern.input_sensitivity(summarize=False)
    scales2 = mrdModel.Y1.kern.input_sensitivity(summarize=False)

    scales1 = scales1/scales1.max()
    scales2 = scales2/scales2.max()
    
    # get the number of dimensions
    yThresh = 0.05
    indices = np.asarray(range(qDim))
    active1 = indices[scales1 >= yThresh]
    active2 = indices[scales2 >= yThresh]
    sharedDims = np.intersect1d(active2,active2)
    nShared = len(sharedDims)

    # get init latent state from optimization
    hybridFPS = 15.0
    deltaT = 1.0/30.0
    
    # state transition matrix
    def f_cv(x, dt):
        nShared = len(x)/2
        F = np.eye(2*nShared)
        F[:nShared,nShared:] = dt*np.eye(nShared)
        return np.dot(F, x)

    def h_cv(x):
        nShared = len(x)/2
        return x[:nShared]
        
    # create kalman filter
    sigmas = filterpy.kalman.MerweScaledSigmaPoints(n=2*nShared, alpha=0.1, beta=2.0, kappa=1.0)
    kf = UKF(dim_x=2*nShared, dim_z=nShared, fx=f_cv, hx=h_cv, dt=deltaT, points=sigmas)

    # init state
    yIn = testData['Cloud'][0,:]
    [xPredict, infX] = mrdModel.Y0.infer_newX(yIn[None,:], optimize=True)
    xPredict = xPredict.mean
    
    kf.x = np.zeros((2*nShared))
    kf.x[:nShared] = xPredict[0,sharedDims]

    # init covariance
    kf.P *= 1e-4
    
    # process and measurement noise
    kf.Q *= 1e-5
    kf.R *= 1e-3
    
    # model variables
    kKey = 'Cloud'
    mKey = 'TopCoord'

    qDim = mrdModel.X.mean.shape[1]
    nDimIn = testData[kKey].shape[1]
    nDimOut = testData[mKey].shape[1]
    nSamples = testData[mKey].shape[0]
    latentVals = np.zeros((nSamples,qDim))
    predictVals = np.zeros((nSamples,nDimOut))

    # obtain the training data latent positions
    latentPositions = mrdModel.X.mean
    nn = NearestNeighbors(n_neighbors=5,algorithm='kd_tree').fit(mrdModel.Y0.Y)

    startTime = time.time()
    for n in range(nSamples):
        yIn = testData[kKey][n,:]
        yTrueOut = testData[mKey][n,:]

        kf.predict()
        if n%hybridFPS == 0:
            [xPredict, infX] = mrdModel.Y0.infer_newX(yIn[None,:], optimize=True)
            xPredict = xPredict.mean
            kf.update(xPredict[0,sharedDims], R=1e-6*np.eye(nShared))
        else:
            _,indices = nn.kneighbors(np.atleast_2d(yIn))
            xPredict = latentPositions[indices[0],:].mean(axis=0)
            kf.update(xPredict[sharedDims])
        
        # how to apply hybrid here??
        # kalman filter
        latentVal = np.atleast_2d(xPredict)    
        latentVal[0,sharedDims] = kf.x[:nShared]
        
        yOut = mrdModel.predict(latentVal, Yindex=1)
        latentVals[n,:] = latentVal
        predictVals[n,:] = yOut[0]
        sys.stdout.write('.')
        sys.stdout.flush()
    stopTime = time.time()
    print '\nFinished Strategy Hybrid'

    nrmse = np.divide(np.sqrt(metrics.mean_squared_error(testData[mKey],predictVals,multioutput='raw_values')),
                      testData[mKey].max(axis=0) - testData[mKey].min(axis=0))
    rmse = np.sqrt(metrics.mean_squared_error(testData[mKey],predictVals,multioutput='raw_values'))
    corr = np.zeros((1,nDimOut))
    for d in range(nDimOut):
        corr[0,d],_ = stats.pearsonr(testData[mKey][:,d],predictVals[:,d])

    results = {}
    results['corr'] = corr
    results['rmse'] = rmse
    results['nrmse'] = nrmse
    results['pred'] = predictVals
    results['latent'] = latentVals
    results['time'] = nSamples/(stopTime - startTime)
    return results

nShr = 4
nPos = 6
names = []
dims = [1,7500,8]
keys = ['Time','Cloud','TopCoord']

for nS in range(nShr):
    for nP in range(nPos):
        names.append('K1S%dP%dT1' % (nS+1,nP+1))
        
Data = pickle.load(open('../Data/Data.p','rb'))

experiments = ['Pos', 'Shr']
functions = ['filter','nnsearch','optimize']        

for nS in range(nShr):
    for nP in range(nPos):
        print 'Cycle:%d,%d' % (nS+1,nP+1)        
        testInd = {'Pos':nS*nPos+nP, 'Shr':((nS+1)%nShr)*nPos+nP}
        
        # load mrd model and obtain plot indices
        mrdModel = pickle.load(open('../Models/Model%d%d.p' % (nS+1,nP+1), 'rb'))
        scales = 1./np.asarray(mrdModel.Y0.kern.lengthscale)
        indices = scales.argsort()[-2:][::-1]
            
        for exp in experiments:
            testData = {}
            for key,dim in zip(keys,dims):
                testData[key] = Data[names[testInd[exp]]][key]        
        
            results = {}
            results['filter'] = filterFunc(mrdModel, testData)
            results['nnsearch'] = nnsearchFunc(mrdModel, testData)
            results['optimize'] = optimizeFunc(mrdModel, testData)
            pickle.dump(results,open('Results/Res%s%d%d.p' % (exp,nS+1,nP+1), 'wb'))            
