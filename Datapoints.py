#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 28 16:13:26 2017

To have all the tools used for the Errorbars script in versitile, 
easily accessible form.

@author: scott
"""

from matplotlib import pyplot as plt
import numpy as np

#one could argue that the following two scripts should be in this module, but instead:
#   get_datapoints is in Integrate_Signals.py
#   plot_datapoints is in Plottying.py
   


def fill_with(quantitydict, value):
    '''
    generates a (multilayer) dictionary with the same keys as an input
    dictionary, but values replaced by value
    '''
    emptydict ={}
    for (key, val) in quantitydict.items():
#        print(str(key) + ' ' + str(value))
        if type(val) is dict:
            emptydict[key] = get_empty(val)
        else:
            if type(value) in [list, dict]:
                value = value.copy() # otherwise they get linked... 
            emptydict[key] = value
    return emptydict

def get_empty(quantitydict):
    '''
    generates a (multilayer) dictionary with the same keys as an input
    dictionary, but values replaced by empty lists
    '''
    return fill_with(quantitydict, value=[])
    
def add_datapoint(source, target, index=None, add_key=True):
    '''
    adds the values in a source dictionary to 
    '''
#    print(str(source))
    for key, value in source.items():

        if type(value) is dict:
            if key not in target.keys() and add_key:
                target[key] = {}
            add_datapoint(value, target[key], index, add_key=add_key)
            continue
        
        if index is None:
            v = value
        else:
            v = value[index]

        if key in target.keys():

            if type(target[key]) is np.ndarray:
                target[key] = np.append(target[key], v)
            elif hasattr(v, '__iter__'):
                target[key] += v
            else: 
                target[key] += [v]
#                print('adding ' + str(value[index]) + ' to ' + str(key))
        elif add_key:
            if hasattr(v, '__iter__'):
                target[key] = v.copy() #this .copy() is important
            else:
                target[key] = [v]

    
def datapoints_to_values(datapoints, X='all', X_str='V', rnd=2, avoid='blank', verbose=True):
    '''
    Reorganizes the datapoints dictionary, such that
    the value indicated by X_str is the outer organizational level. A list of 
    desired X_str to include in values can be input as X. Numerical values
    are considered equal if equal to rnd decimals.
    The original outermost organizational level (i.e., sample) is lost.
    '''
    if verbose:
        print('\n\nfunction \'datapoints_to_values\ at your service!\n')
    if type(avoid) is str:
        avoid = [avoid]
    empty = get_empty(list(datapoints.values())[0]) 
    if type(X) is list:
        values = dict([(x, get_empty(empty)) for x in X]) 
        #.copy here is not good enough to avoid linking!
    elif X == 'all':
        values = {}
    
    for (name, data) in datapoints.items():
        if len([a for a in avoid if a in name])>0:
            continue
        if verbose:
            print('adding ' + name + ' to values based on ' + X_str)
        for i, x in enumerate(data[X_str]):
            if rnd is not None:
                try:
                    x_round = float(np.round(x, rnd))
                except TypeError: #if it's not a numerical value, just move on.
                    x_round = x

            if x_round not in X:       
                if X == 'all':
                    values[x_round] = get_empty(empty)
                print(str(x_round) + ' not in potentials')
                continue

            add_datapoint(source=data, target=values[x_round], index=i)
    if verbose:
        print('\nfunction \'points_to_values\' finished!\n\n')
        
    return values

def datapoints_to_datalist(datapoints, avoid=[], verbose=True):
    '''Removes the outer layer of the datapoints dictionary, i.e.
    sample. The second organizational level (i.e., molecule) becomes the 
    outermost level. Lists and arrays are appended.
    In other words, it just lumps all samples together. 
    '''
    if verbose:
        print('\n\nfunction \'datapoints_to_datalists\' at your service!\n')
    if type(avoid) is str:
        avoid = [avoid]        
    datalists = {}
    for name, point in datapoints.items():
        if len([a for a in avoid if a in name])>0:
            print('skipping ' + name)
            continue
        if verbose:
            print('working on ' + name)
        add_datapoint(point, datalists, add_key=True) #should be just that simple
        
    if verbose:
        print('\nfunction \'datapoints_to_datalists\' finished!\n\n')  
    return datalists



def values_to_stats(values, logmean=False):
    '''
    replaces all numerical arrays or lists in the values of a (multilayer) 
    dictionary with the two-element list: [mean, standard_devation]
    '''
    #print('\nfunction values_to_stats in Datapoints.py has been called.')
    stats = {}
    for key, value in values.items():
        #print(key)
        if type(value) is dict:
            stats[key] = values_to_stats(value, logmean=logmean)
            #remember to feed arguments inwards in recursive functions!
        elif type(value) is list or type(value) is np.ndarray:
            if logmean:
                #print('logmean is True') 
                mean = np.exp(np.mean(np.log(value)))
                std = np.exp(np.log(mean) + np.std(np.log(value))) - mean
            else:
                mean = np.mean(value)
                #std = 0
                std = np.std(value)
            stats[key] = [mean, std]
    return stats

    
def get_mlu(stat, logmean=False): # mlu stands for for: mean, [lower, upper]
    if type(stat) is not list:
        return stat, None
    elif len(stat) == 2:
        mean = stat[0]
        std = stat[1]
        if logmean:
            log_mean = np.log(mean)
            log_std = np.log((std + mean)/mean)
            upper = np.exp(log_mean + log_std)
            lower = np.exp(log_mean - log_std)
#            print('logmean is True')
        else:
            upper = mean + std
            lower = mean - std
    elif len(stat) == 3:
        lower = stat[0]
        mean = stat[1]
        upper = stat[2]
    else:
        print('need stats of length 2 or 3 for errorbars')
        raise ValueError
    return mean, [lower, upper]


def plot_errorbar(xstat, ystat, ax=plt.gca(), logmean=False,
                  spec='.', color='k', markersize=None):
    if markersize is None:
        if spec == '.':
            markersize = 15
        else:
            markersize = 5
    x, x_lu = get_mlu(xstat, logmean)
    y, y_lu = get_mlu(ystat, logmean)   
    ax.plot(x, y, spec, markersize=markersize, color=color)
    if x_lu is not None:
        ax.plot([x_lu[0], x_lu[1]], [y, y], '|-', color=color)
    if y_lu is not None:
        ax.plot([x, x], [y_lu[0], y_lu[1]], '_-', color=color)    

        
def plot_errorbars_y(stats, x='outer', ax='new', label='', logmean=False,
                     colors='k', Xrange=None, verbose=True, outercall=True):
    if verbose and outercall:
        print('\n\nfunction \'plot_errorbars_y\' at your service!\n')    
    if ax == 'new':
        fig1 = plt.figure()
        ax = fig1.add_subplot(111)
#    print(type(stats))
    if type(stats) is not dict:
        if Xrange is None or Xrange[0] <= x <= Xrange[1]:
            plot_errorbar(x, stats, ax=ax, color=colors, logmean=logmean)
#        print('I should have just plotted something.')
        return ax
    
    if (x not in ['outer', 'inner'] and type(colors) is not dict):
        colors = fill_with(stats, colors)
    if (x not in ['outer', 'inner'] and type(Xrange) is not dict):
        colors = fill_with(stats, Xrange)

    for key, val in stats.items():
        if verbose:
            print('working on ' + label + str(key))
        if x=='outer':
            x_val = key
            color_val = colors
            Xrange_val = Xrange
        elif x=='inner':
            print('errorbars: x=\'inner\' not yet implemented.')
            pass
        else:
            x_val = x
            try:
                color_val = colors[key]
            except KeyError:
                if verbose:
                    print('skipping ' + key)
                continue
            Xrange_val = Xrange[key]
        plot_errorbars_y(val, x=x_val, ax=ax, colors=color_val, Xrange=Xrange_val, 
                         label=label+str(key) + '_', outercall=False, logmean=logmean)
    if verbose and outercall:
        print('\nfunction \'plot_errorbars_y\' finished!\n\n')        
    return ax  
    
def get_from_key(item, key, reduced_key=None, delimiter='.'):
    '''
    nice little tool to aid in flexibility when dealing with multilayer dicts.
    '''
    if type(item) is not dict:
        return item
    try:
        return item[key]
    except KeyError:
        if reduced_key is None:
            reduced_key = key.split(delimiter)[0]
        return item[reduced_key]
                
    
def plot_datalist_fit(datalist, colors, X_str='V', Xrange='all', keys=None,
                   txt=None, ax='new',  specs={}, results={}, 
                   X=None, logy=False, logx=False,
                   label='', verbose=True, outercall=True, ):
    '''
    Some parts of this function, particularly the writing and plotting bit,
    are just for tafel. Otherwise its as general as possible, to an extent
    that may be a bit ridiculous...
    '''
    
    
    if verbose and outercall:
        print('\n\nfunction \'plot_datalist_fit\' at your service!\n') 

    if type(datalist) is not dict:
        print('could\'t find data for ' + label)
        return
        
    if ax=='new':
        ax = plt.figure().add_subplot(111)
    if type(txt) is str:
        txt = open(txt, 'w')
    
    if keys is None:
        if type(Xrange) is dict:
            keys = Xrange.keys() #for multiple vspans for a given quantity, just put a '.' in in the key
        elif type(colors) is dict:
            keys = colors.keys()
        elif type(datalist) is dict:
            keys = datalist.keys()
    
    if X_str in datalist.keys():
        X = datalist[X_str]
    
    for key in keys:      
        if key == X_str:
            continue
        if verbose:    
            print('working on: ' + label + key)
        xspan = get_from_key(Xrange, key) #so I'm flexible in how deep I define vspan, color, and data.
        color = get_from_key(colors, key)
        data = get_from_key(datalist, key)   
#       print(xspan)

        if type(color) is dict or type(xspan) is dict or X is None:
            results[key] = {}
            plot_datalist_fit(data, colors=color, X_str=X_str, Xrange=xspan, 
                           txt=txt, ax=ax, specs=specs, X=X, logx=logx, logy=logy,
                           label=key + '_', results=results[key],
                           verbose=verbose, outercall=False)
            continue
        
        y = np.array(data)
        x = np.array(X)
        
        if xspan is not 'all':
            try:
                I_keep = [I for (I, x_I) in enumerate(x) if x_I>xspan[0] and x_I<xspan[1]]
                x = x[I_keep]
                y = y[I_keep]
            except:
                print(xspan)
                print(x)
                raise
                #print('couldn\'t cut x and y')
                #print('len(x) = ' + str(len(x)))
                #print('xspan = ' + str(xspan)))                
            
        if logy:
            y = np.log(y)
        if logx:
            x = np.log(x)    
        
        p1 = np.polyfit(x, y, deg=1)
        a = p1[0] #slope
        b = p1[1] #intercept
        if logy:
            ts = np.log(10) / a #tafel slope

        if txt is not None:
            txt.write('---\n' + label + key + ' on interval ' + str(xspan) + '\n')
            txt.write('ln(' + label + key + '/[nmol]) = ' + str(b) + ' + ' + str(a) + ' * (V vs RHE / [V])\n')
            if logy:
                txt.write('\ttafel slope = ' + str(ts*1e3) + ' mV/decade\n')
      
        if ax is not None:
              x_fit = np.array(xspan)
              y_fit = b + a * x_fit
              if logy:
                  y_fit = np.exp(y_fit)
              ax.plot(x_fit, y_fit, color=color, label=label + key, **specs)
        
        results[key] = p1
              
    if outercall and txt is not None:
        txt.close()

    if verbose and outercall:
        print('\nfunction \'plot_datalist_fit\' finished!\n\n')
    
    return results, ax 





