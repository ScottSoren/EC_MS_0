#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 10:07:44 2017

@author: scott
"""
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import colors
ColorConverter = colors.ColorConverter
plt.close('all')

colorlist = list(colors.cnames.items())


ourcolors_0 = {'M2':'b','M4':'m', 'M18':'y', 'M28':'0.5', 'M32':'k', 'M40':'c', 'M44':'brown', #H2, He, and air 
             'M15':'r', 'M26':'g', 'M27':'limegreen', 'M30':'olive', 'M31':'palegreen', 'M43':'greenyellow', #hydrocarbons
             'M34':'darkred', 'M36':'darkgreen', 'M16':'indigo', #O isotopes
             'M20':'slateblue', 'M19':'teal', 'M17':'chocolate', # O isotopes continued
             'M70':'purple', 'M3':'darkgoldenrod' #exotic stuff
             }  


ourcolors = {}

fig1 = plt.figure()
ax1 = fig1.add_subplot(111)



header = '{:8s},\t{:20s},\t{:21s},\t{:10s}\n'.format('mass','python name', 'rgb', 'hex') 

line_0 = '{:8s},\t{:20s},\t[{:5.3f}, {:5.3f}, {:5.3f}],\t{:10s}\n'

f = open('color_table.txt', 'w')

f.write(header)          
          
for (mass, color) in ourcolors_0.items():
    print(mass + ' : ' + color)
    m = int(mass[1:])
    ax1.barh(m, 1, align='center', color=color)
    rgb = ColorConverter.to_rgb(ColorConverter, color) #why do I have to do this?
    html = colors.rgb2hex(rgb)
    ourcolors[mass] = (color, rgb, html)
    rgb = [np.round(a,3) for a in rgb]
    f.write(line_0.format(mass, color, rgb[0], rgb[1], rgb[2], str(html)))
f.close()
plt.savefig('colors_for_cinfdata.png')

makeECMSfile = True
if makeECMSfile:
    import os
    cwd = os.getcwd()
    os.chdir('..')
    from Object_Files import structure_to_lines
    os.chdir(cwd)
    lines = structure_to_lines(ourcolors_0, preamble='standard colors')
    g = open('standard_colors.txt','w')
    g.writelines(lines)
    g.close()
    






